from fire_vm import *
from itertools import product
from collections import Counter
counts=Counter();records=[];s=FireVM(RAW);v=FireVM();codes=[p for p in range(71) if p%10 in [0,3,7]]
def pair(role,mode,changes,entry):
 ans=[]
 for vm in [s,v]:
  vm.setup(role,mode);vm.wb(0x54c,5)
  for off,val in changes.items():vm.wb(off,val)
  ans.append(vm.run(entry))
 return ans
# Core original readiness semantics, independent of physical transistor model.
for role,mode,ready,present,subready,on,head,event in product([0,3,4],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],['TEST','exposure']):
 entry=0x08010f98 if event=='TEST' else (0x08020534 if role==4 else 0x0800b1ec)
 a,b=pair(role,mode,{0x50c:ready,0x496:present,0x497:subready,0x4c1:on,0x544:head,0x4fd:10,0x512:10},entry)
 main=bool(ready and (not present or subready));sub=bool(main and present and on and head)
 assert b['sub']==sub and b['main_trigger_set_requests']==int(main),(role,mode,ready,present,subready,on,head,event,a,b)
 assert b['radio_serial_hex']==a['radio_serial_hex']
 if role==0:assert pulse_signature(a)==pulse_signature(b)
 assert v.rb(0x33c)==role and v.rb(0x4c0)==30
 counts['ready_on_presence_head_TEST_exposure_matrix']+=1
 if present and on and head:records.append(dict(role=role,mode=mode,event=event,ready=ready,subready=subready,main=main,sub=sub,radio_commands=b['remote_fire_command_count']))
# Actual RF interrupt -> FIFO -> power update -> trigger; SUB is local and independent.
rf_samples=[]
for group,mode,power,subpower,clock,command in product([1,3,5],[0,1],[0,10,40,70,80],codes,[0,1],['broadcast','addressed']):
 out=[]
 for vm in [s,v]:
  vm.setup(4,mode,subpower);vm.wb(0x503,group);vm.wb(0x33e,group+9);vm.wb(0x54c,5);vm.wb(0x45,clock)
  vm.packet([0xa9,group+9,0xbc,power]);vm.packet([0xa9,group+9,0xb9,80])
  assert vm.rb(0x4d0+group)==power and vm.rb(0x4c0)==subpower
  vm.clear_trace();r=vm.packet([0xd5,0x19,0,0] if command=='broadcast' else [0xa9,group+9,0xb4,9]);out.append(r)
 a,b=out;assert b['sub'] and b['main_trigger_set_requests']==a['main_trigger_set_requests']==1
 assert b['local_main_energy']['prepared_duration_code']==a['local_main_energy']['prepared_duration_code']
 assert v.rb(0x4c0)==subpower and v.rb(0x4d0+group)==power and 0x0802a9d0 in v.executed
 counts['RF_FIFO_remote_main_local_SUB_power_independence']+=1
 if group==1 and clock==1 and subpower in [0,30,70] and command=='broadcast':rf_samples.append(dict(mode=mode,remote_main_code=power,local_SUB_code=subpower,duration_code=b['local_main_energy']['prepared_duration_code'],timer_reloads=b['local_main_energy']['timer_reload_requests']))
# Sender real camera IRQ path, all supported local SUB codes.
for mode,power,subpower,clock in product([0,1],[0,30,60,80],codes,[0,1]):
 a,b=pair(3,mode,{0x4d0:power,0x4c0:subpower,0x45:clock,0x512:10,0x4ae:1},0x0800edd4)
 assert b['sub'] and b['main_trigger_set_requests']==1
 assert a['local_main_energy']['prepared_duration_code']==b['local_main_energy']['prepared_duration_code']
 assert a['radio_serial_hex']==b['radio_serial_hex'];counts['Sender_camera_main_preparation_and_radio_preserved']+=1
# Excluded HSS/invalid commands and RX group OFF; Sender OFF is independently tested.
for role,mode,cmd in product([0,3,4],[0,1,0x10,0x11],[0,5,8,0x1a,0x9a]):
 entry=0x08020534 if role==4 else 0x0800b1ec
 a,b=pair(role,mode,{0x512:cmd,0x4fd:cmd},entry)
 assert pulse_signature(a)==pulse_signature(b),(role,mode,cmd,a,b)
 counts['excluded_command_HSS_original_parity']+=1
for role,mode in product([3,4],[0,1]):
 changes={0x512:10,0x4fd:10,0x504:0,0x4c4:2} if role==3 else {0x4fd:10,0x4d1:255}
 if role==4 and mode==0:continue # TTL ignores M-power OFF by original design.
 a,b=pair(role,mode,changes,0x08020534 if role==4 else 0x0800b1ec)
 if role==3:
  assert b['sub'] and b['main_trigger_set_requests']==0 and a['radio_serial_hex']==b['radio_serial_hex'];counts['Sender_local_OFF_SUB_independent']+=1
 else:
  assert pulse_signature(a)==pulse_signature(b) and not b['sub'];counts['RX_M_group_OFF_original']+=1
# Existing error/inhibit and invalid stored SUB code cannot activate new SUB.
for role,mode in product([3,4],[0,1]):
 for off,val in [(0x531,1),(0x536,1),(0x53c,1)]+[(0x4c0,x) for x in range(256) if x not in codes]:
  a,b=pair(role,mode,{off:val,0x512:10,0x4fd:10},0x08020534 if role==4 else 0x0800b1ec)
  assert not b['sub'] and pulse_signature(a)==pulse_signature(b),(role,mode,off,val)
  counts['new_path_invalid_state_fail_closed']+=1
# GUI lock/menu cannot suppress normal RX exposure; it is not a TEST/UI action.
for page,locked in product([0,1,2,3,7,11],[0,1]):
 a,b=pair(4,1,{0x59f:page,0x398:page,0x54b:locked,0x4fd:10},0x08020534)
 assert b['sub'];counts['normal_exposure_independent_of_UI_focus_lock_page']+=1
r=dict(status='PASS_BOUNDED_R5_FIRING_AND_READINESS',candidate_sha256=sha(IMAGE),counts=dict(counts),total=sum(counts.values()),readiness_matrix=records,RF_examples=rf_samples,hardware_verified=False,limits=['Original CPU code and FIFO dispatcher; virtual GPIO/SysTick','Transport/delay/HSS and thermal completion stubbed, unchanged completion call retained','No physical microseconds/energy/temperature/recovery proof','RX main OFF tested in M; TTL original semantics retained'])
(ROOT/'analysis/FIRING_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
