"""Run original input scan and TEST chain with virtual peripheral observations.
Inherited stubs: transport, delay, selected completion/HSS services; no wall time.
Decode the loaded candidate bytes, not a cache of the stock instruction stream.
"""
from config import *
import struct
import stock_trace as st
from stock_trace import VM,RAM,SP,STOP,REGS,UC_HOOK_CODE
from unicorn.arm_const import *
class FireVM(VM):
 def __init__(self,image=IMAGE):
  self.decoded={};self.gpio=[];self.frames=[];self.helper_steps=0;self.image=image
  super().__init__('V100F');self.u.mem_write(0x08008000,image)
 def instruction(self,model,a):
  if a not in self.decoded:self.decoded[a]=next(st.MD.disasm(bytes(self.u.mem_read(a,4)),a,count=1))
  return self.decoded[a]
 def observe(self,u,a,s,d):
  st.instruction=self.instruction
  if a==0x0800fb94:self.gpio.append(self.args()[:3])
  if a in [0x0800d7c6,0x080121fe]:
   sp=u.reg_read(UC_ARM_REG_SP);leaf,outer=(4,28) if a==0x0800d7c6 else (36,60)
   self.frames.append(dict(site=hex(a),sp=hex(sp),leaf_lr=hex(struct.unpack('<I',u.mem_read(sp+leaf,4))[0]),dispatch_lr=hex(struct.unpack('<I',u.mem_read(sp+outer,4))[0]),primask=u.reg_read(UC_ARM_REG_PRIMASK)))
  if 0x080be000<=a<0x080be200:self.helper_steps+=1
  super().observe(u,a,s,d)
 def setup(self,role=3,mode=1,power=30,**overrides):
  self.seed(state=mode&3,mode=mode,ready=1)
  page={0:0,3:1,4:2}.get(role,3)
  for o,v in {0x33c:role,0x59f:page,0x398:page,0x503:1,0x33e:10,0x496:1,0x497:1,0x4c1:1,0x544:1,0x4c0:power,0x34:2,0x1a:4,0xe:2,0x3d6:1,0x3d3:1}.items():self.wb(o,v)
  # TEST key low on GPIO A14; SET and other key released.
  self.u.mem_write(0x40020810,struct.pack('<I',0x20));self.u.mem_write(0x40020010,struct.pack('<I',0x2000))
  for o,v in overrides.items():self.wb(int(o,16),v)
  self.gpio=[];self.frames=[];self.helper_steps=0
 def run(self,entry=0x08010f98):
  self.call(entry)
  assert all(self.u.reg_read(REGS[i])==0x11220000+i for i in range(4,12)),('callee saved',hex(entry))
  assert self.u.reg_read(UC_ARM_REG_PRIMASK)==0,('PRIMASK',hex(entry))
  r=self.result('TEST');r.update(gpio=self.gpio[:],sub=any(p==0x40020800 and m==0x2000 and on==1 for p,m,on in self.gpio),frames=self.frames[:],helper_steps=self.helper_steps)
  return r
 def packet(self,data):
  self.radio_bytes=list(data)
  self.stub(0x08029ff0,lambda args:int(args[0]==0x200 and bool(self.radio_bytes)))
  def take(args):
   assert self.radio_bytes,'Unexpected FIFO read'
   return self.radio_bytes.pop(0)
  self.stub(0x0802cf80,take)
  result=self.run(0x0800da9c)
  assert not self.radio_bytes
  return result
 def clear_trace(self):
  self.gpio=[];self.frames=[];self.helper_steps=0;self.serial=[];self.stores=[];self.trace=[];self.executed=[]
def pulse_signature(r):
 return {k:r[k] for k in ['gpio','main_trigger_set_requests','local_main_energy','radio_serial_hex']}
