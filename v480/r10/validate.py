"""Bind native UI, baseline regression, IRQ and image checks to exact sources."""
from pathlib import Path
import sys,json,subprocess,hashlib
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def sources():
 files=list((ROOT/'src').iterdir())+list((ROOT/'lab').glob('*.py'))+[ROOT/'build.py',ROOT/'validate.py',ROOT/'package.py']
 files+=list((ROOT.parent/'lab').glob('*.py'))+[ROOT.parent/'patcher.py',ROOT.parent/'patches/v2.json',ROOT.parent/'metadata/build.json']
 return {str(p.relative_to(REPO)):sha(p.read_bytes()) for p in sorted(files)}
def main():
 before=sources();out=ROOT/'.lab';out.mkdir(exist_ok=True);digest=sha((ROOT/'.build/candidate.bin').read_bytes());suites={}
 jobs=[('image',['lab/check_image.py'],'IMAGE_INTEGRITY.json'),('persistence',['lab/test_persistence.py'],'RX_PERSISTENCE_RESULTS.json'),('ui',['lab/test_ui.py'],'R10_UI_RESULTS.json'),('receiver',['lab/test_receiver.py'],'RX_BADGE_RESULTS.json'),('baseline',['lab/run_legacy.py','test_candidate.py'],'legacy/analysis/functional_tests.json'),('interrupt',['lab/run_legacy.py','test_candidate_interrupts.py'],'legacy/analysis/interrupt_tests.json'),('receiver_interrupt',['lab/test_receiver_interrupts.py'],'receiver_irq/analysis/interrupt_tests.json')]
 for name,args,result in jobs:
  print('Running',name,flush=True)
  with (out/(name+'.log')).open('w') as f:r=subprocess.run([sys.executable,str(ROOT/args[0]),*args[1:]],cwd=REPO,stdout=f,stderr=subprocess.STDOUT)
  if r.returncode:print((out/(name+'.log')).read_text()[-6000:]);raise SystemExit(r.returncode)
  b=(out/result).read_bytes();data=json.loads(b);assert data['candidate_sha256']==digest and data['status'].startswith('PASS')
  n=data.get('total',data.get('injection_cases'));suites[name]=dict(result=result,result_sha256=sha(b),checks=n)
  print(name,n,'PASS',flush=True)
 assert before==sources(),'Sources changed during validation'
 assert digest==sha((ROOT/'.build/candidate.bin').read_bytes()),'Candidate changed during validation'
 report=dict(status='PASS_V480_R10B_NATIVE_REGRESSION',candidate_sha256=digest,source_sha256=before,suites=suites,functional_checks=sum(suites[k]['checks'] for k in ['ui','receiver','baseline','persistence']),interrupt_cases=suites['interrupt']['checks']+suites['receiver_interrupt']['checks'],integrity_checks=suites['image']['checks'],hardware_verified=False)
 (out/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['suites','source_sha256']},indent=2))
if __name__=='__main__':main()
