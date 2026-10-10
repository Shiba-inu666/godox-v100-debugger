"""R10 native gestures, editor controls, display, full encoder input and lifecycle.

Runs complete candidate instructions/LVGL. Only physical touch/GPIO samples,
LCD transfer and three wake/beep services are substituted. No hardware claim.
"""
from vm import *
from patcher import transform,sha
IMAGE=(ROOT/'.build/candidate.bin').read_bytes()
from input_driver import *
from itertools import product
from collections import Counter

from unicorn.arm_const import UC_ARM_REG_PRIMASK
counts=Counter();heap_samples=[];OUT=ROOT/'.lab';OUT.mkdir(exist_ok=True)

def check(ok,label,detail=None):
 assert ok,(label,detail)
 counts[label]+=1

def make(page=1,image=IMAGE,language=0,decimal=0,capture=False):
 v=VM(image,capture=capture);v.wb(0x5fd,0);v.wb(0x1372,language);v.wb(0x1368,decimal)
 v.create(page);v.render();clean(v);return v

def tick(v):v.call(0x8043240);v.render()
def save(v):return [bytes(v.u.mem_read(a,n)) for a,n in [(RAM,0x100000),(0x10000000,0x10000)]]
def restore(v,s):
 for a,b in zip([RAM,0x10000000],s):v.u.mem_write(a,b)
def settings(v):return [bytes(v.u.mem_read(RAM+a,n)) for a,n in [(0x518,2),(0x51c,5),(0x528,5),(0x547,5),(0x55c,5),(0x436,1)]]
def isolated(before,after,g,kinds=()):
 for k,(a,b) in enumerate(zip(before,after)):
  for i,(x,y) in enumerate(zip(a,b)):
   if k==5:assert (x^y)&~(1<<g)==0
   elif (k,i) not in [(kind,g) for kind in kinds]:assert x==y,(k,i,x,y,g,kinds)
def open_group(v,g):
 row=v.rw(0x1630+4*g)
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
 v.u.mem_write(RAM+0xe0000,struct.pack('<hh',x,y));return v.call(0x8039194,r,RAM+0xe0000)
def row_y(v,g):
 row=v.rw(0x1630+4*g);v.call(0x803ec44,row,0);v.render();return v.coords(row)[1]+40

print('native gestures',flush=True)
v2=transform(RAW)
for g,mode in product(range(5),range(3)):
 v=make();ref=make(image=v2)
 for w in [v,ref]:
  w.wb(0x51c+g,mode);w.wb(0x55c+g,mode!=2);w.call(0x80168b4);w.call(0x8016e14)
 y,ry=row_y(v,g),row_y(ref,g)
 touch,rt=Touch(v),Touch(ref)
 # Actual LVGL long-press timer emits events 5/6 and no short-click.
 for _ in range(3):
  touch.hold(150,y);rt.hold(150,ry)
  check(settings(v)==settings(ref),'native_long_press_three_mode_cycle_parity',(g,mode))
  check(not v.modal(),'long_release_does_not_open_editor')
 # Drag input goes through the original native slider callback.
 for dx in [80,-80]:
  touch.drag(150,y,dx);rt.drag(150,ry,dx)
  check(settings(v)==settings(ref),'native_swipe_power_FEC_OFF_parity',(g,mode,dx))
  check(not v.modal(),'swipe_release_does_not_open_editor')
 # +/- continue to use their native hit targets/actions.
 for x in ([65,290] if v.rb(0x51c+g)!=2 else []):
  touch.tap(x,y);rt.tap(x,ry)
  check(settings(v)==settings(ref) and not v.modal(),'list_plus_minus_remain_native',(g,mode,x,hex(v.modal()),settings(v),settings(ref)))
 # Both group badge and value open this group by a real short tap.
 for x in [20,150]:
  before=settings(v);touch.tap(x,y);v.render()
  check(bool(v.modal()) and v.text(v.child(v.child(v.modal(),0),0) if g else v.child(v.modal(),0))=='MABCD'[g],'real_short_tap_opens_correct_group',(g,mode,x))
  check(settings(v)==before,'short_tap_does_not_change_power_or_mode')
  touch.tap(290,20);v.render();check(not v.modal(),'touch_back_returns_to_list')
 touch.close();rt.close()

# A drag that returns to its start still must not be mistaken for a tap.
v=make();t=Touch(v);t.send(150,70,1);t.send(180,70,1);t.send(150,70,1);t.send(150,70,0)
check(not v.modal(),'out_and_back_drag_is_not_a_tap')
# Vertical list scrolling remains native, including the later C/D rows.
v=make();ref=make(image=v2);t,rt=Touch(v),Touch(ref)
t.drag(150,170,0,-90);rt.drag(150,170,0,-90)
v.render();ref.render()
check([v.coords(v.rw(0x1630+4*g)) for g in range(5)]==[ref.coords(ref.rw(0x1630+4*g)) for g in range(5)],'vertical_scroll_geometry_matches_v2')
check(not v.modal(),'vertical_scroll_does_not_open_editor')

print('editor controls and native display',flush=True)
for g,initial,decimal in product(range(5),range(3),[0,1]):
 v=make(decimal=decimal);v.wb(0x51c+g,initial);v.wb(0x55c+g,initial!=2);v.wb(0x436,31&~((1<<g) if initial==2 else 0));tick(v)
 open_group(v,g);v.render();m=v.modal()
 check(v.function('editor_target')==17 and v.rb(0x50c)==g,'fixed_encoder_scope_is_current_group')
 check(v.coords(v.child(m,3))[2]<v.coords(v.child(m,4))[0],'mode_button_left_of_pause')
 for i,x,y in [(1,290,20),(2,160,91),(3,100,210),(4,250,210),(5,30,91),(6,290,91),(7,160,155)]:
  check(hit(v,v.rw(0x664),x,y)==v.child(m,i),'editor_native_touch_target',(i,g))
 if initial==2:press(v,4)
 mode=v.rb(0x51c+g)
 for _ in range(2):
  before=settings(v);press(v,3);mode=1-mode
  check(v.rb(0x51c+g)==mode and text(v,3)==('M' if mode else 'TTL'),'TTL_M_switch_readback')
  isolated(before,settings(v),g,(1,4))
 before=settings(v);press(v,4)
 check(v.rb(0x51c+g)==2 and not v.rb(0x55c+g) and not v.rb(0x436)&(1<<g) and text(v,4)=='OFF','pause_updates_mode_enable_mask')
 isolated(before,settings(v),g,(1,4))
 paused=settings(v);stored=value(v)
 for i in [2,5,6]:press(v,i)
 for address in [0x8010850,0x800b9f0]:v.call(address)
 check(settings(v)==paused and value(v)==stored,'paused_encoder_buttons_leave_settings_unchanged')
 press(v,3)
 check(v.rb(0x51c+g)==2 and not v.rb(0x55c+g),'TTL_M_preselection_keeps_group_paused')
 chosen=1-mode;press(v,1);open_group(v,g);press(v,4)
 check(v.rb(0x51c+g)==chosen and v.rb(0x55c+g) and v.rb(0x436)&(1<<g),'resume_restores_chosen_mode_across_reopen')
 # Native plus/minus callback output and subsequent encoder selection.
 for i in [5,6,2]:
  old=settings(v);press(v,i)
  isolated(old,settings(v),g,(2 if chosen else 3,))
  check(v.rb(0x53d)==17 and v.rb(0x50c)==g,'controls_keep_encoder_bound_to_current_group')
 press(v,1)
 check(not v.modal() and v.focus()==v.rw(0x1630+4*g),'back_restores_list_focus')

# Every valid TTL value and every manual power/decimal value. Use the original
# formatter's strings/signs as the oracle; no reimplementation of EV encoding.
for decimal in [0,1]:
 v=make(decimal=decimal);open_group(v,0);base=save(v)
 for mode,values in [(0,range(-18,19,2)),(1,range(81))]:
  for n in values:
   restore(v,base);v.wb(0x51c,mode);v.wb((0x547 if mode==0 else 0x528),n)
   v.call(0x8016e14);native=[v.text(v.rw(o)) for o in [0x1694,0x1698,0x169c,0x16a0]]
   v.function('group_refresh');actual=value(v)
   if mode==0:
    check(actual==native,'all_TTL_signs_and_thirds_match_native',(n,actual,native))
    check(v.call(0x8036cf8,0x80652d8,RAM+0xe0000,ord(native[2]),0)==1,'TTL_sign_glyph_exists_in_native_font')
   else:check(actual==native,'all_M_fraction_decimal_labels_match_native',(n,decimal,actual,native))
# Actual slider input in single-lamp page, paused isolation and readback.
for g,mode in product(range(5),[0,1,2]):
 v=make();v.wb(0x51c+g,mode);open_group(v,g);v.render();t=Touch(v);old=settings(v)
 t.drag(150,155,95);tick(v)
 if mode==2:check(settings(v)==old,'paused_editor_slider_cannot_adjust')
 else:
  isolated(old,settings(v),g,(2 if mode else 3,))
  check(settings(v)!=old,'editor_slider_adjusts_selected_value')
 check(v.rb(0x53d)==17,'slider_keeps_encoder_scope')

# Single-page slider honors the same native 0.1 / 1/3 M step setting.
for step in [0,1]:
 v=make();v.wb(0x5e,step);open_group(v,0);slider=v.child(v.modal(),7);expected=80
 for n in range(25 if step else 81):
  if n:expected=v.call(0x801dbf8,0,expected,3 if step else 1)
  v.call(0x8030d18,slider,n,0);v.event(slider,0x1c)
  check(v.rb(0x528)==expected,'editor_slider_matches_native_M_step_grid',(step,n,expected,v.rb(0x528)))

print('full encoder decoder -> consumer -> GUI',flush=True)
for g,mode in product(range(5),range(3)):
 v=make();ref=make(image=v2)
 for w in [v,ref]:
  w.wb(0x51c+g,mode);w.wb(0x55c+g,mode!=2);w.wb(0x436,31&~((1<<g) if mode==2 else 0));w.wb(0x528+g,40);w.wb(0x547+g,0);w.call(0x8016e14)
 open_group(v,g);v.render()
 ref.call(0x803767c,ref.rw(0x1630+4*g));ref.event(ref.rw(0x1630+4*g),keyboard=True)
 ref.wb(0x50c,g);ref.wb(0x53d,17);ref.call(0x803763c,ref.rw(0xa60),1)
 for w in [v,ref]:consumer_stubs(w);poll(w)
 bases=[save(v),save(ref)]
 for direction,batch,step,gui_first in product([0,1],[1,7,20],[0,1],[False,True]):
  for w,s in zip([v,ref],bases):restore(w,s);clean(w);w.wb(0x5e,step)
  before=settings(v);focus=v.focus();m=v.modal()
  # Deliberately stale selector: editor must recover its power/FEC target.
  v.wb(0x53d,0);v.wb(0x50c,(g+1)%5)
  detents(v,direction,batch,gui_first);detents(ref,direction,batch,gui_first)
  check(settings(v)==settings(ref),'full_encoder_pipeline_matches_native_group_adjustment',(g,mode,direction,batch,step,gui_first,settings(v),settings(ref)))
  isolated(before,settings(v),g,(2 if mode==1 else 3,) if mode!=2 else ())
  check(v.focus()==focus and v.modal()==m and v.rb(0x53d)==17 and v.rb(0x50c)==g,'encoder_never_navigates_or_changes_mode')
  check(v.rw(0x28)==0 and v.rw(0xa5c)==0 and not v.rb(0x16) and not v.rb(0x17),'encoder_deltas_consumed_without_focus_residue')
  if mode!=2 and direction==0 and batch==7 and step==0 and not gui_first:
   v.call(0x8043240)
   native=[v.text(v.rw(o+28*g)) for o in [0x1694,0x1698,0x169c,0x16a0]]
   check(value(v)==native,'encoder_value_refreshes_through_real_main_tick',(g,mode,value(v),native))


# SET can never turn the editor into a mode/button navigator. Negative stale
# GUI residual values require a full 32-bit clear, not a halfword clear.
v=make();open_group(v,2);v.render();consumer_stubs(v);poll(v);focus=v.focus()
for delta in [-65537,-20,-1,0,1,20,65537]:
 v.ww(0xa5c,delta);v.ww(0x28,delta);old=settings(v);poll(v)
 check(v.focus()==focus and settings(v)==old and v.rw(0xa5c)==0,'signed_GUI_residual_cannot_navigate')
for _ in range(3):
 v.u.mem_write(0x40020810,struct.pack('<I',0));poll(v)
 v.u.mem_write(0x40020810,struct.pack('<I',0x20));poll(v)
 detents(v,0,7)
 check(v.focus()==focus and v.rb(0x53d)==17 and v.rb(0x51c+2)==1,'SET_then_rotate_still_adjusts_only_value')

# Real touch mode/pause/+/- followed by the complete physical encoder chain.
for g in range(5):
 v=make();open_group(v,g);v.render();t=Touch(v);consumer_stubs(v);poll(v)
 for x,y in [(100,210),(30,91),(290,91),(160,91),(250,210),(100,210),(250,210)]:
  t.tap(x,y);tick(v);old=settings(v);mode=v.rb(0x51c+g);focus=v.focus()
  detents(v,0,7)
  isolated(old,settings(v),g,(2 if mode==1 else 3,) if mode!=2 else ())
  check(v.focus()==focus and v.rb(0x50c)==g and v.rb(0x53d)==17,'touch_control_then_encoder_stays_on_same_lamp')
  at_limit=mode==2 or (mode==1 and old[2][g]==0) or (mode==0 and old[3][g]==238)
  check((settings(v)==old)==at_limit,'touch_control_then_encoder_respects_pause_and_limits',(g,mode,x,y))

print('guards, fallback, lifecycle',flush=True)
for off,mask in [(0x5a3,1),(0x576,1),(0x358,1),(0x589,1),(0x5f5,1),(0x5f6,1),(0x18,1),(0x31,8),(0x3a,2),(0x7ae,1),(0x7b0,1),(0x7b1,1)]:
 v=make();open_group(v,0);old=settings(v);v.wb(off,mask)
 for addr in [0x8010850,0x800b9f0]:v.call(addr)
 check(settings(v)==old,'locked_or_busy_encoder_does_not_adjust',hex(off))
# Check interrupt-state preservation on all four entry wrappers.
v=make();open_group(v,0)
for primask,address,args in product([0,1],[0x8010850,0x800b9f0,0x800b4f0,0x802a79c],[None]):
 v.u.reg_write(UC_ARM_REG_PRIMASK,primask)
 v.call(address,*((0,RAM+0xe0000) if address==0x802a79c else ()))
 check(v.u.reg_read(UC_ARM_REG_PRIMASK)==primask,'rotary_wrappers_preserve_PRIMASK_and_ABI')
# Outside an editor, the original v2 GUI callback remains byte-identical.
for page in range(12):
 a,b=make(0),make(0,image=v2)
 for w in [a,b]:w.wb(0x5fb,page);w.wb(0x3af,page);w.wb(0x53d,0)
 for delta,key in product([-3,-1,0,1,3],[0,0x20]):
  for w in [a,b]:
   w.ww(0x28,delta);w.ww(0xa5c,2);w.u.mem_write(0x40020810,struct.pack('<I',key));w.call(0x802a79c,0,RAM+0xe0000)
  check(bytes(a.u.mem_read(RAM+0xe0000,16))==bytes(b.u.mem_read(RAM+0xe0000,16)),'non_editor_GUI_fallback_matches_v2')

# Forced page transitions also reclaim an open custom editor before allocating
# another screen; the normal back key is checked separately below.
for target in [0,2,5]:
 v=make();open_group(v,4);m=v.modal();old_root=v.rw(0x664);deleted=[]
 h=v.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:deleted.append(v.args(1)[0]),begin=0x803b6cc,end=0x803b6cc)
 v.call(0x801d3ec,target,6);v.u.hook_del(h)
 # The new screen may reuse the freed address; is_valid(address) alone is
 # not an object-lifetime assertion once another tree has been allocated.
 check(m in deleted and int.from_bytes(v.u.mem_read(old_root+0x10,4),'little')==0,'page_change_reclaims_custom_editor_first')
# Repeated native allocation/deletion, physical back key, and Multi transition.
v=make()
for cycle in range(50):
 open_group(v,cycle%5);m=v.modal();press(v,1)
 # The real firmware runs LVGL's animation timer. Frozen-time tests retain
 # queued style transitions and are not a valid heap-leak measurement.
 v.call(0x80428dc,100);v.call(0x8023ad4,0)
 if cycle%5==4:
  total=0;a=0x2004d56c # V480 TLSF pool base 0x2004d034 + control size 0x538.
  while True:
   flags=int.from_bytes(v.u.mem_read(a+4,4),'little');n=flags&~3
   if not n:break
   assert 4<=n<65536 and a+n+4<0x2005d034
   if not flags&1:total+=n
   a+=n+4
  heap_samples.append(total)
  if cycle>=14:check(total<=heap_samples[1],'heap_usage_bounded_after_native_animation_completion',heap_samples)
 check(not v.call(0x803d94c,m),'50_editor_cycles_reclaim_native_heap')
open_group(v,3);a=v.stub(0x8038a08,lambda _:0);b=v.stub(0x8038a14,lambda _:2)
v.event(v.rw(0x664),0xc);v.u.hook_del(a);v.u.hook_del(b)
check(not v.modal() and v.rb(0x5fb)==1,'physical_back_closes_editor_first')
open_group(v,2);v.wb(0x51b,2);tick(v);check(not v.modal(),'Multi_transition_closes_editor')

# Full native LCD framebuffer capture, accumulated across dirty rectangles.
for name,g,mode,n,pause in [('manual',1,1,57,False),('ttl',2,0,-4,False),('paused',3,1,57,True)]:
 v=make(capture=True);v.wb(0x51c+g,mode);v.wb((0x528 if mode else 0x547)+g,n);tick(v);open_group(v,g)
 if pause:press(v,4)
 v.render(str(OUT/(name+'.png')))
 # Catch missing control rendering, not just existing object rectangles/text.
 for x0,y0,x1,y1 in [(277,4,310,37),(10,70,48,111),(271,70,310,111),(30,193,172,228),(220,193,296,228)]:
  lit=sum(any(v.pixels[(y*320+x)*3:(y*320+x)*3+3]) for y in range(y0,y1) for x in range(x0,x1))
  check(lit>40,'native_single_buffer_preview_contains_all_controls',(name,x0,y0,lit))
report=dict(status='PASS_V480_R10_NATIVE_UI',candidate_sha256=sha(IMAGE),total=sum(counts.values()),counts=dict(counts),heap_samples=heap_samples,hardware_verified=False,
 limits=['Synthetic physical touch/GPIO, explicit polling/consumer order, three wake/beep services replaced','Preview alone uses one framebuffer because hardware double-buffer synchronization is not emulated; functional VMs retain the original display configuration',
 'No panel/touch-controller/RF/physical-device acceptance'])
report['preview_sha256']={name+'.png':sha((OUT/(name+'.png')).read_bytes()) for name in ['manual','ttl','paused']}
(OUT/'R10_UI_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
