"""Shared isolated ARM/LVGL mechanics; no device I/O."""
from pathlib import Path
import hashlib, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

RAM=0x20000000; SP=RAM+0xf0000; STOP=0x09000000
REGS=[UC_ARM_REG_R0+i for i in range(13)]
if not __debug__:raise RuntimeError('Assertions required; do not use -O')
class StockVM:
    def __init__(self):
        self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        self.u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        for address,size in [(0x08000000,0x200000),(RAM,0x100000),(0x10000000,0x10000),(STOP,0x1000),(0x40020000,0x10000)]:self.u.mem_map(address,size)

    def wb(self,off,val):self.u.mem_write(RAM+off,bytes([val&255]))
    def ww(self,off,val):self.u.mem_write(RAM+off,struct.pack('<I',val&0xffffffff))
    def rb(self,off):return self.u.mem_read(RAM+off,1)[0]
    def rw(self,off):return struct.unpack('<I',self.u.mem_read(RAM+off,4))[0]
    def seed(self):
        self.u.mem_write(RAM,bytes(0x20000))
        self.wb(0x33c,3);self.wb(0x59f,1);self.wb(0x398,1);self.wb(0x4c3,1)
        self.wb(0x496,1);self.wb(0x4c0,50);self.wb(0x4c1,0)
        self.u.mem_write(RAM+0x4d0,bytes([40,30,20,10,0,77]))
        self.u.mem_write(RAM+0x4c4,bytes([1]*5))
        self.u.mem_write(RAM+0x504,bytes([1]*5))
        self.ww(0x600,RAM+0x9000);self.ww(0x5d8,RAM+0x9100);self.ww(0x9e8,RAM+0xe000)
        self.ww(0x9e0,RAM+0xd000);self.ww(0x9dc,RAM+0xd100)
        for i in range(5):self.ww(0x15b8+4*i,RAM+0x10000+i*0x100)
        self.u.reg_write(UC_ARM_REG_PRIMASK,0)
    def args(self,n=8):
        first=[self.u.reg_read(r) for r in REGS[:4]]
        return (first+list(struct.unpack('<4I',self.u.mem_read(self.u.reg_read(UC_ARM_REG_SP),16))))[:n]
    def ret(self,val=0):
        self.u.reg_write(UC_ARM_REG_R0,val&0xffffffff);self.u.reg_write(UC_ARM_REG_PC,self.u.reg_read(UC_ARM_REG_LR))
    def stub(self,address,fn=None):
        def hook(u,a,s,d):self.ret(0 if fn is None else fn(self.args()))
        return self.u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
    def call(self,address,*args,count=50000):
        for i,r in enumerate(REGS):self.u.reg_write(r,0x11220000+i)
        for r,v in zip(REGS[:4],args):self.u.reg_write(r,v&0xffffffff)
        if len(args)>4:self.u.mem_write(SP,struct.pack('<'+'I'*len(args[4:]),*[a&0xffffffff for a in args[4:]]))
        self.u.reg_write(UC_ARM_REG_SP,SP);self.u.reg_write(UC_ARM_REG_LR,STOP|1);self.u.reg_write(UC_ARM_REG_XPSR,0x1000000)
        self.u.emu_start(address|1,STOP,count=count)
        assert self.u.reg_read(UC_ARM_REG_PC)==STOP,(hex(address),hex(self.u.reg_read(UC_ARM_REG_PC)))
        assert self.u.reg_read(UC_ARM_REG_SP)==SP
        for i in range(4,12):assert self.u.reg_read(REGS[i])==0x11220000+i,(hex(address),i)
        return self.u.reg_read(UC_ARM_REG_R0)
    def packets(self,entry=0x080184d4):
        frames=[];serial=[]
        def capture(u,a,s,d):frames.append(bytes(u.mem_read(RAM+0x36b,4)).hex())
        hook=self.u.hook_add(UC_HOOK_CODE,capture,begin=0x0801f948,end=0x0801f948)
        stubs=[self.stub(a) for a in [0x0802d07c,0x0802c14a,0x08025094]]
        stubs.append(self.stub(0x0802cff4,lambda a:serial.append(a[0]) or 0))
        try:self.call(entry)
        finally:
            for h in [hook,*stubs]:self.u.hook_del(h)
        return dict(frames=frames,serial=serial)
