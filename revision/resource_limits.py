"""Sampled CPU cap and memory controls for our own process group only."""
import os
import shutil
import signal
import sys
import time
import psutil

GIB = 1024**3


def cpu_environment(threads=2):
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES='', HIP_VISIBLE_DEVICES='', ROCR_VISIBLE_DEVICES='',
               DEVICE='cpu', FORCE_CPU='1', REVISION_THREADS=str(threads),
               PYTORCH_ENABLE_MPS_FALLBACK='0', PYTHONUNBUFFERED='1',
               OMP_WAIT_POLICY='PASSIVE', KMP_BLOCKTIME='0')
    for name in ('OMP', 'MKL', 'OPENBLAS', 'VECLIB_MAXIMUM', 'NUMEXPR', 'BLIS', 'TORCH'):
        env[name+'_NUM_THREADS' if name != 'VECLIB_MAXIMUM' else name+'_THREADS'] = str(threads)
    return env


def low_priority(command, background=True):
    result = [shutil.which('nice') or '/usr/bin/nice', '-n', '15', *command]
    if sys.platform == 'darwin' and background:
        result = [shutil.which('taskpolicy') or '/usr/bin/taskpolicy', '-b', *result]
    return result


class ProcessGroup:
    def __init__(self, pid, created=None):
        self.pid = int(pid)
        self.created = psutil.Process(pid).create_time() if created is None else created
        self.known = {self.pid: self.created}

    def members(self):
        found = {}
        for pid, created in list(self.known.items()):
            try:
                p = psutil.Process(pid)
                if abs(p.create_time()-created) > .001 or os.getpgid(pid) != self.pid:
                    continue
                for child in [p, *p.children(recursive=True)]:
                    try:
                        if os.getpgid(child.pid) == self.pid and child.status() != psutil.STATUS_ZOMBIE:
                            found[child.pid] = child
                    except (psutil.Error, ProcessLookupError):
                        pass
            except (psutil.Error, ProcessLookupError):
                pass
        if len(found) > 256:
            raise RuntimeError('Too many worker descendants')
        self.known = {p.pid: p.create_time() for p in found.values()}
        return list(found.values())

    def send(self, sig):
        if not self.members():
            return False
        try:
            os.killpg(self.pid, sig)
            return True
        except ProcessLookupError:
            return False

    def terminate(self):
        self.send(signal.SIGCONT)
        self.send(signal.SIGTERM)
        deadline = time.monotonic()+1
        while self.members() and time.monotonic() < deadline:
            time.sleep(.05)
        self.send(signal.SIGKILL)


class Limiter:
    def __init__(self, group, cpu_cores=1.5, memory_gib=4):
        self.group, self.cap, self.memory = group, cpu_cores, memory_gib*GIB
        self.start = self.last = time.monotonic()
        self.credit, self.previous, self.total, self.stopped = cpu_cores*.2, {}, 0., False

    def sample(self, user_paused=False):
        now = time.monotonic()
        delta, rss, current = 0., 0, {}
        for p in self.group.members():
            try:
                key = (p.pid, p.create_time())
                t = p.cpu_times()
                current[key] = t.user+t.system
                delta += max(0., current[key]-self.previous.get(key, 0.))
                rss += p.memory_info().rss
            except psutil.Error:
                pass
        self.credit = min(self.cap*.2, self.credit+(now-self.last)*self.cap)-delta
        self.total += delta
        self.last, self.previous = now, current
        memory = psutil.virtual_memory()
        if rss > self.memory:
            raise MemoryError(f'Worker exceeded {self.memory/GIB:g} GiB RSS cap')
        reasons = []
        if user_paused:
            reasons.append('user')
        if memory.available < max(4*GIB, .15*memory.total):
            reasons.append('memory_pressure')
        if self.credit < 0:
            reasons.append('cpu_budget')
        if reasons and not self.stopped:
            self.stopped = self.group.send(signal.SIGSTOP)
        elif not reasons and self.stopped:
            self.group.send(signal.SIGCONT)
            self.stopped = False
        return dict(paused_for=reasons, rss_bytes=rss, cpu_seconds=self.total,
                    average_cpu_percent=100*self.total/max(.2, now-self.start),
                    cpu_cap_cores=self.cap, available_memory_bytes=memory.available)

    def release(self):
        self.group.send(signal.SIGCONT)
        self.stopped = False
