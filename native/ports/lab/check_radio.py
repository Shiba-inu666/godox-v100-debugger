from port_vm import M
from fire_probe import FireVM,RAM
from pathlib import Path
import sys,hashlib,json
from itertools import product
name=sys.argv[1];s=FireVM(name,False);v=FireVM(name,True);count=0

def packet(vm,data):
 queue=list(data)
 vm.stub(vm.port.flash(0x8029ff0),lambda args:int(args[0]==0x200 and bool(queue)))
 def take(args):
  assert queue
  return queue.pop(0)
 vm.stub(vm.port.flash(0x802cf80),take)
 result=vm.runf(0x800da9c);assert not queue;return result
for g,mode,power,subpower,command in product([0,2,4] if name.startswith('V100C') else [1,3,5],[0,1],[0,30,80],[0,30,70],['broadcast','addressed']):
 out=[];states=[]
 for vm in [s,v]:
  vm.setup(4,mode,subpower);vm.wf(0x503,g);vm.wf(0x33e,g+(10 if name.startswith('V100C') else 9));vm.wf(0x54c,5)
  packet(vm,[0xa9,g+(10 if name.startswith('V100C') else 9),0xbc,power]);packet(vm,[0xa9,g+(10 if name.startswith('V100C') else 9),0xb9,80])
  states.append(bytes(vm.u.mem_read(RAM+vm.port.ram(0x4d0),6)))
  vm.gpio=[];vm.stores=[];vm.serial=[];vm.trace=[];vm.executed=[]
  out.append(packet(vm,[0xd5,0x19,0,0] if command=='broadcast' else [0xa9,g+(10 if name.startswith('V100C') else 9),0xb4,9]))
 a,b=out;detail=(g,mode,power,subpower,command,a['main_trigger_set_requests'],b['main_trigger_set_requests'],a['sub'],b['sub'])
 assert states[0]==states[1],detail
 assert v.rf(0x4c0)==s.rf(0x4c0)==subpower,detail
 assert b['sub'] and b['main_trigger_set_requests']==a['main_trigger_set_requests']==1,detail
 assert a['local_main_energy']['prepared_duration_code']==b['local_main_energy']['prepared_duration_code'],detail
 assert a['radio_serial_hex']==b['radio_serial_hex'],detail
 count+=5
r=dict(status='PASS_RF',model=name,checks=count,hardware_verified=False,candidate_sha256=hashlib.sha256(v.image).hexdigest());(M/name/'partial-radio-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
