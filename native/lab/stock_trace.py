"""Stock code only. Virtual hardware, no patch or device access.

Observe stores at CODE boundaries, never with Unicorn MEM_WRITE hooks.
SysTick COUNTFLAG is synthesized before its reads. No real timing claim.
"""
import hashlib,struct,json
from functools import lru_cache
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_MEM
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from profiles import *
RAM=0x20000000; SP=RAM+0xf0000; STOP=0x09000000
REGS=[UC_ARM_REG_R0+i for i in range(13)]
REG_NAMES={**{f'r{i}':r for i,r in enumerate(REGS)},'sp':UC_ARM_REG_SP,'lr':UC_ARM_REG_LR,'pc':UC_ARM_REG_PC,
           'sb':UC_ARM_REG_R9,'sl':UC_ARM_REG_R10,'fp':UC_ARM_REG_R11,'ip':UC_ARM_REG_R12}
MD=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_LITTLE_ENDIAN);MD.detail=True
from config import RAW as FIRMWARE_RAW
RAW={'V100F':FIRMWARE_RAW}
for m,p in PROFILES.items():
    assert len(RAW[m])==p['size'] and hashlib.sha256(RAW[m]).hexdigest()==p['sha']
@lru_cache(None)
def instruction(m,a):return next(MD.disasm(RAW[m][a-0x08008000:a-0x08008000+4],a,count=1))

class VM:
 def __init__(self,model):
    self.model=model;self.p=PROFILES[model];self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    self.u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    for a,n in [(0x08000000,0x200000),(RAM,0x100000),(STOP,0x1000),(0x40000000,0x40000),(0xe000e000,0x2000)]:self.u.mem_map(a,n)
    self.u.mem_write(0x08008000,RAW[model]);self.callbacks={};self.trace=[];self.serial=[];self.stores=[];self.executed=[]
    self.inject=None;self.injected=False;self.energy_reads=[]
    for a in self.p['delays']+self.p['transport']+self.p['post']+self.p['hss']:self.stub(a)
    self.stub(self.p['serial'],lambda args:self.serial.append(args[0]&255) or 0)
    # Alternate radio routines drive a different transport; record reaching it,
    # but do not pretend this measures that transport or its timing.
    self.stub(self.p['variant_send']);self.stub(self.p['variant_end'])
    self.u.hook_add(UC_HOOK_CODE,self.observe)
 def wb(self,o,v):self.u.mem_write(RAM+o,bytes([v&255]))
 def wh(self,o,v):self.u.mem_write(RAM+o,struct.pack('<H',v&65535))
 def ww(self,o,v):self.u.mem_write(RAM+o,struct.pack('<I',v&0xffffffff))
 def rb(self,o):return self.u.mem_read(RAM+o,1)[0]
 def rh(self,o):return struct.unpack('<H',self.u.mem_read(RAM+o,2))[0]
 def rw(self,o):return struct.unpack('<I',self.u.mem_read(RAM+o,4))[0]
 def args(self):return [self.u.reg_read(r) for r in REGS[:4]]
 def stub(self,a,fn=None):self.callbacks[a]=fn or (lambda args:0)
 def seed(self,state=2,mode=1,enabled=None,command=10,protocol=1,event=0,alternate=0,ready=1,physical_test=0):
    p=self.p;self.u.mem_write(RAM,bytes(0x20000));self.u.mem_write(0x40000000,bytes(0x40000))
    for k,v in [('role',3),('mode',mode),('ready',ready),('command',command),('protocol_valid',protocol),('event_kind',event),('alternate',alternate),('clock',1)]:self.wb(p[k],v)
    self.u.mem_write(RAM+p['group_mode'],bytes([state,1,0,2,1]));self.u.mem_write(RAM+p['power'],bytes([40,30,20,10,50,60]))
    self.u.mem_write(RAM+p['enabled'],bytes([int(state!=2) if enabled is None else enabled,1,1,0,1]))
    self.wh(p['adc'],600);self.wb(p['sub_ready'],1);self.wb(p['presence'],0);self.wb(p['mask'],0x17)
    if 'physical_test_flag' in p:self.wb(p['physical_test_flag'],physical_test)
    self.ww(p['ui_keyboard'],RAM+0xd000);self.ww(p['ui_touch'],RAM+0xd100)
    for i in range(5):self.ww(p['ui_rows']+i*4,RAM+0x10000+i*0x100)
    self.trace=[];self.serial=[];self.stores=[];self.executed=[];self.energy_reads=[];self.inject=None;self.injected=False
    self.u.reg_write(UC_ARM_REG_PRIMASK,0)
 def observe(self,u,a,s,d):
    self.executed.append(a)
    if self.inject and self.inject(self,a):self.injected=True;self.inject=None
    p=self.p
    names=[k for k in ['trigger','exposure','radio_only','ttl','manual','preflash','other','test','fixed_pulse','manual_test','prep','radio','encode','transfer','variant_send','variant_end'] if p[k]==a]
    for name in names:self.trace.append(dict(name=name,pc=hex(a),args=self.args(),mode=self.rb(p['group_mode']),enabled=self.rb(p['enabled']),primask=u.reg_read(UC_ARM_REG_PRIMASK)))
    if a in self.callbacks:
      ret=self.callbacks[a](self.args());u.reg_write(UC_ARM_REG_R0,(ret or 0)&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
    if not 0x08008000<=a<0x08008000+len(RAW[self.model]):return
    ins=instruction(self.model,a)
    if ins.mnemonic.startswith(('ldr','str')) and ins.operands[-1].type==ARM_OP_MEM:
      op=ins.operands[-1].mem
      if op.base:
        base=u.reg_read(REG_NAMES[ins.reg_name(op.base)])
        if ins.reg_name(op.base)=='pc':base=(a+4)&~3
        addr=base+op.disp
        if op.index:addr+=u.reg_read(REG_NAMES[ins.reg_name(op.index)])<<ins.operands[-1].shift.value
        addr&=0xffffffff
        if ins.mnemonic.startswith('ldr') and addr==0xe000e010:u.mem_write(addr,struct.pack('<I',0x10005))
        if ins.mnemonic.startswith('str'):
          value=u.reg_read(REG_NAMES[ins.reg_name(ins.operands[0].reg)])
          if addr>=0x40000000:self.stores.append(dict(pc=hex(a),address=hex(addr),value=value,insn=ins.mnemonic+' '+ins.op_str))
 def call(self,address,*args,count=250000):
    for i,r in enumerate(REGS):self.u.reg_write(r,0x11220000+i)
    for r,v in zip(REGS[:4],args):self.u.reg_write(r,v)
    self.u.reg_write(UC_ARM_REG_SP,SP);self.u.reg_write(UC_ARM_REG_LR,STOP|1);self.u.reg_write(UC_ARM_REG_XPSR,0x1000000)
    self.u.emu_start(address|1,STOP,count=count)
    assert self.u.reg_read(UC_ARM_REG_PC)==STOP,(self.model,hex(address),hex(self.u.reg_read(UC_ARM_REG_PC)))
    assert self.u.reg_read(UC_ARM_REG_SP)==SP
    return self.u.reg_read(UC_ARM_REG_R0)
 def result(self,event_label):
    p=self.p;pulses=[s for s in self.stores if int(s['address'],16)==p['main_set'] and s['value']&p['main_mask']]
    pre=bool(pulses) and event_label=='preflash'
    return dict(model=self.model,event=event_label,M_state=self.rb(p['group_mode']),M_enable=self.rb(p['enabled']),
      local_main_fire_count=int(bool(pulses) and not pre),local_preflash_count=int(pre),main_trigger_set_requests=len(pulses),
      local_main_energy=dict(physical_joules=None,prepared_duration_code=self.rh(p['energy']),timer_reload_requests=[s['value'] for s in self.stores if s['address']=='0xe000e014']),
      radio_tx_count=sum(x['name'] in ['radio','encode','variant_send'] for x in self.trace),
      remote_fire_command_count=sum(x['name']=='radio' and x['args'][0] in [9,0x19] for x in self.trace),
      radio_serial_hex=bytes(self.serial).hex(),trace=self.trace,main_trigger_stores=pulses,
      physical_output_measured=False)
