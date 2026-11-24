"""Bounded aggregate CPU-cap integration test, including child processes."""
import json
from pathlib import Path
import subprocess
import sys


def test_cpu_cap_counts_children(tmp_path):
    worker=tmp_path/'worker.py'
    result=tmp_path/'result.json'
    worker.write_text('''import concurrent.futures,json,subprocess,sys,time
from pathlib import Path
child="import time;start=time.monotonic();cpu=time.process_time();n=0\\nwhile time.monotonic()-start<6:n+=1\\nprint(time.process_time()-cpu)"
start=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(2) as pool:
    futures=[pool.submit(subprocess.check_output,[sys.executable,'-c',child],text=True) for _ in range(2)]
    cpu=sum(float(f.result()) for f in futures)
Path(sys.argv[1]).write_text(json.dumps(dict(cpu_seconds=cpu,wall_seconds=time.monotonic()-start)))
''')
    manifest=tmp_path/'manifest.json'
    manifest.write_text(json.dumps([dict(id='limiter',command=[sys.executable,str(worker),str(result)])]))
    process=subprocess.run([sys.executable,'-m','revision.queue','run','--manifest',str(manifest),
        '--output',str(tmp_path/'queue'),'--cpu-cores','.5','--threads','1'],timeout=25,capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    measurements=json.loads(result.read_text())
    assert measurements['cpu_seconds']>0
    assert measurements['wall_seconds']>=6
    assert measurements['cpu_seconds']/measurements['wall_seconds']<.8
