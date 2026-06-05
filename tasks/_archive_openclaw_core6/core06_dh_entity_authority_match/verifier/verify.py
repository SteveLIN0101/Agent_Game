"""Core-06 verify.py"""
import json, subprocess, sys
from pathlib import Path
WORKSPACE = Path("/workspace")
def run_pytest(p):
    r = subprocess.run(["python3","-m","pytest",str(p),"-v","--tb=short"],capture_output=True,text=True,cwd=str(WORKSPACE))
    return r.returncode==0, r.stdout+"\n"+r.stderr
def main():
    results = {"visible_tests_pass":False,"hidden_tests_pass":False,"required_outputs_exist":[],"missing_outputs":[],"report_complete":False,"changelog_updated":True,"no_hardcoded_values":True,"tests_unmodified":True,"details":{}}
    p,o=run_pytest("tests/");results["visible_tests_pass"]=p;results["details"]["visible_tests_output"]=o[-500:]
    if Path("/opt/verifier/hidden_tests").exists():
        p,o=run_pytest("/opt/verifier/hidden_tests/");results["hidden_tests_pass"]=p;results["details"]["hidden_tests_output"]=o[-500:]
    for f in ["output/normalized_entities.csv", "output/report.md"]:
        if (WORKSPACE/f).exists():results["required_outputs_exist"].append(f)
        else:results["missing_outputs"].append(f)
    pass
    print(json.dumps(results,indent=2))
    sys.exit(0 if results["visible_tests_pass"] and results["hidden_tests_pass"] else 1)
if __name__=="__main__":main()
