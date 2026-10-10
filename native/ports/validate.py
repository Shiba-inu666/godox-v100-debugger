"""Run the model-specific offline suites and save source-bound evidence."""
from pathlib import Path
import argparse,json,os,subprocess,sys
from build import ROOT,build,load,sha
SUITES={'visual':('check_visual','visual-results.json'),'rx_endpoints':('check_rx_endpoints','rx-endpoint-results.json'),'ui':('check_ui','partial-results.json'),'touch':('check_touch','partial-touch-results.json'),'firing':('check_fire','partial-fire-results.json'),'radio':('check_radio','partial-radio-results.json'),'lifecycle':('check_lifecycle','lifecycle-results.json'),'values':('check_values','value-results.json'),'excluded':('check_excluded','excluded-results.json'),'integrity':('check_integrity','integrity-results.json')}
def sources(name):
 paths=[ROOT/'build.py',ROOT/'validate.py',ROOT/'package.py',ROOT/'profiles'/(name+'.json'),*(ROOT/'src'/name).iterdir(),*(ROOT/'lab').glob('*.py')]
 return {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in sorted(paths)}
def collect(name,expected_sources=None):
 out=ROOT/'.lab'/name;p=load(name);image=(out/p['output_filename']).read_bytes();bound=sources(name)
 if expected_sources is not None and bound!=expected_sources:raise RuntimeError('Source changed during validation')
 suites={};total=0
 for key,(script,result) in SUITES.items():
  file=out/result;r=json.loads(file.read_text())
  if not r['status'].startswith('PASS') or r['model']!=name or r['candidate_sha256']!=sha(image) or r['hardware_verified']:raise RuntimeError('Invalid/stale suite '+key)
  suites[key]=dict(script='lab/'+script+'.py',checks=r['checks'],result=result,result_sha256=sha(file.read_bytes()));total+=r['checks']
 report=dict(status='PASS_OFFLINE_EXPERIMENTAL',model=p['model'],firmware_version=p['firmware_version'],candidate_sha256=sha(image),original_sha256=p['original_sha256'],total_checks=total,functional_checks=total-suites['integrity']['checks'],image_checks=suites['integrity']['checks'],hardware_verified=False,device_written=False,physical_output_measured=False,release_channel='prerelease',source_sha256=bound,suites=suites,limitations=['No C/N/S/O hardware was available.','Virtual GPIO, LCD and RF transport; no measured light output or camera timing.','HSS/Multi dispatch parity is bounded; no SUB TTL/HSS/Multi extension.','No sustained shooting, thermal, bootloader flashing or recovery acceptance.'])
 (out/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('model');a.add_argument('original');x=a.parse_args();original=Path(x.original).resolve();env={**os.environ,'V100_PORT_ORIGINAL':str(original)}
 build(x.model,original,ROOT/'.lab'/x.model);bound=sources(x.model)
 for key,(script,result) in SUITES.items():
  (ROOT/'.lab'/x.model/result).unlink(missing_ok=True)
  subprocess.run([sys.executable,str(ROOT/'lab'/(script+'.py')),x.model],env=env,check=True)
 print(json.dumps(collect(x.model,bound),indent=2))
