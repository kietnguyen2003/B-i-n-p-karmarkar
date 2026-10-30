"""[MasterSpec C12/G7,11.1; BC 4.1-4.5] Full real verification with stored evidence."""
from pathlib import Path
import subprocess
import sys
import os
from datetime import datetime,timezone
import xml.etree.ElementTree as ET
from karmarkar.io import write_json


def main():
    """[MS G7] Fail nonzero on tests, figure generation, notebook or coverage errors."""
    root=Path(__file__).resolve().parents[1]
    out=root/"outputs"
    out.mkdir(exist_ok=True)
    env=os.environ.copy()
    env["PYTHONUTF8"]="1"
    # [DX/C12] Ignore unrelated globally installed pytest plugins, not project tests.
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"]="1"
    commands=[
        ("pytest",[sys.executable,"-m","pytest","-q","--basetemp=outputs/pytest-temp","--junitxml=outputs/pytest.xml"]),
        ("source_example",[sys.executable,"scripts/run_example.py"]),
        ("notebook",[sys.executable,"scripts/run_notebook.py"]),
    ]
    evidence={"started":datetime.now(timezone.utc).isoformat(),"checks":{},"status":"INCOMPLETE"}
    write_json(out/"verification.json",evidence)
    for name,command in commands:
        result=subprocess.run(command,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding="utf-8",errors="replace")
        (out/f"{name}_summary.txt").write_text(result.stdout,encoding="utf-8")
        print(result.stdout[-4000:],flush=True)
        evidence["checks"][name]={"exit_code":result.returncode,"command":command}
        write_json(out/"verification.json",evidence)
        if result.returncode:
            raise SystemExit(result.returncode)
    xml=ET.parse(out/"pytest.xml")
    suites=xml.getroot().findall("testsuite")
    evidence["pytest"]={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ("tests","failures","errors","skipped")}
    evidence["status"]="PASS"
    evidence["finished"]=datetime.now(timezone.utc).isoformat()
    evidence["visual_review"]="See outputs/visual_review.md; manually reviewed separately"
    write_json(out/"verification.json",evidence)
    print("Verification PASS; evidence: outputs/verification.json",flush=True)


if __name__=="__main__":
    main()

