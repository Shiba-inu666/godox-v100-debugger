"""Run frozen v2 scope/IRQ tests after loading the full new candidate image."""
from pathlib import Path
import sys,runpy,json,hashlib
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'lab'
sys.path.insert(0,str(OLD))
import config
image=(ROOT/'.build/candidate.bin').read_bytes()
config.IMAGE=image;config.ROOT=ROOT/'.lab/legacy';(config.ROOT/'analysis').mkdir(parents=True,exist_ok=True)
import candidate_vm
OriginalVM=candidate_vm.VM
class WholeVM(OriginalVM):
 def __init__(self,model,patched=True):
  super().__init__(model,patched)
  if patched:self.u.mem_write(0x08008000,image)
candidate_vm.VM=WholeVM
script=sys.argv[1];assert script in ['test_candidate.py','test_candidate_interrupts.py']
runpy.run_path(str(OLD/script),run_name='__main__')
