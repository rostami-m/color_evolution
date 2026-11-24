import json
from pathlib import Path
import subprocess
import sys
import time
import psutil


def test_pause_resume_stop_and_restart(tmp_path):
    queue=tmp_path/'queue';progress=tmp_path/'progress'
    code=f"import time;from pathlib import Path\np=Path({str(progress)!r});start=time.monotonic()\nwhile time.monotonic()-start<3:\n p.write_text(str(time.monotonic()));time.sleep(.05)"
    manifest=tmp_path/'manifest.json';manifest.write_text(json.dumps([dict(id='worker',command=[sys.executable,'-c',code])]))
    command=[sys.executable,'-m','revision.queue','run','--manifest',str(manifest),'--output',str(queue)]
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    try:
        deadline=time.monotonic()+10
        while not progress.exists() and time.monotonic()<deadline:time.sleep(.05)
        assert progress.exists()
        (queue/'pause.request').touch()
        time.sleep(.4)
        before=progress.read_text();time.sleep(.3)
        assert progress.read_text()==before
        record=json.loads((queue/'status.json').read_text())['jobs']['worker']['worker']
        assert psutil.Process(record['pid']).status()==psutil.STATUS_STOPPED
        (queue/'pause.request').unlink();time.sleep(.4)
        assert progress.read_text()!=before
        (queue/'stop.request').touch()
        stdout,stderr=process.communicate(timeout=10)
        assert process.returncode==130,stderr
        assert json.loads((queue/'status.json').read_text())['jobs']['worker']['status']=='pending'
        assert not psutil.pid_exists(record['pid'])
        restarted=subprocess.run(command,capture_output=True,text=True,timeout=15)
        assert restarted.returncode==0,restarted.stderr
        state=json.loads((queue/'status.json').read_text())
        assert state['jobs']['worker']['status']=='completed'
        assert state['jobs']['worker']['attempts']==2
    finally:
        if process.poll() is None:
            (queue/'stop.request').touch()
            process.wait(timeout=10)
