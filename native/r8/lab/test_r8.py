"""Execute full candidate instructions and actual LVGL objects for R8 changes."""
from probe import *
from itertools import product
from collections import Counter
from unicorn import UC_HOOK_CODE
from config import RAW,transform,load_spec
counts=Counter();samples=[]
OUT=ROOT/'.lab';OUT.mkdir(exist_ok=True)
def check(ok,label):
 assert ok,label
 counts[label]+=1
def make(page=1,language=0,decimal=0):
 v=VM();v.wb(0x5a1,0);v.wb(0x12fa,language);v.wb(0x12f0,decimal);v.create(page);v.render();return v
def tick(v):v.call(0x080426bc);v.render()
def settings(v):return [bytes(v.u.mem_read(0x20000000+a,n)) for a,n in [(0x4c0,2),(0x4c4,5),(0x4d0,5),(0x4ef,5),(0x504,5),(0x3da,1)]]
def isolated(before,after,g,changed=()):
 for k,(a,b) in enumerate(zip(before,after)):
  for i,(x,y) in enumerate(zip(a,b)):
   if k==5:
    assert (x^y)&~(1<<g)==0
   elif (k,i) not in [(kind,g) for kind in changed]:assert x==y,(k,i,x,y,g,changed)
def text(v,idx):return v.text(v.child(v.child(v.modal(),idx),0))
def press(v,idx):v.event(v.child(v.modal(),idx));tick(v)
def saved(v):return [bytes(v.u.mem_read(a,n)) for a,n in [(0x20000000,0x100000),(0x10000000,0x10000)]]
def restore(v,s):
 for a,b in zip([0x20000000,0x10000000],s):v.u.mem_write(a,b)
def hit(v,r,x,y):
 v.u.mem_write(0x200e0000,struct.pack('<hh',x,y));return v.call(0x08038604,r,0x200e0000)

# Footer text/font/geometry exactly follows hotshoe in both languages.
print("footer",flush=True)
for language,mode,decimal,on in product([0,1],[0,1],[0,1],[0,1]):
 a,b=make(0,language,decimal),make(2,language,decimal)
 for v in [a,b]:v.wb(0x4c3,mode);v.wb(0x4c1,on);tick(v)
 check(a.text(a.rw(0x1554))==b.text(b.rw(0x1554))==('副灯' if language==0 else 'SUB'),'RX_native_hotshoe_name')
 check(a.coords(a.rw(0x1554))==b.coords(b.rw(0x1554)),'RX_native_hotshoe_label_geometry')
 b.event(b.rw(0x1550));b.event(b.rw(0x1570));tick(b)
 check(a.text(a.rw(0x1554))==b.text(b.rw(0x1554)),'RX_close_preserves_label')

# S uses native row metrics, no missing glyph fallback, baseline matches M-A-D.
v=make();title=v.rw(0x1554);x,y,r,b=v.coords(title);mx,my,mr,mb=v.coords(v.rw(0x15f4))
check((y,b)==(my+86,mb+86) and b-y+1==29,'S_matches_M_row_height_and_baseline')
font=v.manifest['symbols']['s_font'];glyph=v.manifest['symbols']['s_glyph'];bitmap=v.manifest['symbols']['s_pixels']
check(v.call(glyph,font,0x200e0000,ord('S'),0)==1,'S_glyph_exists')
d=struct.unpack('<IHHHhhBB',v.u.mem_read(0x200e0000,16))
check(d[3]==29 and d[5]==-3 and d[6]==4,'S_glyph_real_cap_height_and_baseline')
ptr=v.call(bitmap,font,ord('S'));check(bool(ptr) and any(v.u.mem_read(ptr,334)),'S_real_bitmap')
check(v.call(glyph,font,0x200e0000,ord('U'),0)==0,'S_font_missing_character_fails_cleanly')
v.render(str(OUT/'sender.png'))

# Actual native touch search on each scrolled row: both its title and
# numerical field open the editor; +/- keep their independent native actions.
for g in range(5):
 v=make();row=v.rw(0x15b8+g*4)
 v.call(0x0803e0b4,row,0);v.render();y=v.coords(row)[1]+40
 for x in [25,160,240]:
  target=hit(v,v.rw(0x600),x,y)
  check(target==row,'title_and_number_native_hit_test_reaches_row')
  v.event(target);check(bool(v.modal()),'actual_title_and_number_tap_opens_editor')
  press(v,1)
 for x,offset in [(90,0x16d0),(425,0x16a8)]:
  check(hit(v,v.rw(0x600),x,y)==v.rw(offset+g*8),'native_row_plus_minus_hit_targets_preserved')

# Dedicated editor: selected group only; OFF state preserved during mode choice;
# native mode/enabled/mask triplet restored together, remembered TTL/M on reopen.
print("editors",flush=True)
for g,language,decimal,initial in product(range(5),[0,1],[0,1],[0,1,2]):
 v=make(1,language,decimal)
 v.wb(0x4c4+g,initial);v.wb(0x504+g,int(initial!=2));v.wb(0x3da,0x1f&~((1<<g) if initial==2 else 0));tick(v)
 before=settings(v);v.event(v.rw(0x15b8+4*g));m=v.modal();v.render()
 check(bool(m) and v.text(v.child(m,0))=='MABCD'[g],'each_row_single_click_opens_own_editor')
 isolated(before,settings(v),g)
 mode_rect=v.coords(v.child(m,3));switch_rect=v.coords(v.child(m,4))
 check(mode_rect[2]<switch_rect[0],'TTL_M_left_of_enable')
 for idx,point in [(1,(445,26)),(2,(240,120)),(3,(90,320)),(4,(380,320)),(5,(90,240)),(6,(380,240))]:
  check(hit(v,v.rw(0x600),*point)==v.child(m,idx),'native_touch_hits_editor_control')
 # If initially OFF, enable before verifying both mode toggles.
 if initial==2:press(v,4)
 expected=v.rb(0x4c4+g)
 for _ in range(2):
  old=settings(v);press(v,3);expected=1-expected
  check(v.rb(0x4c4+g)==expected and v.rb(0x504+g)==1 and v.rb(0x3da)&(1<<g),'TTL_M_updates_original_group_state')
  isolated(old,settings(v),g,(1,4));check(text(v,3)==('M' if expected else 'TTL'),'mode_button_readback')
 old=settings(v);press(v,4)
 check(v.rb(0x4c4+g)==2 and not v.rb(0x504+g) and not v.rb(0x3da)&(1<<g) and text(v,2)=='OFF','OFF_updates_mode_enable_mask_and_display')
 isolated(old,settings(v),g,(1,4))
 old=settings(v)
 for idx in [5,6]:press(v,idx)
 check(settings(v)==old,'OFF_blocks_power_adjustment')
 press(v,3);check(v.rb(0x4c4+g)==2 and not v.rb(0x504+g),'mode_choice_does_not_enable_OFF_group')
 remembered=1-expected
 press(v,1);check(v.modal()==0 and v.focus()==v.rw(0x15b8+4*g),'close_returns_focus_to_selected_row')
 v.event(v.rw(0x15b8+4*g));press(v,4)
 check(v.rb(0x4c4+g)==remembered,'OFF_mode_choice_survives_editor_reopen')
 if g==0 and language==0 and decimal==0 and initial==1:
  v.render(str(OUT/'group-M.png'));samples.append(dict(mode=mode_rect,switch=switch_rect))
 press(v,1)

# Every native manual power, decimal/step setting and TTL FEC input. Expected
# values come from the original R7 +/- callback on the corresponding row.
print("native value steps",flush=True)
for g,decimal,step in product(range(5),[0,1],[0,1]):
 v=make(1,0,decimal);ref=NativeVM(image=transform(RAW));ref.wb(0x5a1,0);ref.create(1)
 v.wb(0x5a,step);ref.wb(0x5a,step)
 v.event(v.rw(0x15b8+4*g));base=saved(v);baseline=saved(ref)
 for mode,values in [(1,range(81)),(0,range(-18,19,2))]:
  for value,idx in product(values,[5,6]):
   restore(v,base);restore(ref,baseline);off=(0x4d0 if mode else 0x4ef)+g
   for z in [v,ref]:z.wb(0x4c4+g,mode);z.wb(off,value);z.call(0x08016cf4)
   before=settings(v)
   ref.event(ref.rw((0x16d0 if idx==5 else 0x16a8)+8*g))
   v.event(v.child(v.modal(),idx))
   check(v.rb(off)==ref.rb(off),'all_group_power_FEC_steps_match_R7_native_buttons')
   isolated(before,settings(v),g,(2 if mode else 3,))

# Native encoder path: selector 0x11 uses the original selected-group routine.
print("encoder and guards",flush=True)
for g,mode in product(range(5),[0,1]):
 v=make();v.wb(0x4c4+g,mode);v.wb(0x4d0+g,40);tick(v);v.event(v.rw(0x15b8+g*4));before=settings(v)
 v.call(0x08010924);tick(v)
 check(v.rb(0x4b4)==g and before!=settings(v),'encoder_changes_selected_group')
 isolated(before,settings(v),g,(2 if mode else 3,))
 check(bool(v.modal()),'encoder_keeps_dedicated_editor_open')

# Native physical back/power-key event closes this panel first.
v=make();v.event(v.rw(0x15bc));root=v.rw(0x600)
a=v.stub(0x08037e78,lambda _:0);b=v.stub(0x08037e84,lambda _:2)
v.event(root,0xc);v.u.hook_del(a);v.u.hook_del(b)
check(not v.modal() and v.rb(0x59f)==1 and v.focus()==v.rw(0x15bc),'physical_back_closes_editor_without_leaving_sender')

# Reject stale/background/repeated/locked events without modifying groups.
for off,value in [(0x599,1),(0x59a,1),(0x54b,1),(0x398,9),(0x748,1),(0x74a,1),(0x74b,1)]:
 v=make();v.wb(off,value);old=settings(v);v.event(v.rw(0x15b8))
 check(not v.modal() and settings(v)==old,'blocked_state_rejects_row_open')
 v=make();v.event(v.rw(0x15b8));v.wb(off,value);old=settings(v)
 for idx in [2,3,4,5,6]:v.event(v.child(v.modal(),idx))
 check(settings(v)==old,'blocked_state_rejects_editor_mutations')
for g in range(5):
 v=make();v.event(v.rw(0x15b8+g*4));m=v.modal();old=settings(v)
 for i in range(5):v.event(v.rw(0x15b8+i*4))
 v.event(v.rw(0x1550))
 check(v.modal()==m and not v.rw(0x156c) and settings(v)==old,'modal_prevents_nested_group_or_SUB_editor')

# A background switch to Multi must close the custom editor before stock
# mode refresh changes the group widgets and their focus list.
v=make();v.event(v.rw(0x15b8));v.wb(0x4c3,2);tick(v)
check(not v.modal(),'Multi_switch_closes_group_editor_before_native_relayout')

# Exact short power/back input used to exit Receiver, including animation.
v=make(2);old=v.rw(0x604);row=v.rw(0x1550)
a=v.stub(0x08037e78,lambda _:0);b=v.stub(0x08037e84,lambda _:2)
v.event(old,0xc);v.u.hook_del(a);v.u.hook_del(b)
check(v.rb(0x59f)==5 and v.call(0x0803cdbc,row),'Receiver_physical_exit_retains_SUB_during_animation')

# Actual screen transition: outgoing SUB survives until native screen deletion.
print("transitions",flush=True)
for source,target in product(range(3),[0,1,2,5]):
 if source==target:continue
 v=make(source);old=v.rw({0:0x5d8,1:0x600,2:0x604}[source]);row=v.rw(0x1550)
 # Record row deletion and target-construction order via real LVGL objects.
 deleted=[]
 h=v.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:deleted.append(v.args(1)[0]),begin=0x0803ab3c,end=0x0803ab3c)
 v.call(0x0801d008,target,6)
 if target==1:
  check(row in deleted,'direct_Sender_transition_reclaims_SUB_for_heap_capacity')
 else:
  check(v.call(0x0803cdbc,old) and v.call(0x0803cdbc,row) and row not in deleted,'outgoing_SUB_survives_native_transition')
  check(not v.call(0x0803c616,row,1),'outgoing_SUB_not_hidden_early')
 new=v.rw({0:0x5d8,1:0x600,2:0x604,5:0x5fc}[target])
 v.call(0x0803f714,new,0,0,0,1)
 check(not v.call(0x0803cdbc,old),'native_screen_deletion_reclaims_outgoing_screen')
 if target!=1:check(not v.call(0x0803cdbc,row),'native_screen_deletion_reclaims_outgoing_SUB')
 v.u.hook_del(h)

# Repeated editor deletion/recreation cannot retain the focus list or leak heap.
v=make();first=None
for cycle in range(50):
 g=cycle%5;v.event(v.rw(0x15b8+g*4));m=v.modal();check(bool(m),'repeat_open_50_cycles')
 press(v,1);check(not v.call(0x0803cdbc,m),'repeat_close_releases_panel')

report=dict(status='PASS_R8_NATIVE_UI',candidate_sha256=sha(IMAGE),total=sum(counts.values()),counts=dict(counts),samples=samples,hardware_verified=False)
(OUT/'R8_UI_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
