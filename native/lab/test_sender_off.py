"""Execute actual camera / TEST paths, requiring SUB-only and stock RF parity.
Transport/delays are substituted; virtual registers do not prove physical sync.
"""
from fire_vm import *
from itertools import product
from collections import Counter
counts=Counter();samples=[];s=FireVM(RAW);v=FireVM()
codes=[p for p in range(71) if p%10 in [0,3,7]]
def run(vm,mode,off_kind=0,changes=None,entry=0x0800b1ec,role=3):
 vm.setup(role,mode);vm.wb(0x54c,5);vm.wb(0x512,10);vm.wb(0x4ae,1)
 if off_kind==0:vm.wb(0x504,0);vm.wb(0x4c4,2)
 else:vm.wb(0x4c4,1);vm.wb(0x4d0,255)
 for o,b in (changes or {}).items():vm.wb(o,b)
 before=bytes(vm.u.mem_read(RAM+0x4c4,0x21))+bytes(vm.u.mem_read(RAM+0x503,6))
 result=vm.run(entry)
 if entry!=0x08010f98:assert before==bytes(vm.u.mem_read(RAM+0x4c4,0x21))+bytes(vm.u.mem_read(RAM+0x503,6))
 return result
for mode,kind,ready,present,subready,on,head in product([0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]):
 changes={0x50c:ready,0x496:present,0x497:subready,0x4c1:on,0x544:head}
 a=run(s,mode,kind,changes);b=run(v,mode,kind,changes)
 expected=bool(ready and present and subready and on and head)
 assert b['sub']==expected and a['main_trigger_set_requests']==b['main_trigger_set_requests']==0
 assert b['radio_serial_hex']==a['radio_serial_hex'] and v.rb(0x512)==0
 assert v.rb(0x33c)==3 and v.rb(0x4c0)==30
 assert not any(mask==0x200 for _,mask,_ in b['gpio']),b
 counts['OFF_main_no_pulse_ready_presence_ON_head_matrix']+=1
 if ready and present and on and head:samples.append(dict(mode=mode,off_kind=kind,subready=subready,main=0,sub=expected,radio=b['radio_serial_hex']))
# Real camera dispatcher, both clock branches, full stock photographic U16 table.
for mode,kind,power,clock in product([0,1],[0,1],codes,[0,1]):
 changes={0x4c0:power,0x45:clock}
 a=run(s,mode,kind,changes,0x0800edd4);b=run(v,mode,kind,changes,0x0800edd4)
 assert b['sub'] and b['main_trigger_set_requests']==0 and b['radio_serial_hex']==a['radio_serial_hex']
 duration=struct.unpack_from('<H',RAW,0x080528d6-0x08008000+(80-power)*2)[0]
 assert b['local_main_energy']['timer_reload_requests']==[duration*(48 if clock==1 else 240)]
 assert b['gpio']==[[0x40020800,0x2000,1],[0x40020800,0x2000,0]]
 assert v.rb(0x4c2)==0 and v.rh(0x522)==0 and 0x0802a9d0 not in v.executed
 assert 0x0800fbA0 not in v.executed # No fabricated main-pulse thermal accounting.
 counts['camera_IRQ_all_SUB_powers_U16_no_main_gate']+=1
# Safety flags, invalid table index and excluded mode/command stay byte-observation
# equivalent to the original radio-only branch, without creating a later request.
excluded=[{o:1} for o in [0x531,0x536,0x53c]]
excluded += [{0x4c0:x} for x in range(256) if x not in codes]
excluded += [{0x512:x,0x421:1} for x in [0,5,8,0x1a,0x8a,0x9a]]
for mode,kind,changes in product([0,1],[0,1],excluded):
 a=run(s,mode,kind,changes);b=run(v,mode,kind,changes)
 assert pulse_signature(a)==pulse_signature(b) and not b['sub'],(mode,kind,changes,a,b)
 counts['invalid_or_excluded_state_original_parity']+=1
for mode in [2,3,0x10,0x11]:
 a=run(s,mode,changes={0x421:1});b=run(v,mode,changes={0x421:1})
 assert pulse_signature(a)==pulse_signature(b);counts['Multi_HSS_other_mode_original']+=1
for role in [0,1,2,4,5]:
 a=run(s,1,1,role=role);b=run(v,1,1,role=role)
 assert pulse_signature(a)==pulse_signature(b);counts['non_Sender_OFF_path_unchanged']+=1
# A GUI page/lock must not prevent a legitimate camera exposure.
for page,lock in product([0,1,2,3,7,11],[0,1]):
 b=run(v,1,changes={0x59f:page,0x398:page,0x54b:lock})
 assert b['sub'] and b['main_trigger_set_requests']==0;counts['camera_independent_of_GUI_lock_focus']+=1
# No deferred fire. Updating ready flags after a dropped trigger cannot pulse.
for mode,notready in product([0,1],[0x50c,0x497]):
 b=run(v,mode,changes={notready:0});assert not b['sub'] and v.rb(0x512)==0
 v.clear_trace();v.wb(0x497,1);v.stub(0x08009174);v.call(0x0800b480)
 assert not v.gpio and not v.stores;counts['not_ready_drop_no_replay']+=1
# TEST still follows the original TEST main-light behavior; OFF does not redefine it.
r4=transform(RAW,load_spec('r4'));previous=FireVM(r4)
for mode,kind,power in product([0,1],[0,1],codes):
 a=run(previous,mode,kind,{0x4c0:power},0x08010f98);b=run(v,mode,kind,{0x4c0:power},0x08010f98)
 assert pulse_signature(a)==pulse_signature(b) and b['sub']==a['sub']
 assert bytes(previous.u.mem_read(RAM+0x4c4,0x21))==bytes(v.u.mem_read(RAM+0x4c4,0x21))
 if kind==0:assert b['sub'] and b['main_trigger_set_requests']==1
 counts['TEST_main_OFF_retains_R4_and_stock_main_semantics']+=1
r=dict(status='PASS_R5_SENDER_OFF_SUB_ONLY',candidate_sha256=sha(IMAGE),counts=dict(counts),total=sum(counts.values()),examples=samples,hardware_verified=False,limits=['Actual firmware camera dispatcher and SUB pulse body; virtual ready flags and peripherals','Original RF byte sequence retained; no physical RF/shutter latency or light-output measurement','Normal command 0x0A only; original 0x8A radio-only no-op, HSS and Multi remain unchanged','Native SUB charging/ready/body unchanged; analog safety and recovery not proven'])
(ROOT/'analysis/SENDER_OFF_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
