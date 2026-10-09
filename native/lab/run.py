"""Run the portable subset of the native R7 lab; no hardware I/O."""
from config import *
import subprocess
from datetime import datetime,timezone

JOBS=[('glyph','test_glyph.py','GLYPH_RESULTS.json'),
      ('drawer','test_drawer.py','DRAWER_RESULTS.json'),
      ('sender_row','test_sender_row.py','SENDER_ROW_RESULTS.json'),
      ('firing','test_firing.py','FIRING_RESULTS.json'),
      ('sender_off','test_sender_off.py','SENDER_OFF_RESULTS.json'),
      ('readiness','test_stock_readiness.py','STOCK_READINESS_RESULTS.json'),
      ('wrapper','test_wrapper.py','WRAPPER_RESULTS.json'),
      ('modal','test_modal.py','MODAL_RESULTS.json'),
      ('ttl_research','analyze_su1_ttl.py','TTL_FEASIBILITY_RESULTS.json')]

def sources():
    files=list((NATIVE/'lab').glob('*.py'))+list((NATIVE/'src').iterdir())+list((NATIVE/'patches').glob('*.json'))+[NATIVE/'patcher.py']
    return {str(p.relative_to(NATIVE)):sha(p.read_bytes()) for p in sorted(files)}

def main():
    before=sources();suites={}
    for label,script,result in JOBS:
        print('Running',label,flush=True)
        with (ROOT/'analysis'/(label+'.log')).open('w') as log:
            subprocess.run([sys.executable,str(NATIVE/'lab'/script)],stdout=log,stderr=subprocess.STDOUT,check=True)
        report=json.loads((ROOT/'analysis'/result).read_text())
        require(report['candidate_sha256']==sha(IMAGE),'Wrong candidate: '+label)
        suites[label]=dict(checks=report['total'],status=report['status'],result=result,
                           result_sha256=sha((ROOT/'analysis'/result).read_bytes()))
        print(label,report['total'],'PASS',flush=True)
    require(before==sources(),'Source changed during verification')
    report=dict(status='PASS_PORTABLE_R7_LAB_SUBSET',candidate_sha256=sha(IMAGE),
                functional_checks=sum(v['checks'] for k,v in suites.items() if k!='ttl_research'),
                ttl_research_observations=suites['ttl_research']['checks'],suites=suites,
                source_sha256=before,timestamp=datetime.now(timezone.utc).isoformat(),hardware_verified=False,
                scope='Portable subset. The historical 39851-check engineering run is separately archived.')
    (ROOT/'PUBLIC_LAB_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['source_sha256','suites']},indent=2))

if __name__=='__main__':main()
