"""Executes original Thumb machine code plus an emulator-only routing prototype.
No peripheral/device access. Synthetic SRAM state, not full-system emulation.
"""
if not __debug__: raise SystemExit('Tests require assertions: run Python without -O')
from pathlib import Path
import struct,json,sys,hashlib,collections,time
from unicorn import *
from unicorn.arm_const import *
from capstone import *
from config import *
RAM=0x20000000;STOP=0x09000000;SP=0x200f0000
REGS=[UC_ARM_REG_R0+i for i in range(13)]
class VM:
 def __init__(self,model,patched):
  self.p=dict(META["profile"]);self.model=model;self.patched=patched
  self.b=RAW;verify_original(self.b)
  self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);self.u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  self.u.mem_map(0x8000000,0x200000);self.u.mem_write(0x8008000,self.b)
  self.u.mem_map(RAM,0x100000);self.u.mem_map(STOP,0x1000)
  self.u.mem_map(0x40020000,0x10000) # Simulated GPIO values only.
  if patched: raise ValueError('Use candidate_vm for v2')
  self.stub_calls=[]
  self.u.hook_add(UC_HOOK_CODE,self.hook,begin=self.p['add_state'],end=self.p['add_state'])
 def hook(self,u,addr,size,data):
  # Only GUI style invalidation is stubbed. Math, dispatch, group lookup,
  # state-test, callback key handling, and all prototype instructions execute.
  obj=u.reg_read(UC_ARM_REG_R0);mask=u.reg_read(UC_ARM_REG_R1)
  self.stub_calls.append({'function':hex(addr),'object':hex(obj),'mask':mask})
  old=struct.unpack('<H',u.mem_read(obj+0x20,2))[0];u.mem_write(obj+0x20,struct.pack('<H',old|mask));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def wb(self,off,v):self.u.mem_write(RAM+off,bytes([v&255]))
 def ww(self,off,v):self.u.mem_write(RAM+off,struct.pack('<I',v&0xffffffff))
 def rb(self,off):return self.u.mem_read(RAM+off,1)[0]
 def seed(self,mode=0,selector=0,value=0,step=0):
  self.u.mem_write(RAM,bytes(0x10000));self.stub_calls=[]
  self.wb(self.p['mode'],mode);self.wb(self.p['selector'],selector);self.wb(self.p['fec'],value);self.wb(self.p['power'],value);self.wb(self.p['step'],step)
  self.ww(self.p['root'],RAM+0xf100)
  self.ww(self.p['group'],RAM+0xe000);self.ww(0xe00c,RAM+0xe100);self.ww(0xe100,RAM+0xe200)
  self.u.mem_write(RAM+0xe220,struct.pack('<H',4)) # Already focus-key; no redraw stub needed.
  self.u.mem_write(self.p['key_gpio'],struct.pack('<I',self.p['key_bit']))
 def call(self,addr,*args):
  for i,r in enumerate(REGS):self.u.reg_write(r,0x11220000+i)
  for i,a in enumerate(args):self.u.reg_write(REGS[i],a)
  self.u.reg_write(UC_ARM_REG_SP,SP);self.u.reg_write(UC_ARM_REG_LR,STOP|1);self.u.reg_write(UC_ARM_REG_XPSR,0x01000000)
  self.u.emu_start(addr|1,STOP,count=5000)
  assert self.u.reg_read(UC_ARM_REG_PC)==STOP,(self.model,hex(addr),hex(self.u.reg_read(UC_ARM_REG_PC)))
  assert self.u.reg_read(UC_ARM_REG_SP)==SP
  for i in range(4,12):assert self.u.reg_read(REGS[i])==0x11220000+i,(hex(addr),'callee-saved',i)
  return self.u.reg_read(UC_ARM_REG_R0)
 def snap(self,ignore_selector=False):
  data=bytearray(self.u.mem_read(RAM,0x10000))
  if ignore_selector:data[self.p['selector']]=0
  return bytes(data)
