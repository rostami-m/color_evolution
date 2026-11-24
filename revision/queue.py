"""Resumable sequential queue. Commands are argv arrays, never shell strings."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
import psutil
from .common import atomic_json, digest
from .resource_limits import ProcessGroup, Limiter, cpu_environment, low_priority


def now():
    return datetime.now(timezone.utc).isoformat()


def read_manifest(path):
    jobs = json.loads(Path(path).read_text())
    if not isinstance(jobs,list) or not jobs:
        raise ValueError('Manifest must be a nonempty list')
    ids = set()
    for j in jobs:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', j['id']) or j['id'] in ids:
            raise ValueError('Invalid/duplicate ID')
        ids.add(j['id'])
        if not isinstance(j['command'], list) or not j['command'] or not all(isinstance(x, str) for x in j['command']):
            raise ValueError('Command must be argv array')
    pending = {j['id']: set(j.get('depends_on', [])) for j in jobs}
    done = set()
    while pending:
        ready = [k for k, v in pending.items() if v <= done]
        if not ready:
            raise ValueError('Cyclic or unknown dependency')
        for k in ready:
            done.add(k)
            del pending[k]
    return jobs


class Queue:
    def __init__(self, args):
        self.a, self.root, self.stop = args, Path(args.output).resolve(), False
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root/'logs').mkdir(exist_ok=True)
        self.jobs = read_manifest(args.manifest)

    def save(self):
        self.state['updated_at'] = now()
        atomic_json(self.root/'status.json', self.state)

    def event(self, event, **kw):
        with (self.root/'events.jsonl').open('a') as f:
            f.write(json.dumps(dict(time=now(), event=event, **kw))+'\n')

    def stopping(self):
        return self.stop or (self.root/'stop.request').exists()

    def signal_stop(self, *_):
        self.stop = True

    def run_job(self, job):
        rec = self.state['jobs'][job['id']]
        rec.update(status='running', attempts=rec['attempts']+1, started_at=now(),
                   worker=None, reason=None)
        self.state['active_job'] = job['id']
        (self.root/'gpu_status.json').unlink(missing_ok=True)
        self.save()
        self.event('started', job_id=job['id'])
        process = group = limiter = None
        failure, stopped, last_save = None, False, 0.
        try:
            with (self.root/'logs'/f"{job['id']}.log").open('a') as log:
                process = subprocess.Popen(low_priority(job['command'], background=not getattr(self.a,'gpu',False)), cwd=self.a.workdir,
                    env={**cpu_environment(self.a.threads),'REVISION_PROGRESS_PATH':str(self.root/'gpu_status.json')}, stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                group = ProcessGroup(process.pid)
                rec['worker'] = dict(pid=process.pid, create_time=group.created)
                self.save()
                limiter = Limiter(group, self.a.cpu_cores, self.a.memory_gib)
                while process.poll() is None:
                    if self.stopping():
                        stopped = True
                        break
                    rec['resources'] = limiter.sample((self.root/'pause.request').exists())
                    self.state['queue_state'] = 'paused' if any(x != 'cpu_budget' for x in rec['resources']['paused_for']) else 'running'
                    if time.monotonic()-last_save > 5:
                        rec['worker']['known_members'] = group.known.copy()
                        self.save()
                        last_save = time.monotonic()
                    time.sleep(.1)
        except Exception as e:
            failure = f'{type(e).__name__}: {e}'
        finally:
            if limiter:
                limiter.release()
            if group:
                group.terminate()
            if process:
                process.wait(timeout=5)
        rc = process.returncode if process else None
        rec.update(status='pending' if stopped else 'failed' if failure or rc != 0 else 'completed',
                   reason=failure or (f'Exit {rc}' if rc else None), worker=None,
                   finished_at=now(), returncode=rc)
        self.state['active_job'] = None
        self.save()
        self.event('finished', job_id=job['id'], status=rec['status'], reason=rec['reason'])

    def run(self):
        with (self.root/'.lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            status = self.root/'status.json'
            if status.exists():
                self.state = json.loads(status.read_text())
                if self.state['manifest_sha256'] != digest(self.jobs):
                    raise ValueError('Manifest changed: use a new run directory')
                retried=set()
                for ident,rec in self.state['jobs'].items():
                    if rec['status'] == 'running':
                        w = rec.get('worker')
                        if w:
                            previous_group=ProcessGroup(w['pid'], w['create_time'])
                            previous_group.known.update({int(k):v for k,v in w.get('known_members',{}).items()})
                            previous_group.terminate()
                        rec.update(status='pending', worker=None)
                    elif self.a.retry_failed and rec['status'] == 'failed':
                        rec.update(status='pending', reason=None)
                        retried.add(ident)
                for job in self.jobs:
                    if job.get('allow_failed_dependencies') and set(job.get('depends_on',[])) & retried:
                        self.state['jobs'][job['id']].update(status='pending',reason='Refresh analysis after retry')
            else:
                self.state = dict(manifest_sha256=digest(self.jobs), created_at=now(),
                    jobs={j['id']: dict(status='pending', attempts=0, metadata=j.get('metadata', {})) for j in self.jobs})
            self.state.update(queue_state='running', active_job=None,
                limits=dict(cpu_cores=self.a.cpu_cores, threads=self.a.threads, worker_memory_gib=self.a.memory_gib, workers=1, training_backend='mps', mps_driver_memory_gib=4, analysis_backend='cpu'))
            (self.root/'stop.request').unlink(missing_ok=True)
            atomic_json(self.root/'pid.json', dict(pid=os.getpid(), create_time=psutil.Process().create_time()))
            for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                signal.signal(sig, self.signal_stop)
            self.save()
            try:
                while not self.stopping():
                    if (self.root/'pause.request').exists():
                        self.state['queue_state'] = 'paused'
                        self.save()
                        time.sleep(1)
                        continue
                    pending = [j for j in self.jobs if self.state['jobs'][j['id']]['status'] == 'pending']
                    if not pending:
                        break
                    progressed = False
                    for j in pending:
                        deps = [self.state['jobs'][d]['status'] for d in j.get('depends_on', [])]
                        if 'failed' in deps and not j.get('allow_failed_dependencies',False):
                            self.state['jobs'][j['id']].update(status='failed', reason='Required dependency failed')
                            progressed = True
                        elif all(d == 'completed' or (d=='failed' and j.get('allow_failed_dependencies',False)) for d in deps):
                            self.run_job(j)
                            progressed = True
                            break
                    if not progressed:
                        raise RuntimeError('No runnable job')
                failed = sum(r['status'] == 'failed' for r in self.state['jobs'].values())
                self.state['queue_state'] = 'stopped' if self.stopping() else 'completed_with_failures' if failed else 'completed'
                self.save()
                return 130 if self.stopping() else int(bool(failed))
            finally:
                (self.root/'pid.json').unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['run', 'status', 'pause', 'resume', 'stop'])
    p.add_argument('--output', required=True)
    p.add_argument('--manifest')
    p.add_argument('--workdir', default=os.getcwd())
    p.add_argument('--threads', type=int, default=2)
    p.add_argument('--cpu-cores', type=float, default=1.5)
    p.add_argument('--memory-gib', type=float, default=4.)
    p.add_argument('--retry-failed', action='store_true')
    p.add_argument('--gpu', action='store_true', help='Avoid macOS background Metal scheduling; backend still comes from each frozen config')
    a = p.parse_args()
    root = Path(a.output)
    if a.action == 'run':
        if not a.manifest or a.threads < 1 or a.cpu_cores <= 0 or a.memory_gib <= 0:
            p.error('Require manifest and positive resource limits')
        return Queue(a).run()
    if a.action == 'status':
        s = json.loads((root/'status.json').read_text())
        active = s.get('active_job')
        print(json.dumps(dict(state=s['queue_state'], updated_at=s['updated_at'],
             counts=dict(Counter(r['status'] for r in s['jobs'].values())),
             active_job=active, resources=s['jobs'].get(active, {}).get('resources'),
             limits=s.get('limits')), indent=2))
    elif a.action == 'resume':
        (root/'pause.request').unlink(missing_ok=True)
    else:
        (root/f'{a.action}.request').touch()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
