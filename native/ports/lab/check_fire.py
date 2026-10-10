from port_vm import M
from fire_probe import FireVM
from pathlib import Path
from itertools import product
import json,hashlib,sys
name=sys.argv[1] if len(sys.argv)>1 else 'V100O_V1.04'
s=FireVM(name,False);v=FireVM(name,True);checks=[]
def check(ok,name,detail):
 assert ok,(name,detail)
 checks.append(name)
def runpair(role,mode,event,changes):
 results=[]
 for vm in [s,v]:
  vm.setup(role,mode);vm.wf(0x54c,5);vm.wf(0x4fd,10);vm.wf(0x512,10)
  for off,value in changes.items():vm.wf(off,value)
  results.append(vm.runf(0x8010f98 if event=='TEST' else 0x8020534 if role==4 else 0x800b1ec))
 return results
for role,mode,ready,present,subready,on,head,event in product([0,3,4],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],['TEST','exposure']):
 changes={0x50c:ready,0x496:present,0x497:subready,0x4c1:on,0x544:head}
 a,b=runpair(role,mode,event,changes)
 main=bool(ready and (not present or subready));sub=bool(main and present and on and head)
 detail=(role,mode,ready,present,subready,on,head,event,a['sub'],b['sub'],a['main_trigger_set_requests'],b['main_trigger_set_requests'])
 check(b['sub']==sub and b['main_trigger_set_requests']==int(main),'ready_on_presence_head',detail)
 check(b['radio_serial_hex']==a['radio_serial_hex'],'radio unchanged',detail)
 if role==0:check(a['gpio']==b['gpio'],'WiOff unchanged',detail)
 check(v.rf(0x33c)==role and v.rf(0x4c0)==30,'role and SUB power unchanged',detail)
print('readiness matrix',len(checks),flush=True)
for role,mode in product([3,4],[0,1]):
 for off,val in [(0x531,1),(0x536,1),(0x53c,1)]+[(0x4c0,x) for x in range(256) if x>70 or x%10 not in [0,3,7]]:
  a,b=runpair(role,mode,'exposure',{off:val})
  check(not b['sub'] and a['gpio']==b['gpio'] and a['radio_serial_hex']==b['radio_serial_hex'],'invalid state fail closed',(role,mode,off,val))
for mode,power in product([0,1],[0,3,7,10,30,50,67,70]):
 a,b=runpair(3,mode,'exposure',{0x504:0,0x4c4:2,0x4c0:power})
 check(b['sub'] and b['main_trigger_set_requests']==0 and a['radio_serial_hex']==b['radio_serial_hex'],'Sender main OFF independent SUB',(mode,power))
r=dict(status='PASS_FIRING',model=name,checks=len(checks),hardware_verified=False,candidate_sha256=hashlib.sha256(v.image).hexdigest())
(M/name/'partial-fire-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
