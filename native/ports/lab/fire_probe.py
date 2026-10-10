from pathlib import Path
import json,sys,struct
from port_vm import PortVM as FireProfile, M, BASE

import trace as st
from trace import VM as StockFireVM,RAM,REGS
from legacy_operations import PROFILES
from unicorn.arm_const import *
class FireVM(StockFireVM):
 def __init__(self,name,patched):
  self.port=FireProfile(name);self.image=(M/name/self.port.profile['output_filename']).read_bytes() if patched else self.port.data
  self.decoded={};self.gpio=[];self.frames=[]
  orig=PROFILES['V100F'];p={**orig}
  ramkeys=['role','mode','group_mode','power','fec','enabled','mask','ready','command','protocol_valid','alternate','event_kind','blocked','inhibit','send_test','test_context','clock','adc','energy','presence','sub_ready','radio_variant','radio_buffer','protocol_mode','ui_count','ui_rows','ui_keyboard','ui_touch','ui_selected','parsed_protocol','radio_channel','radio_config_aux']
  for k in ramkeys:
   try:p[k]=self.port.ram(orig[k])
   except ValueError:p.pop(k,None)
  codekeys=['trigger_irq','trigger','exposure','radio_only','ttl','manual','preflash','other','test','fixed_pulse','manual_test','prep','radio','encode','transfer','radio_full','radio_periodic','serial','variant_send','variant_end','ui','touch_ui','ui_event','ui_target','ui_source','ui_activity','ui_style','ui_update','ui_render','settings_save','button_scan','parser','spi_irq_status','spi_read','spi_write','spi_status']
  for k in codekeys:
   try:p[k]=self.port.flash(orig[k])
   except ValueError:p[k]=None
  for k in ['delays','transport','post','hss']:p[k]=[self.port.flash(a) for a in orig[k]]
  p['size']=len(self.image);PROFILES[name]=p;st.RAW[name]=self.image
  super().__init__(name);self.u.mem_write(BASE,self.image)
 def seed(self,state=2,mode=1,ready=1):
  p=self.p;self.u.mem_write(RAM,bytes(0x20000));self.u.mem_write(0x40000000,bytes(0x40000))
  for k,x in [('role',3),('mode',mode),('ready',ready),('command',10),('protocol_valid',1),('clock',1)]:self.wb(p[k],x)
  self.u.mem_write(RAM+p['group_mode'],bytes([state,1,0,2,1]));self.u.mem_write(RAM+p['power'],bytes([40,30,20,10,50,60]));self.u.mem_write(RAM+p['enabled'],bytes([int(state!=2),1,1,0,1]))
  self.wh(p['adc'],600);self.wh(p['energy'],300);self.wb(p['sub_ready'],1);self.wb(p['mask'],0x17)
  self.trace=[];self.serial=[];self.stores=[];self.executed=[];self.u.reg_write(UC_ARM_REG_PRIMASK,0)
 def wf(self,o,v):self.wb(self.port.ram(o),v)
 def rf(self,o):return self.rb(self.port.ram(o))
 def instruction(self,model,a):
  if a not in self.decoded:self.decoded[a]=next(st.MD.disasm(bytes(self.u.mem_read(a,4)),a,count=1))
  return self.decoded[a]
 def observe(self,u,a,s,d):
  st.instruction=self.instruction
  if a==self.port.flash(0x800fb94):self.gpio.append(self.args()[:3])
  super().observe(u,a,s,d)
 def setup(self,role,mode,power=30):
  self.seed(state=mode&3,mode=mode,ready=1)
  page={0:0,3:1,4:2}[role]
  for o,v in {0x33c:role,0x59f:page,0x398:page,0x503:1,0x33e:10,0x496:1,0x497:1,0x4c1:1,0x544:1,0x4c0:power,0x34:2,0x1a:4,0xe:2,0x3d6:1}.items():self.wf(o,v)
  if self.model=='V100C_V1.11':self.wf(0x4f8,1) # Native Canon local-trigger gate, distinct from group enable.
  self.u.mem_write(0x40020810,struct.pack('<I',0x20));self.u.mem_write(0x40020010,struct.pack('<I',0x2000));self.gpio=[]
 def runf(self,address):
  entry=self.port.flash(address);self.call(entry,count=1000000)
  assert all(self.u.reg_read(REGS[i])==0x11220000+i for i in range(4,12)),('callee saved',hex(entry))
  assert self.u.reg_read(UC_ARM_REG_PRIMASK)==0,('primask',hex(entry))
  r=self.result('TEST');r.update(sub=any(p==0x40020800 and m==0x2000 and on==1 for p,m,on in self.gpio),gpio=self.gpio)
  return r
