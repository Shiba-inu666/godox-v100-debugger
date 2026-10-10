from pathlib import Path
import sys,json,struct
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parent/'lab'))
from native_vm import NativeVM
from config import sha
IMAGE=(ROOT/'.build/candidate.bin').read_bytes()
class VM(NativeVM):
 def __init__(self,image=IMAGE):
  super().__init__(image=image);self.manifest=json.loads((ROOT/'.build/ui.json').read_text())
 def child(self,obj,i):return self.call(0x0803b504,obj,i)
 def modal(self):return self.function('group_modal')
if __name__=='__main__':
 v=VM();v.wb(0x5a1,0);v.create(1);v.render();print('S',v.coords(v.rw(0x1554)),'M',v.coords(v.rw(0x15f4)),flush=True)
 v.event(v.rw(0x15b8));print('modal',hex(v.modal()),'state',v.rb(0x4c4),v.rb(0x4e5),flush=True);v.render()
 m=v.modal()
 for i in range(7):
  obj=v.child(m,i);print(i,hex(obj),v.coords(obj),v.text(obj) if i==0 else v.text(v.child(obj,0)),flush=True)
 for i in [5,6,4,3,4,3]:
  v.event(v.child(m,i));v.call(0x080426bc);v.render();print('clicked',i,'mode',v.rb(0x4c4),'enable',v.rb(0x504),'mask',v.rb(0x3da),'power',v.rb(0x4d0),'FEC',v.rb(0x4ef),'text',v.text(v.child(v.child(m,2),0)),flush=True)
 v.event(v.child(m,1));print('closed',v.modal(),'focus',hex(v.focus()),flush=True)
 v.render(str(ROOT/'.build/sender.png'))
 for page in [0,2]:
  v=VM();v.wb(0x12fa,0);v.create(page);v.render();print(page,v.text(v.rw(0x1554)),v.coords(v.rw(0x1554)),flush=True)
