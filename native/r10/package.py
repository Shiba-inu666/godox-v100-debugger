"""Write a new R10 experimental package only after hash-bound validation passes."""
from pathlib import Path
import argparse,json,sys
from validate import ROOT,REPO,sources,sha
sys.path.insert(0,str(ROOT.parent))
from patcher import original,transform,R7_SHA256,require
NAME='v1.03r10.bin'
def package(directory):
 spec=json.loads((ROOT/'.build/r10.json').read_text())
 data=(ROOT/'.build/candidate.bin').read_bytes()
 report=json.loads((ROOT/'.lab/VALIDATION.json').read_text())
 require(report['status']=='PASS_R10_NATIVE_REGRESSION' and report['candidate_sha256']==sha(data),'Candidate not validated')
 require(report['source_sha256']==sources(),'Source changed after validation')
 for suite in report['suites'].values():
  require(sha((ROOT/'.lab'/suite['result']).read_bytes())==suite['result_sha256'],'Validation report changed')
 raw=transform(data,spec,restore=True);original(raw)
 require(transform(raw,spec)==data,'Inverse mismatch')
 r7=transform(raw);require(sha(r7)==R7_SHA256,'R7 baseline mismatch')
 meta=json.loads((ROOT/'.build/ui.json').read_text())
 require(meta['candidate_sha256']==sha(data),'Build metadata mismatch')
 manifest=dict(model='V100F',firmware_version='1.03',revision='R10',output_filename=NAME,base_sha256=R7_SHA256,
  original_sha256=sha(raw),output_sha256=sha(data),size=len(data),changed_bytes_from_R7=sum(a!=b for a,b in zip(r7,data)),
  changed_bytes_from_original=sum(a!=b for a,b in zip(raw,data)),patches=spec['patches'],
  source_sha256=report['source_sha256'],functional_checks=report['functional_checks'],integrity_checks=report['integrity_checks'],hardware_verified=False,
  device_written=False,SU1_TTL_implemented=False,fire_bytes_match_R7=True,rotary_helpers_match_R7=True,rotary_entry_hooks_wrapped_for_editors=True)
 payloads={NAME:data,'SHA256SUMS.txt':(sha(data)+'  '+NAME+'\n').encode(),
  'PATCH_MANIFEST.json':(json.dumps(manifest,indent=2)+'\n').encode(),
  'VALIDATION.json':(json.dumps(report,indent=2)+'\n').encode()}
 ui_report=json.loads((ROOT/'.lab/R10_UI_RESULTS.json').read_text())
 changes=json.loads((ROOT/'.lab/R10_CHANGES_RESULTS.json').read_text())
 ui_report['preview_sha256'].update(changes['preview_sha256'])
 payloads['R10_CHANGES_RESULTS.json']=(ROOT/'.lab/R10_CHANGES_RESULTS.json').read_bytes()
 for name,digest in ui_report['preview_sha256'].items():
  content=(ROOT/'.lab'/name).read_bytes();require(sha(content)==digest,'Preview changed after validation');payloads[name]=content
 payloads['IMAGE_INTEGRITY.json']=(ROOT/'.lab/IMAGE_INTEGRITY.json').read_bytes()
 directory=Path(directory);directory.parent.mkdir(parents=True,exist_ok=True);directory.mkdir()
 for name,content in payloads.items():
  with (directory/name).open('xb') as f:f.write(content)
  require((directory/name).read_bytes()==content,'Readback mismatch')
 print(json.dumps(dict(path=str(directory/NAME),sha256=sha(data),checks=report['functional_checks']),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output_dir',type=Path);a=p.parse_args();package(a.output_dir)
