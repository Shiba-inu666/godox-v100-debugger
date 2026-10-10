"""R10: real RX badge pixel parity and SUB gestures through native touch polling."""
from probe import *
from input_driver import *
from config import RAW,transform
from itertools import product
from collections import Counter
counts=Counter();OUT=ROOT/'.lab';OUT.mkdir(exist_ok=True);previews=[]

def check(ok,name,detail=None):
 assert ok,(name,detail)
 counts[name]+=1

def make(page=1,image=IMAGE,capture=False):
 v=VM(image,capture=capture);v.wb(0x5a1,0);v.create(page);v.render();clean(v);return v

def state(v):
 return [bytes(v.u.mem_read(RAM+a,n)) for a,n in [(0x4c1,1),(0x4c4,5),(0x4d0,5),(0x4ef,5),(0x504,5),(0x3da,1)]]

def open_group(v,g):
 for code in [1,8,4]:v.event(v.rw(0x15b8+4*g),code)
 check(bool(v.modal()),'group_opens')

def crop(v,obj):
 x,y,right,bottom=v.coords(obj)
 return b''.join(v.framebuffer[(yy*480+x)*3:(yy*480+right+1)*3] for yy in range(y,bottom+1))

def preview(v,name):
 v.render(OUT/name);previews.append(name)

print('RX badge parity',flush=True)
for g in range(1,5):
 ref=VM(RAW,capture=True);ref.wb(0x5a1,0);ref.wb(0x503,g);ref.create(2);ref.render()
 for mode in [0,1,2]:
  v=make(capture=True);v.wb(0x4c4+g,mode);v.call(0x080426bc);open_group(v,g);v.render()
  badge=v.child(v.modal(),0);label=v.child(badge,0)
  check(v.text(label)==ref.text(ref.rw(0x1864))=='MABCD'[g],'native_RX_group_text',(g,mode))
  x,y,r,b=v.coords(badge);check((x,y,r-x+1,b-y+1)==(16,4,44,44),'RX_badge_size_and_header_placement')
  check(crop(v,badge)==crop(ref,ref.rw(0x1860)),'exact_native_RX_badge_pixels',(g,mode))
  check(not v.call(0x0803c616,badge,2),'badge_does_not_intercept_control_touches')
  if mode==1:preview(v,'group_'+ 'MABCD'[g]+'.png')

print('SUB relative drag and isolation',flush=True)
v=make();ref=make();t=Touch(v);y=v.coords(v.rw(0x1550))[1]+40
# The native +/- implementation is the independent oracle; GUI gesture math
# is exercised by the real polling/press/move/release path, not direct callbacks.
for decimal,step,raw,dx in product([0,1],[0,1],range(0,71),[-100,100]):
 v.wb(0x12f0,decimal);v.wb(0x5a,step);v.wb(0x4c0,raw);before=state(v)
 expected=raw
 for _ in range(5):
  if dx<0 and expected>=70:break
  expected=min(70,ref.call(0x0801d7fc,int(dx<0),expected,3))
 t.drag(220,y,dx)
 check(v.rb(0x4c0)==expected,'drag_matches_five_native_SUB_steps',(decimal,step,raw,dx,v.rb(0x4c0),expected))
 check(state(v)==before,'drag_only_changes_SUB_power')
 check(not v.rw(0x156c),'drag_release_does_not_open_SUB_editor')
for raw,dx,expected in [(3,200,0),(67,-200,70),(0,200,0),(70,-200,70)]:
 v.wb(0x4c0,raw);t.drag(220,y,dx)
 check(v.rb(0x4c0)==expected,'SUB_drag_clamps_at_native_1_to_128_limits')
# Drag out and back is still a drag; restore the press value without a tap.
v.wb(0x4c0,30);t.send(220,y,1);t.send(300,y,1);t.send(220,y,1);t.send(220,y,0)
check(v.rb(0x4c0)==30 and not v.rw(0x156c),'out_and_back_restores_power_without_opening')
# A simple tap/jitter opens the normal editor without adjusting the press value.
for jitter in [0,5,-5]:
 v.wb(0x4c0,30);t.send(220,y,1);t.send(220+jitter,y,1);t.send(220+jitter,y,0)
 check(v.rb(0x4c0)==30 and v.rw(0x156c),'tap_and_small_jitter_open_without_adjustment')
 v.event(v.rw(0x1570));v.render()
# OFF and lock/transition/drawer states do not adjust, even with synthetic moves.
for off,value in [(0x4c1,0),(0x54b,1),(0x36,2),(0x599,1),(0x59a,1),(0x398,2),(0x748,1),(0x74a,1),(0x74b,1),(0x496,0)]:
 old=v.rb(off);v.wb(0x4c0,30);v.wb(off,value);t.drag(220,y,100)
 check(v.rb(0x4c0)==30,'disabled_locked_hidden_or_transition_SUB_not_adjusted',hex(off));v.wb(off,old)
t.close()
# Vertical scrolling has exactly the previous R9 list geometry and no change.
r9=transform(RAW,json.loads((ROOT.parent/'r9/evidence/r9.json').read_text()))
check(sha(r9)=='6373f518f30e0582c9fde4c18efc6da81978207bbd8def1781219c2ddd3e24e5','exact_published_R9_reference')
a,b=make(),make(image=r9);ta,tb=Touch(a),Touch(b)
for w,touch in [(a,ta),(b,tb)]:w.wb(0x4c0,30);touch.drag(220,168,0,-100);w.render()
check(a.rb(0x4c0)==b.rb(0x4c0)==30,'vertical_scroll_does_not_change_SUB')
check(not a.rw(0x156c),'vertical_scroll_does_not_open_SUB_editor')
check([a.coords(a.rw(0x15b8+4*g)) for g in range(5)]==[b.coords(b.rw(0x15b8+4*g)) for g in range(5)],'vertical_scroll_matches_R9')
ta.close();tb.close()
# +/- and S-title taps retain the previous behavior with the new observer.
for x in [75,440]:
 a,b=make(),make(image=r9);ta,tb=Touch(a),Touch(b)
 for w,touch in [(a,ta),(b,tb)]:w.wb(0x4c0,30);touch.tap(x,168)
 check(a.rb(0x4c0)==b.rb(0x4c0) and not a.rw(0x156c),'SUB_plus_minus_unchanged')
 ta.close();tb.close()
v=make();t=Touch(v);t.tap(25,168);check(bool(v.rw(0x156c)),'S_title_still_opens_editor');t.close()
# Native SUB editor dragging was already supported in R9 in all three roles.
# Preserve it and check the complete encoder route remains bound to SUB.
print('SUB editors in all roles',flush=True)
for page,dx in product(range(3),[-100,100]):
 a,b=make(page),make(page,image=r9)
 for w in [a,b]:w.event(w.rw(0x1550));w.render();w.wb(0x4c0,30);w.call(0x080426bc);w.render()
 ta,tb=Touch(a),Touch(b);before=state(a)
 for w,touch in [(a,ta),(b,tb)]:touch.drag(220,180,dx);w.call(0x080426bc);w.render()
 check(a.rb(0x4c0)==b.rb(0x4c0)!=30,'native_SUB_editor_drag_parity',(page,dx))
 check(state(a)==before,'SUB_editor_drag_does_not_change_main_or_groups')
 hooks=consumer_stubs(a);old=a.rb(0x4c0);detents(a);check(a.rb(0x4c0)!=old and state(a)==before,'encoder_after_SUB_drag_only_adjusts_SUB')
 for h in hooks:a.u.hook_del(h)
 ta.close();tb.close()
v=make(capture=True);t=Touch(v);t.drag(220,168,100);v.call(0x080426bc);preview(v,'sub_list_drag.png');t.tap(220,168);v.call(0x080426bc);preview(v,'sub_editor.png');t.close()
report=dict(status='PASS_R10_BADGE_AND_SUB_DRAG',candidate_sha256=sha(IMAGE),total=sum(counts.values()),counts=dict(counts),hardware_verified=False,
 preview_sha256={n:sha((OUT/n).read_bytes()) for n in previews},
 reference_R9_sha256=sha(r9),reference_original_sha256=sha(RAW))
(OUT/'R10_CHANGES_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
