from pathlib import Path
import json,sys,struct
from port_vm import PortVM as Profile, M
from unicorn.arm_const import UC_ARM_REG_PRIMASK
class UI(Profile):
 def __init__(self,name):
  super().__init__(name);self.out=M/name;self.syms=json.loads((self.out/'symbols.json').read_text());self.u.mem_write(0x08008000,(self.out/self.profile['output_filename']).read_bytes());self.checks=[]
 def function(self,name,*args):return self.call(self.syms[name],*args,count=10000000)
 def rw(self,o):return self.getf(o)
 def ww(self,o,x):self.u.mem_write(0x20000000+self.ram(o),struct.pack('<I',x))
 def stubf(self,a,fn=None):return self.stub(self.flash(a),fn)
 def coords(self,obj):return struct.unpack('<4h',self.u.mem_read(obj+0x14,8))
 def rb(self,o):return self.u.mem_read(0x20000000+self.ram(o),1)[0]
 def wb(self,o,x):self.setf(o,x)
 def child(self,obj,i):return self.callf(0x0803b504,obj,i)
 def event(self,obj,code=4):return self.callf(0x08035fc8,obj,code,self.getf(0x9dc))
 def modal(self):return self.function('group_modal')
 def text(self,obj):
  a=int.from_bytes(self.u.mem_read(obj+0x24,4),'little');return bytes(self.u.mem_read(a,80)).split(b'\0')[0].decode()
 def state(self):return [bytes(self.u.mem_read(0x20000000+self.ram(a),n)) for a,n in [(0x4c0,2),(0x4c4,5),(0x4d0,6),(0x4ef,5),(0x504,5),(0x3da,1)]]
 def check(self,ok,name,details=None):
  assert ok,(self.name,name,details)
  self.checks.append(name)
 def open(self,g):
  for code in [1,8,4]:self.event(self.getf(0x15b8+4*g),code)
  self.check(bool(self.modal()),'group opens',g)
 def press(self,i):self.event(self.child(self.modal(),i));self.function('group_refresh')
 def close(self):self.press(1);self.check(not self.modal(),'group closes')
 def clean(self):
  for a in [0x54b,0x51e,0x342,0x531,0x599,0x59a,0x18,0x748,0x74a,0x74b]:self.wb(a,0)
  self.wb(0x31,self.rb(0x31)&~8);self.wb(0x36,self.rb(0x36)&~2);self.u.reg_write(UC_ARM_REG_PRIMASK,0)

def test(name):
 v=UI(name);v.wb(0x5a1,0);v.wb(0x12fa,0);v.create(1);v.clean();v.callf(0x080426bc)
 for g in range(5):
  old=v.state();v.open(g);m=v.modal()
  v.check(v.state()==old,'tap state isolation')
  label=v.child(v.child(m,0),0) if g or name=='V100C_V1.11' else v.child(m,0)
  v.check(v.text(label)==('ABCDE' if name=='V100C_V1.11' else 'MABCD')[g],'native group name')
  v.check(v.function('editor_target')==17 and v.rb(0x4b4)==g,'encoder bound to group')
  for mode in [0,1]:
   v.wb(0x4c4+g,mode);v.wb(0x504+g,1);v.wb(0x4d0+g,30);v.wb(0x4ef+g,0);v.function('group_refresh')
   old=v.state();v.callf(0x08010924);after=v.state()
   expected_field=2 if mode else 3
   v.check(after[expected_field][g]!=old[expected_field][g],'encoder changes value',(g,mode,old,after))
   for i,(a,b) in enumerate(zip(old,after)):
    for k,(x,y) in enumerate(zip(a,b)):v.check(x==y or (i==expected_field and k==g),'encoder other parameters unchanged',(g,mode,i,k))
   v.press(4);v.check(v.rb(0x4c4+g)==2 and v.rb(0x504+g)==0,'pause')
   old=v.state();v.callf(0x08010924);v.callf(0x0800ba84);v.press(5);v.press(6);v.check(v.state()==old,'paused encoder and plus minus blocked')
   v.press(3);v.check(v.rb(0x4c4+g)==2,'mode preselection stays paused');v.press(4)
   v.check(v.rb(0x4c4+g)==1-mode and v.rb(0x504+g)==1,'resume desired mode')
  v.close()
 v.open(1);v.render(v.out/'group-A.png');v.close();v.render(v.out/'sender.png')
 result={'model':name,'status':'PASS_UI_AND_ROTARY','checks':len(v.checks),'hardware_verified':False,'candidate_sha256':__import__('hashlib').sha256((v.out/v.profile['output_filename']).read_bytes()).hexdigest()};(v.out/'partial-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
if __name__=='__main__':test(sys.argv[1])
