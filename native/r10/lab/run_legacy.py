"""Run an unchanged R7 lab suite against the SHA-checked R10 complete image."""
from pathlib import Path
import sys,json,runpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parent/'lab'))
import config
spec=json.loads((ROOT/'.build/r10.json').read_text())
config.IMAGE=config.transform(config.RAW,spec)
config.require(config.IMAGE==(ROOT/'.build/candidate.bin').read_bytes(),'Candidate mismatch')
config.ROOT=ROOT/'.lab';(config.ROOT/'analysis').mkdir(parents=True,exist_ok=True)
def compose(raw):
 image=config.transform(raw,spec)
 return image,spec['patches'],None,dict(sha256=config.sha(image))
config.compose=compose
import revision_vm
class RevisionVM(revision_vm.NativeVM):
 def __init__(self,image=config.IMAGE):
  super().__init__(image=image)
  self.manifest=json.loads((ROOT/'.build/ui.json').read_text())
revision_vm.RevisionVM=RevisionVM
if __name__=='__main__':
 allowed={'test_drawer.py','test_sender_row.py','test_firing.py','test_sender_off.py','test_stock_readiness.py','test_wrapper.py','test_modal.py'}
 config.require(len(sys.argv)==2 and sys.argv[1] in allowed,'Select an existing regression suite')
 runpy.run_path(str(ROOT.parent/'lab'/sys.argv[1]),run_name='__main__')
