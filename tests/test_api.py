import os, subprocess, time, json
from urllib.request import urlopen

def test_api_module_health(tmp_path):
    env=os.environ.copy()
    env["SIEM_DATA_DIR"]=str(tmp_path)
    p=subprocess.Popen(["python","-m","src.api"],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(30):
            try:
                with urlopen("http://127.0.0.1:8080/health",timeout=1) as r:
                    assert json.load(r)["status"]=="ok"
                    return
            except Exception:
                time.sleep(0.1)
        raise AssertionError("API did not start")
    finally:
        p.terminate()
        p.wait(timeout=5)
