"""R9 native gestures, editor controls, display, full encoder input and lifecycle.

Runs complete candidate instructions/LVGL. Only physical touch/GPIO samples,
LCD transfer and three wake/beep services are substituted. No hardware claim.
"""
from probe import *
from input_driver import *
from itertools import product
from collections import Counter
from config import RAW,transform
from unicorn.arm_const import UC_ARM_REG_PRIMASK
counts=Counter();heap_samples=[];OUT=ROOT/'.lab';OUT.mkdir(exist_ok=True)

def check(ok,label,detail=None):
 assert ok,(label,detail)
 counts[label]+=1

def make(page=1,image=IMAGE,language=0,decimal=0,capture=False):
 v=VM(image,capture=capture);v.wb(0x5a1,0);v.wb(0x12fa,language);v.wb(0x12f0,decimal)
 v.create(page);v.render();clean(v);return v

def tick(v):v.call(0x080426bc);v.render()
def save(v):return [bytes(v.u.mem_read(a,n)) for a,n in [(RAM,0x100000),(0x10000000,0x10000)]]
def restore(v,s):
 for a,b in zip([RAM,0x10000000],s):v.u.mem_write(a,b)
def settings(v):return [bytes(v.u.mem_read(RAM+a,n)) for a,n in [(0x4c0,2),(0x4c4,5),(0x4d0,5),(0x4ef,5),(0x504,5),(0x3da,1)]]
def isolated(before,after,g,kinds=()):
 for k,(a,b) in enumerate(zip(before,after)):
  for i,(x,y) in enumerate(zip(a,b)):
   if k==5:assert (x^y)&~(1<<g)==0
   elif (k,i) not in [(kind,g) for kind in kinds]:assert x==y,(k,i,x,y,g,kinds)
def open_group(v,g):
 row=v.rw(0x15b8+4*g)
 # Event-level entry used in the value/encoder matrices. Real input/hit-test
 # and long/drag separation are tested independently below.
 v.event(row,1);v.event(row,8);v.event(row,4)
 check(bool(v.modal()),'open_each_group',g)
def press(v,i):v.event(v.child(v.modal(),i));tick(v)
def text(v,i):return v.text(v.child(v.child(v.modal(),i),0))
def value(v):
 field=v.child(v.modal(),2)
 return [v.text(v.child(field,i)) for i in range(4)]
def hit(v,r,x,y):
 v.u.mem_write(RAM+0xe0000,struct.pack('<hh',x,y));return v.call(0x08038604,r,RAM+0xe0000)
def row_y(v,g):
 row=v.rw(0x15b8+4*g);v.call(0x0803e0b4,row,0);v.render();return v.coords(row)[1]+40

print('native gestures',flush=True)
r7=transform(RAW)
for g,mode in product(range(5),range(3)):
 v=make();ref=make(image=r7)
 for w in [v,ref]:
  w.wb(0x4c4+g,mode);w.wb(0x504+g,mode!=2);w.call(0x0801687c);w.call(0x08016cf4)
 y,ry=row_y(v,g),row_y(ref,g)
 touch,rt=Touch(v),Touch(ref)
 # Actual LVGL long-press timer emits events 5/6 and no short-click.
 for _ in range(3):
  touch.hold(220,y);rt.hold(220,ry)
  check(settings(v)==settings(ref),'native_long_press_three_mode_cycle_parity',(g,mode))
  check(not v.modal(),'long_release_does_not_open_editor')
 # Drag input goes through the original native slider callback.
 for dx in [80,-80]:
  touch.drag(220,y,dx);rt.drag(220,ry,dx)
  check(settings(v)==settings(ref),'native_swipe_power_FEC_OFF_parity',(g,mode,dx))
  check(not v.modal(),'swipe_release_does_not_open_editor')
 # +/- continue to use their native hit targets/actions.
 for x in ([70,425] if v.rb(0x4c4+g)!=2 else []):
  touch.tap(x,y);rt.tap(x,ry)
  check(settings(v)==settings(ref) and not v.modal(),'list_plus_minus_remain_native',(g,mode,x,hex(v.modal()),settings(v),settings(ref)))
 # Both group badge and value open this group by a real short tap.
 for x in [25,220]:
  before=settings(v);touch.tap(x,y);v.render()
  check(bool(v.modal()) and v.text(v.child(v.modal(),0))=='MABCD'[g],'real_short_tap_opens_correct_group',(g,mode,x))
  check(settings(v)==before,'short_tap_does_not_change_power_or_mode')
  touch.tap(440,25);v.render();check(not v.modal(),'touch_back_returns_to_list')
 touch.close();rt.close()

# A drag that returns to its start still must not be mistaken for a tap.
v=make();t=Touch(v);t.send(220,80,1);t.send(250,80,1);t.send(220,80,1);t.send(220,80,0)
check(not v.modal(),'out_and_back_drag_is_not_a_tap')
# Vertical list scrolling remains native, including the later C/D rows.
v=make();ref=make(image=r7);t,rt=Touch(v),Touch(ref)
t.drag(220,250,0,-130);rt.drag(220,250,0,-130)
v.render();ref.render()
check([v.coords(v.rw(0x15b8+4*g)) for g in range(5)]==[ref.coords(ref.rw(0x15b8+4*g)) for g in range(5)],'vertical_scroll_geometry_matches_R7')
check(not v.modal(),'vertical_scroll_does_not_open_editor')

print('editor controls and native display',flush=True)
for g,initial,decimal in product(range(5),range(3),[0,1]):
 v=make(decimal=decimal);v.wb(0x4c4+g,initial);v.wb(0x504+g,initial!=2);v.wb(0x3da,31&~((1<<g) if initial==2 else 0));tick(v)
 open_group(v,g);v.render();m=v.modal()
 check(v.function('editor_target')==17 and v.rb(0x4b4)==g,'fixed_encoder_scope_is_current_group')
 check(v.coords(v.child(m,3))[2]<v.coords(v.child(m,4))[0],'mode_button_left_of_pause')
 for i,x,y in [(1,440,25),(2,240,129),(3,150,307),(4,380,307),(5,50,129),(6,430,129),(7,240,210)]:
  check(hit(v,v.rw(0x600),x,y)==v.child(m,i),'editor_native_touch_target',(i,g))
 if initial==2:press(v,4)
 mode=v.rb(0x4c4+g)
 for _ in range(2):
  before=settings(v);press(v,3);mode=1-mode
  check(v.rb(0x4c4+g)==mode and text(v,3)==('M' if mode else 'TTL'),'TTL_M_switch_readback')
  isolated(before,settings(v),g,(1,4))
 before=settings(v);press(v,4)
 check(v.rb(0x4c4+g)==2 and not v.rb(0x504+g) and not v.rb(0x3da)&(1<<g) and text(v,4)=='OFF','pause_updates_mode_enable_mask')
 isolated(before,settings(v),g,(1,4))
 paused=settings(v);stored=value(v)
 for i in [2,5,6]:press(v,i)
 for address in [0x8010924,0x800ba84]:v.call(address)
 check(settings(v)==paused and value(v)==stored,'paused_encoder_buttons_leave_settings_unchanged')
 press(v,3)
 check(v.rb(0x4c4+g)==2 and not v.rb(0x504+g),'TTL_M_preselection_keeps_group_paused')
 chosen=1-mode;press(v,1);open_group(v,g);press(v,4)
 check(v.rb(0x4c4+g)==chosen and v.rb(0x504+g) and v.rb(0x3da)&(1<<g),'resume_restores_chosen_mode_across_reopen')
 # Native plus/minus callback output and subsequent encoder selection.
 for i in [5,6,2]:
  old=settings(v);press(v,i)
  isolated(old,settings(v),g,(2 if chosen else 3,))
  check(v.rb(0x4e5)==17 and v.rb(0x4b4)==g,'controls_keep_encoder_bound_to_current_group')
 press(v,1)
 check(not v.modal() and v.focus()==v.rw(0x15b8+4*g),'back_restores_list_focus')

# Every valid TTL value and every manual power/decimal value. Use the original
# formatter's strings/signs as the oracle; no reimplementation of EV encoding.
for decimal in [0,1]:
 v=make(decimal=decimal);open_group(v,0);base=save(v)
 for mode,values in [(0,range(-18,19,2)),(1,range(81))]:
  for n in values:
   restore(v,base);v.wb(0x4c4,mode);v.wb((0x4ef if mode==0 else 0x4d0),n)
   v.call(0x08016cf4);native=[v.text(v.rw(o)) for o in [0x161c,0x1620,0x1624,0x1628]]
   v.function('group_refresh');actual=value(v)
   if mode==0:
    check(actual==native,'all_TTL_signs_and_thirds_match_native',(n,actual,native))
    check(v.call(0x0803616c,0x0806e700,RAM+0xe0000,ord(native[2]),0)==1,'TTL_sign_glyph_exists_in_native_font')
   else:check(actual==native,'all_M_fraction_decimal_labels_match_native',(n,decimal,actual,native))
# Actual slider input in single-lamp page, paused isolation and readback.
for g,mode in product(range(5),[0,1,2]):
 v=make();v.wb(0x4c4+g,mode);open_group(v,g);v.render();t=Touch(v);old=settings(v)
 t.drag(220,210,130);tick(v)
 if mode==2:check(settings(v)==old,'paused_editor_slider_cannot_adjust')
 else:
  isolated(old,settings(v),g,(2 if mode else 3,))
  check(settings(v)!=old,'editor_slider_adjusts_selected_value')
 check(v.rb(0x4e5)==17,'slider_keeps_encoder_scope')

# Single-page slider honors the same native 0.1 / 1/3 M step setting.
for step in [0,1]:
 v=make();v.wb(0x5a,step);open_group(v,0);slider=v.child(v.modal(),7);expected=80
 for n in range(25 if step else 81):
  if n:expected=v.call(0x0801d7fc,0,expected,3 if step else 1)
  v.call(0x0803018c,slider,n,0);v.event(slider,0x1c)
  check(v.rb(0x4d0)==expected,'editor_slider_matches_native_M_step_grid',(step,n,expected,v.rb(0x4d0)))

print('full encoder decoder -> consumer -> GUI',flush=True)
for g,mode in product(range(5),range(3)):
 v=make();ref=make(image=r7)
 for w in [v,ref]:
  w.wb(0x4c4+g,mode);w.wb(0x504+g,mode!=2);w.wb(0x3da,31&~((1<<g) if mode==2 else 0));w.wb(0x4d0+g,40);w.wb(0x4ef+g,0);w.call(0x08016cf4)
 open_group(v,g);v.render()
 ref.call(0x08036af0,ref.rw(0x15b8+4*g));ref.event(ref.rw(0x15b8+4*g),keyboard=True)
 ref.wb(0x4b4,g);ref.wb(0x4e5,17);ref.call(0x08036ab0,ref.rw(0x9e8),1)
 for w in [v,ref]:consumer_stubs(w);poll(w)
 bases=[save(v),save(ref)]
 for direction,batch,step,gui_first in product([0,1],[1,7,20],[0,1],[False,True]):
  for w,s in zip([v,ref],bases):restore(w,s);clean(w);w.wb(0x5a,step)
  before=settings(v);focus=v.focus();m=v.modal()
  # Deliberately stale selector: editor must recover its power/FEC target.
  v.wb(0x4e5,0);v.wb(0x4b4,(g+1)%5)
  detents(v,direction,batch,gui_first);detents(ref,direction,batch,gui_first)
  check(settings(v)==settings(ref),'full_encoder_pipeline_matches_native_group_adjustment',(g,mode,direction,batch,step,gui_first,settings(v),settings(ref)))
  isolated(before,settings(v),g,(2 if mode==1 else 3,) if mode!=2 else ())
  check(v.focus()==focus and v.modal()==m and v.rb(0x4e5)==17 and v.rb(0x4b4)==g,'encoder_never_navigates_or_changes_mode')
  check(v.rw(0x28)==0 and v.rw(0x9e4)==0 and not v.rb(0x16) and not v.rb(0x17),'encoder_deltas_consumed_without_focus_residue')

# SET can never turn the editor into a mode/button navigator. Negative stale
# GUI residual values require a full 32-bit clear, not a halfword clear.
v=make();open_group(v,2);v.render();consumer_stubs(v);poll(v);focus=v.focus()
for delta in [-65537,-20,-1,0,1,20,65537]:
 v.ww(0x9e4,delta);v.ww(0x28,delta);old=settings(v);poll(v)
 check(v.focus()==focus and settings(v)==old and v.rw(0x9e4)==0,'signed_GUI_residual_cannot_navigate')
for _ in range(3):
 v.u.mem_write(0x40020010,struct.pack('<I',0));poll(v)
 v.u.mem_write(0x40020010,struct.pack('<I',0x2000));poll(v)
 detents(v,0,7)
 check(v.focus()==focus and v.rb(0x4e5)==17 and v.rb(0x4c4+2)==1,'SET_then_rotate_still_adjusts_only_value')

# All native SUB pages also retain power-only encoder behavior regardless of
# the last touched/focused native switch or back control.
for page in [0,1,2]:
 v=make(page);v.event(v.rw(0x1550));v.render();consumer_stubs(v);poll(v)
 check(v.function('editor_target')==18,'native_SUB_editor_scope')
 for off in [0x1574,0x15a4,0x1570]:
  v.call(0x08036af0,v.rw(off));focus=v.focus();v.wb(0x4e5,0);old=settings(v)
  detents(v,0,7)
  after=settings(v)
  check(after[0][0]!=old[0][0] and after[0][1]==old[0][1] and after[1:]==old[1:],'SUB_encoder_only_changes_SUB_power')
  check(v.focus()==focus and v.rw(0x156c) and v.rb(0x4e5)==18,'SUB_encoder_never_navigates_controls')

# Real touch mode/pause/+/- followed by the complete physical encoder chain.
for g in range(5):
 v=make();open_group(v,g);v.render();t=Touch(v);consumer_stubs(v);poll(v)
 for x,y in [(150,307),(50,129),(430,129),(240,129),(380,307),(150,307),(380,307)]:
  t.tap(x,y);tick(v);old=settings(v);mode=v.rb(0x4c4+g);focus=v.focus()
  detents(v,0,7)
  isolated(old,settings(v),g,(2 if mode==1 else 3,) if mode!=2 else ())
  check(v.focus()==focus and v.rb(0x4b4)==g and v.rb(0x4e5)==17,'touch_control_then_encoder_stays_on_same_lamp')
  at_limit=mode==2 or (mode==1 and old[2][g]==0) or (mode==0 and old[3][g]==238)
  check((settings(v)==old)==at_limit,'touch_control_then_encoder_respects_pause_and_limits',(g,mode,x,y))

print('guards, fallback, lifecycle',flush=True)
for off,mask in [(0x54b,1),(0x51e,1),(0x342,1),(0x531,1),(0x599,1),(0x59a,1),(0x18,1),(0x31,8),(0x36,2),(0x748,1),(0x74a,1),(0x74b,1)]:
 v=make();open_group(v,0);old=settings(v);v.wb(off,mask)
 for addr in [0x8010924,0x800ba84]:v.call(addr)
 check(settings(v)==old,'locked_or_busy_encoder_does_not_adjust',hex(off))
# Check interrupt-state preservation on all four entry wrappers.
v=make();open_group(v,0)
for primask,address,args in product([0,1],[0x8010924,0x800ba84,0x800b564,0x8029c0c],[None]):
 v.u.reg_write(UC_ARM_REG_PRIMASK,primask)
 v.call(address,*((0,RAM+0xe0000) if address==0x8029c0c else ()))
 check(v.u.reg_read(UC_ARM_REG_PRIMASK)==primask,'rotary_wrappers_preserve_PRIMASK_and_ABI')
# Outside an editor, the original R7 GUI callback remains byte-identical.
for page in range(12):
 a,b=make(0),make(0,image=r7)
 for w in [a,b]:w.wb(0x59f,page);w.wb(0x398,page);w.wb(0x4e5,0)
 for delta,key in product([-3,-1,0,1,3],[0,0x2000]):
  for w in [a,b]:
   w.ww(0x28,delta);w.ww(0x9e4,2);w.u.mem_write(0x40020010,struct.pack('<I',key));w.call(0x8029c0c,0,RAM+0xe0000)
  check(bytes(a.u.mem_read(RAM+0xe0000,16))==bytes(b.u.mem_read(RAM+0xe0000,16)),'non_editor_GUI_fallback_matches_R7')

# Retained R8 RX label / S metrics / outgoing-screen lifetime.
for language in [0,1]:
 a,b=make(0,language=language),make(2,language=language)
 check(a.text(a.rw(0x1554))==b.text(b.rw(0x1554))==('副灯' if language==0 else 'SUB'),'RX_label_matches_hotshoe')
v=make();_,y,_,bottom=v.coords(v.rw(0x1554));_,my,_,mb=v.coords(v.rw(0x15f4))
check((y,bottom)==(my+86,mb+86) and bottom-y+1==29,'S_matches_native_M_group_font_metrics')
for source,target in product(range(3),[0,1,2,5]):
 if source==target:continue
 v=make(source);old=v.rw({0:0x5d8,1:0x600,2:0x604}[source]);row=v.rw(0x1550)
 v.call(0x0801d008,target,6)
 if target!=1:check(v.call(0x0803cdbc,row) and not v.call(0x0803c616,row,1),'SUB_retained_until_whole_screen_exit')
 new=v.rw({0:0x5d8,1:0x600,2:0x604,5:0x5fc}[target]);v.call(0x0803f714,new,0,0,0,1)
 check(not v.call(0x0803cdbc,old),'screen_transition_releases_old_tree')
# Forced page transitions also reclaim an open custom editor before allocating
# another screen; the normal back key is checked separately below.
for target in [0,2,5]:
 v=make();open_group(v,4);m=v.modal();old_root=v.rw(0x600);deleted=[]
 h=v.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:deleted.append(v.args(1)[0]),begin=0x0803ab3c,end=0x0803ab3c)
 v.call(0x0801d008,target,6);v.u.hook_del(h)
 # The new screen may reuse the freed address; is_valid(address) alone is
 # not an object-lifetime assertion once another tree has been allocated.
 check(m in deleted and int.from_bytes(v.u.mem_read(old_root+0x10,4),'little')==0,'page_change_reclaims_custom_editor_first')
v=make(2);row=v.rw(0x1550);a=v.stub(0x8037e78,lambda _:0);b=v.stub(0x8037e84,lambda _:2)
v.event(v.rw(0x604),0xc);v.u.hook_del(a);v.u.hook_del(b)
check(v.rb(0x59f)==5 and v.call(0x803cdbc,row),'RX_power_back_keeps_SUB_until_screen_deletion')
# Repeated native allocation/deletion, physical back key, and Multi transition.
v=make()
for cycle in range(50):
 open_group(v,cycle%5);m=v.modal();press(v,1)
 # The real firmware runs LVGL's animation timer. Frozen-time tests retain
 # queued style transitions and are not a valid heap-leak measurement.
 v.call(0x08041d58,100);v.call(0x080233fc,0)
 if cycle%5==4:
  total=0;a=0x10000538 # Verified TLSF pool first block header.
  while True:
   flags=int.from_bytes(v.u.mem_read(a+4,4),'little');n=flags&~3
   if not n:break
   if not flags&1:total+=n
   a+=n+4
  heap_samples.append(total)
  if cycle>=14:check(total<=heap_samples[1],'heap_usage_bounded_after_native_animation_completion',heap_samples)
 check(not v.call(0x0803cdbc,m),'50_editor_cycles_reclaim_native_heap')
open_group(v,3);a=v.stub(0x8037e78,lambda _:0);b=v.stub(0x8037e84,lambda _:2)
v.event(v.rw(0x600),0xc);v.u.hook_del(a);v.u.hook_del(b)
check(not v.modal() and v.rb(0x59f)==1,'physical_back_closes_editor_first')
open_group(v,2);v.wb(0x4c3,2);tick(v);check(not v.modal(),'Multi_transition_closes_editor')

# Full native LCD framebuffer capture, accumulated across dirty rectangles.
for name,g,mode,n,pause in [('manual',1,1,57,False),('ttl',2,0,-4,False),('paused',3,1,57,True)]:
 v=make(capture=True);v.wb(0x4c4+g,mode);v.wb((0x4d0 if mode else 0x4ef)+g,n);tick(v);open_group(v,g)
 if pause:press(v,4)
 v.render(str(OUT/(name+'.png')))
 # Catch missing control rendering, not just existing object rectangles/text.
 for x0,y0,x1,y1 in [(420,8,463,42),(25,105,75,150),(405,105,455,150),(40,290,270,325),(320,290,440,325)]:
  lit=sum(any(v.framebuffer[(y*480+x)*3:(y*480+x)*3+3]) for y in range(y0,y1) for x in range(x0,x1))
  check(lit>40,'native_single_buffer_preview_contains_all_controls',(name,x0,y0,lit))
report=dict(status='PASS_R9_NATIVE_UI',candidate_sha256=sha(IMAGE),total=sum(counts.values()),counts=dict(counts),heap_samples=heap_samples,hardware_verified=False,
 limits=['Synthetic physical touch/GPIO, explicit polling/consumer order, three wake/beep services replaced','Preview alone uses one framebuffer because hardware double-buffer synchronization is not emulated; functional VMs retain the original display configuration',
 'No panel/touch-controller/RF/physical-device acceptance'])
report['preview_sha256']={name+'.png':sha((OUT/(name+'.png')).read_bytes()) for name in ['manual','ttl','paused']}
(OUT/'R9_UI_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
