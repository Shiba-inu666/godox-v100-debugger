"""Run the R8 native UI suite and unchanged R7 regressions, binding all hashes."""
from pathlib import Path
import json,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def sha(data):return hashlib.sha256(data).hexdigest()
def sources():
 files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x.startswith('.') or x=='__pycache__' or x=='out' for x in p.relative_to(ROOT).parts) and p.suffix in ('.py','.c','.S','.ld')]
 files+=list((ROOT.parent/'lab').glob('*.py'))+[ROOT.parent/'patcher.py',ROOT.parent/'patches/r7.json']
 return {str(p.relative_to(REPO)):sha(p.read_bytes()) for p in sorted(files)}
JOBS=[('r8_ui','lab/test_r8.py','R8_UI_RESULTS.json'),
 ('drawer','test_drawer.py','analysis/DRAWER_RESULTS.json'),
 ('sender_row','test_sender_row.py','analysis/SENDER_ROW_RESULTS.json'),
 ('firing','test_firing.py','analysis/FIRING_RESULTS.json'),
 ('sender_off','test_sender_off.py','analysis/SENDER_OFF_RESULTS.json'),
 ('readiness','test_stock_readiness.py','analysis/STOCK_READINESS_RESULTS.json'),
 ('wrapper','test_wrapper.py','analysis/WRAPPER_RESULTS.json'),
 ('modal','test_modal.py','analysis/MODAL_RESULTS.json')]
def main():
 before=sources();image=(ROOT/'.build/candidate.bin').read_bytes();digest=sha(image)
 out=ROOT/'.lab';out.mkdir(exist_ok=True);suites={}
 for name,script,result in JOBS:
  print('Running',name,flush=True)
  command=[sys.executable,str(ROOT/script)] if name=='r8_ui' else [sys.executable,str(ROOT/'lab/run_legacy.py'),script]
  with (out/(name+'.log')).open('w') as f:
   r=subprocess.run(command,cwd=REPO,stdout=f,stderr=subprocess.STDOUT)
  if r.returncode:
   print((out/(name+'.log')).read_text()[-6000:],flush=True);raise SystemExit(r.returncode)
  report=json.loads((out/result).read_text());assert report['candidate_sha256']==digest
  suites[name]=dict(checks=report['total'],result=result,result_sha256=sha((out/result).read_bytes()))
  print(name,report['total'],'PASS',flush=True)
 assert before==sources(),'Sources changed during verification'
 assert digest==sha((ROOT/'.build/candidate.bin').read_bytes()),'Candidate changed during verification'
 report=dict(status='PASS_R8_NATIVE_REGRESSION',candidate_sha256=digest,source_sha256=before,suites=suites,
             functional_checks=sum(x['checks'] for x in suites.values()),hardware_verified=False)
 (out/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('source_sha256','suites')},indent=2))
if __name__=='__main__':main()
