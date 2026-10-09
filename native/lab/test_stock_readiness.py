"""Evidence for stock ready/skip semantics; not an analog capacitor model."""
from fire_vm import *
from itertools import product
from collections import Counter
counts=Counter();records=[];v=FireVM(RAW)
for role,present,subready,mask in product([0,3,4],[0,1],[0,1],range(32)):
 v.setup(role,1);v.wb(0x50c,0);v.wb(0x496,present);v.wb(0x497,subready)
 for bit,off in enumerate([0x50d,0x50f,0x550,0x586,0x42e]):v.wb(off,(mask>>bit)&1)
 v.stub(0x08009174);v.call(0x0800b480)
 expected=bool(mask==0 and (not present or subready));assert v.rb(0x50c)==expected
 counts['original_readiness_promotion_all_roles']+=1
# Not-ready triggers are consumed, not scheduled for a later full capacitor.
for role,mode,event in product([0,3,4],[0,1],['TEST','camera','radio']):
 if event=='radio' and role!=4:continue
 v.setup(role,mode);v.wb(0x50c,0);v.wb(0x512,10);v.wb(0x4fd,10);v.wb(0x54c,5)
 r=v.run(0x08010f98 if event=='TEST' else (0x08020534 if event=='radio' else 0x0800b1ec))
 assert not r['sub'] and r['main_trigger_set_requests']==0
 assert v.rb(0x4fd if event=='radio' else 0x512)==0
 records.append(dict(role=role,mode=mode,event=event,ready=0,main=0,sub=0,remote_TEST_commands=r['remote_fire_command_count'],radio_serial=r['radio_serial_hex']))
 v.clear_trace();v.wb(0x497,1);v.stub(0x08009174);v.call(0x0800b480)
 assert v.rb(0x50c)==1 and not v.gpio and not v.stores
 counts['original_drop_trigger_no_auto_replay_on_ready']+=1
r=dict(status='CONFIRMED_STOCK_READY_SKIP_NO_READY_WAIT_LOOP',candidate_sha256=sha(IMAGE),stock_sha256=sha(RAW),counts=dict(counts),total=sum(counts.values()),not_ready_records=records,evidence=['0800B480 promotes overall ready only when protection counters clear and attached SUB ready','0800EF78/0800B1EC/08020534 return and clear the trigger when not ready','08010F98 Sender sends radio TEST before its local EF78 ready check','0802A9D0 returns without either local pulse if SUB ready != 1'],limits=['Firmware local flags and selected trigger chains; camera can independently delay shutter based on ready line','No all-receiver-ready barrier found in traced normal TEST/exposure paths; other model receiver firmware not inspected','No analog charge voltage or physical capacitor timing measurement'])
(ROOT/'analysis/STOCK_READINESS_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
