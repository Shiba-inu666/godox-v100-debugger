"""Package only the exact V480F image with current successful validation."""
from pathlib import Path
import sys,json,shutil
from validate import ROOT,REPO,sha,sources
NAME='v480f-v1.03r10b.bin'
def package(dest):
 image=(ROOT/'.build/candidate.bin').read_bytes();meta=json.loads((ROOT/'.build/ui.json').read_text());report=json.loads((ROOT/'.lab/VALIDATION.json').read_text())
 assert report['status']=='PASS_V480_R10B_NATIVE_REGRESSION'
 assert sha(image)==report['candidate_sha256']==meta['candidate_sha256'] and sources()==report['source_sha256']
 for suite in report['suites'].values():assert sha((ROOT/'.lab'/suite['result']).read_bytes())==suite['result_sha256']
 previews={}
 for result in ['R10_UI_RESULTS.json','RX_BADGE_RESULTS.json']:
  previews.update(json.loads((ROOT/'.lab'/result).read_text())['preview_sha256'])
 for name,digest in previews.items():assert sha((ROOT/'.lab'/name).read_bytes())==digest
 dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True);dest.mkdir()
 (dest/NAME).write_bytes(image);(dest/'PATCH_MANIFEST.json').write_text(json.dumps(meta,indent=2)+'\n')
 mappings={'VALIDATION.json':'VALIDATION.json','IMAGE_INTEGRITY.json':'IMAGE_INTEGRITY.json','R10_UI_RESULTS.json':'UI_RESULTS.json','RX_BADGE_RESULTS.json':'RX_BADGE_RESULTS.json','RX_PERSISTENCE_RESULTS.json':'RX_PERSISTENCE_RESULTS.json','legacy/analysis/functional_tests.json':'functional_tests.json','legacy/analysis/interrupt_tests.json':'interrupt_tests.json','receiver_irq/analysis/interrupt_tests.json':'receiver_interrupt_tests.json'}
 for source,name in mappings.items():shutil.copyfile(ROOT/'.lab'/source,dest/name)
 readme=(ROOT/'README.md').read_text().replace('evidence/','').replace('R10_UI_RESULTS.json','UI_RESULTS.json')
 (dest/'README.md').write_text(readme)
 for name in previews:shutil.copyfile(ROOT/'.lab'/name,dest/name)
 hashes={p.name:sha(p.read_bytes()) for p in sorted(dest.iterdir())}
 (dest/'SHA256SUMS.txt').write_text(''.join(digest+'  '+name+'\n' for name,digest in hashes.items()))
 assert (dest/NAME).read_bytes()==image
 for name,digest in hashes.items():assert sha((dest/name).read_bytes())==digest
 (dest/'DELIVERY_READBACK.json').write_text(json.dumps(dict(status='PASS',file=NAME,bytes=len(image),sha256=sha(image),file_sha256=hashes,device_written=False,hardware_verified=False),indent=2)+'\n')
 print(str(dest.resolve()));print(sha(image))
if __name__=='__main__':package(sys.argv[1])
