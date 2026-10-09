"""Run V480-only functional, interrupt and whole-image checks; no device I/O."""
from config import *
import subprocess
from datetime import datetime,timezone

def sources():
    files=list((PACKAGE/'lab').glob('*.py'))+list((PACKAGE/'src').glob('*'))+list((PACKAGE/'metadata').glob('*.json'))+list((PACKAGE/'patches').glob('*.json'))+[PACKAGE/'patcher.py']
    return {str(p.relative_to(PACKAGE)):sha(p.read_bytes()) for p in sorted(files)}

def main():
    before=sources();results={}
    for name,script,filename in [('functional','test_candidate.py','functional_tests.json'),('interrupt','test_candidate_interrupts.py','interrupt_tests.json'),('whole_image','audit_candidate.py','prebuild_audit.json')]:
        print('Running',name,flush=True)
        with (ROOT/'analysis'/(name+'.log')).open('w') as log:
            subprocess.run([sys.executable,str(PACKAGE/'lab'/script)],stdout=log,stderr=subprocess.STDOUT,check=True)
        data=json.loads((ROOT/'analysis'/filename).read_text())
        require(data.get('candidate_sha256',data.get('sha256'))==sha(IMAGE),'Wrong candidate')
        results[name]=dict(status=data['status'],count=data.get('total',data.get('injection_cases',data.get('whole_image_execution_checks'))),result=filename,result_sha256=sha((ROOT/'analysis'/filename).read_bytes()))
        print(name,results[name]['count'],'PASS',flush=True)
    require(before==sources(),'Sources changed during verification')
    report=dict(status='PASS_PUBLIC_V480_ONLY_LAB',candidate_sha256=sha(IMAGE),suites=results,
                source_sha256=before,timestamp=datetime.now(timezone.utc).isoformat(),hardware_tested_by_runner=False,
                scope='V480-only rerun; earlier dual-model totals are archived separately')
    (ROOT/'PUBLIC_LAB_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
if __name__=='__main__':main()
