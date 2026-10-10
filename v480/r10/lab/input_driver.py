"""Synthetic GPIO/touch samples; original LVGL polling/gesture code executes."""
import struct
from unicorn.arm_const import UC_ARM_REG_PRIMASK
RAM=0x20000000

def clean(v):
 for off in [0x5a3,0x576,0x358,0x589,0x5f5,0x5f6,0x18,0x7ae,0x7b0,0x7b1]:v.wb(off,0)
 v.wb(0x31,v.rb(0x31)&~8);v.wb(0x3a,v.rb(0x3a)&~2)
 v.u.reg_write(UC_ARM_REG_PRIMASK,0)
 v.u.mem_write(0x40020810,struct.pack('<I',0x20))

def poll(v,off=0xa58):
 drv=struct.unpack('<I',v.u.mem_read(v.rw(off),4))[0]
 timer=struct.unpack('<I',v.u.mem_read(drv+20,4))[0]
 v.call(0x08038ac4,timer)

class Touch:
 def __init__(self,v):
  self.v=v;self.sample=(0,0,0);self.events=[]
  self.hook=v.stub(0x08051218,self.read)
  clean(v)
  self.send(0,0,0)
 def read(self,args):
  x,y,down=self.sample
  self.v.u.mem_write(args[1],struct.pack('<hhIIhBB',x,y,0,0,0,down,0))
  return 0
 def send(self,x,y,down,ms=20):
  self.sample=(x,y,down)
  self.v.call(0x080428dc,ms)
  poll(self.v,0xa54)
  self.v.call(0x08023ad4,0) # Native animation timer; process elapsed style transitions.
 def tap(self,x,y):
  self.send(x,y,1);self.send(x,y,0)
 def hold(self,x,y):
  self.send(x,y,1)
  for _ in range(40):self.send(x,y,1)
  self.send(x,y,0)
 def drag(self,x,y,dx,dy=0):
  self.send(x,y,1)
  for i in range(1,11):self.send(x+dx*i//10,y+dy*i//10,1)
  self.send(x+dx,y+dy,0)
 def close(self):self.v.u.hook_del(self.hook)

def detents(v,direction=0,batch=1,gui_first=False):
 for off in [0x16,0x17,0x13]:v.wb(off,0)
 v.ww(0x28,0)
 phases=[0,1,3,2,0] if direction==0 else [0,2,3,1,0]
 for _ in range(batch):
  for phase in phases:
   v.u.mem_write(0x40020410,struct.pack('<I',phase));v.call(0x0800b4f0)
 if gui_first:poll(v)
 v.call(0x0800b59c)
 if not gui_first:poll(v)

def consumer_stubs(v):
 return [v.stub(a) for a in [0x08008a9c,0x0801e424,0x08019f38]]
