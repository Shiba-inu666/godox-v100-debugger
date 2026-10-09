"""Explicitly bounded Cortex-M machine-code harness; no hardware access."""
import ast,json,sys,struct
from pathlib import Path
from config import *
from unicorn import *
from unicorn.arm_const import *
from stock_vm import VM as StockVM,RAM,STOP,SP,REGS

Q={
 'V480F':dict(consumer=0x800b59c,gpio=0x40020410,shift=0,stubs=[0x8008a9c,0x801e424,0x8019f38,0x801323c],isr=0x801901c,rx_status=0x804e9f4,rx_data=0x804e990,tx=0x804e996,tx_status=0x804e99a,writer=0x801001c,index=0x441,consumer_enable=0x38)}

class VM(StockVM):
    def __init__(self,model,patched=True):
        super().__init__(model,False)
        self.m=META
        self.p.update(self.m['profile']);self.q=Q[model];self.patched=patched
        self.base=int(self.m['helper_base'],16)
        if patched:
            blob=HELPER
            if sha(blob)!=self.m['helper_sha256']:raise ValueError('Helper digest mismatch')
            self.u.mem_write(self.base,blob)
            for h in self.m['hooks']:
                a=int(h['address'],16)
                if bytes(self.u.mem_read(a,4)).hex()!=h['original']:raise ValueError('Hook bytes mismatch')
                self.u.mem_write(a,bytes.fromhex(h['replacement']))
        self.trace=[];self.memory_writes=[]
    def run_trace(self,addr,*args):
        self.trace=[];self.memory_writes=[]
        def code(u,a,size,data):
            self.trace.append((a,u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_SP)))
        def write(u,access,a,size,value,data):self.memory_writes.append((a,size,value,u.reg_read(UC_ARM_REG_PRIMASK),u.reg_read(UC_ARM_REG_PC)))
        h1=self.u.hook_add(UC_HOOK_CODE,code);h2=self.u.hook_add(UC_HOOK_MEM_WRITE,write)
        try:return self.call(addr,*args)
        finally:self.u.hook_del(h1);self.u.hook_del(h2)
    def phase(self,phase):
        self.u.mem_write(self.q['gpio'],struct.pack('<I',phase<<self.q['shift']))
        self.call(self.p['decoder'])
    def delta(self):return struct.unpack('<i',self.u.mem_read(RAM+0x28,4))[0]
    def stub_consumer(self):
        def stub(u,a,s,d):u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        return [self.u.hook_add(UC_HOOK_CODE,stub,begin=fn,end=fn) for fn in self.q['stubs']]

if __name__=='__main__':
    for model in Q:
        v=VM(model);v.seed();v.run_trace(v.p['positive'])
        print(model,v.rb(v.p['fec']),v.rb(v.p['selector']),v.u.reg_read(UC_ARM_REG_PRIMASK),len(v.trace))
        v.seed()
        for ph in [0,1,3,2,0]:v.phase(ph)
        print('decoder',v.rb(0x16),v.rb(0x17),v.delta())
