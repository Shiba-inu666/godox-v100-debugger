"""Native factory geometry, actual LVGL callbacks, isolated SUB controls."""
from revision_vm import *
from unicorn import UC_HOOK_CODE
from itertools import product
from collections import Counter
counts=Counter();examples=[];codes=[p for p in range(71) if p%10 in [0,3,7]]
def state(vm):
 return bytes(vm.u.mem_read(0x200004c3,0x32))+bytes(vm.u.mem_read(0x20000503,6))
def snapshot(vm):return [bytes(vm.u.mem_read(a,n)) for a,n in [(0x20000000,0x100000),(0x10000000,0x10000)]]
def restore(vm,data):
 for a,b in zip([0x20000000,0x10000000],data):vm.u.mem_write(a,b)
def rect(vm,obj,dy=0):
 a,b,c,d=vm.coords(obj);return [a,b-dy,c,d-dy]
def make():
 v=RevisionVM();buttons={};sym=v.manifest['symbols']
 def watch(u,a,s,d):
  obj,callback=v.args(2)
  for n in ['minus','plus']:
   if callback&~1==sym[n]&~1:buttons[n]=obj
 h=v.u.hook_add(UC_HOOK_CODE,watch,begin=0x0803a03c,end=0x0803a03c)
 v.create(1);v.u.hook_del(h);v.render();return v,buttons
ref=NativeVM(image=RAW);ref.create(0);ref.event(ref.rw(0x1550))
expected={}
for name,o in [('minus',0x159c),('plus',0x1594)]:
 for power in codes:
  ref.wb(0x4c0,power);ref.event(ref.rw(o));expected[name,power]=ref.rb(0x4c0)
v,buttons=make();baseline=snapshot(v)
assert set(buttons)=={'plus','minus'}
# Identical native numerical anchors and +/- rectangles, translated one row down.
for decimal,power in product([0,1],codes):
 restore(v,baseline);v.wb(0x12f0,decimal);v.wb(0x4c0,power);v.wb(0x4d0,power)
 v.call(0x08016cf4);v.wb(0x38c,255);v.function('sub_refresh');v.render()
 for sub,main in [(0x155c,0x161c),(0x1560,0x1620),(0x1558,0x1624),(0x1564,0x1628)]:
  assert v.text(v.rw(sub))==v.text(v.rw(main)),(decimal,power,hex(sub),v.text(v.rw(sub)),v.text(v.rw(main)))
  assert rect(v,v.rw(sub),86)==rect(v,v.rw(main)),(decimal,power,hex(sub),v.coords(v.rw(sub)),v.coords(v.rw(main)))
 for n,o in [('minus',0x16d0),('plus',0x16a8)]:assert rect(v,buttons[n],86)==rect(v,v.rw(o))
 if power in [0,30,70]:examples.append(dict(decimal=decimal,power=power,number=rect(v,v.rw(0x155c)),minus=rect(v,buttons['minus']),plus=rect(v,buttons['plus']),label=rect(v,v.rw(0x1554))))
 counts['all_power_formats_match_native_M_row_geometry']+=1
for name,power in product(['minus','plus'],codes):
 restore(v,baseline);v.wb(0x4c0,power);before=state(v);v.event(buttons[name]);v.render()
 assert v.rb(0x4c0)==expected[name,power] and not v.rw(0x156c) and state(v)==before
 counts['row_buttons_native_SUB_steps_no_main_group_focus_changes']+=1
guards=[(0x599,1),(0x59a,1),(0x54b,1),(0x496,0),(0x4c3,2),(0x398,9),(0x4c1,0)]
for name,(off,value) in product(['minus','plus'],guards):
 restore(v,baseline);v.wb(off,value);before=state(v);v.event(buttons[name]);assert v.rb(0x4c0)==30 and state(v)==before
 counts['row_buttons_blocked_state_and_SUB_OFF']+=1
for name in ['minus','plus']:
 restore(v,baseline);v.event(v.rw(0x1550));v.event(buttons[name]);assert v.rb(0x4c0)==30
 counts['background_buttons_blocked_while_editor_open']+=1
for name,code in product(['minus','plus'],[1,2,3,6,7,12,0x1c]):
 restore(v,baseline);v.event(buttons[name],code);assert v.rb(0x4c0)==30
 counts['non_click_events_do_not_adjust']+=1
for on,head in product([0,1],[0,1]):
 restore(v,baseline);v.wb(0x4c1,on);v.wb(0x544,head);v.wb(0x38c,255);v.function('sub_refresh');v.render()
 assert v.text(v.rw(0x155c))==('8' if on else 'OFF')
 assert bool(v.call(0x0803c616,v.rw(0x1568),1))==bool(head or not on)
 assert v.coords(v.rw(0x1554))[2]<v.coords(buttons['minus'])[0]
 counts['OFF_label_head_warning_and_label_fit']+=1
for decimal,power in product([0,1],codes):
 restore(v,baseline);v.wb(0x12f0,decimal);v.wb(0x4c0,power);v.wb(0x38c,255);v.function('sub_refresh');v.render()
 before=[(v.text(v.rw(o)),rect(v,v.rw(o))) for o in [0x155c,0x1560,0x1558,0x1564]]
 v.event(v.rw(0x1550));v.event(v.rw(0x1570));v.render()
 assert before==[(v.text(v.rw(o)),rect(v,v.rw(o))) for o in [0x155c,0x1560,0x1558,0x1564]]
 counts['modal_close_restores_native_Sender_not_compact_footer']+=1
for target,busy in [(1,0),(12,0),(0,1),(2,1)]:
 restore(v,baseline);v.event(v.rw(0x1550));row=v.rw(0x1550);modal=v.rw(0x156c);v.wb(0x599,busy)
 v.call(0x0801d008,target,0)
 assert v.rw(0x1550)==row and v.rw(0x156c)==modal
 assert v.call(0x0803cdbc,row) and v.call(0x0803cdbc,modal)
 counts['rejected_transition_never_frees_live_SUB']+=1
z=RevisionVM();z.wb(0x5a1,0);old=z.create(0);z.event(z.rw(0x1550));outgoing=z.rw(0x1550)
z.call(0x0801d008,1,0);new=z.rw(0x600);z.call(0x0803f714,new,0,0,0,1)
assert not z.call(0x0803cdbc,old) and z.rw(0x156c)==0
assert z.call(0x0803b788,z.rw(0x1550))==z.rw(0x15b4)
z.wb(0x599,0);z.wb(0x59a,0);z.event(z.rw(0x1550));assert z.rw(0x156c)
counts['Hotshoe_open_SUB_to_Sender_reclaim_and_reopen']+=1
r=dict(status='PASS_R5_NATIVE_SENDER_ROW',candidate_sha256=sha(IMAGE),counts=dict(counts),total=sum(counts.values()),examples=examples,hardware_verified=False,limits=['Actual LVGL objects and event dispatch, native fonts and stock group widget factory','Touch controller raw coordinate and physical LCD appearance not verified','R7 single S uses bitmap-verified native font centered within the original 46-pixel group tile'])
(ROOT/'analysis/SENDER_ROW_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
