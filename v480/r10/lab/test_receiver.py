"""R10a: native RX direct rotary, isolation, display and exact badge pixels."""
from vm import *
from input_driver import *
from patcher import sha
from itertools import product
from collections import Counter
IMAGE=(ROOT/'.build/candidate.bin').read_bytes()
OUT=ROOT/'.lab';OUT.mkdir(exist_ok=True);counts=Counter();previews=[]
def check(ok,name,detail=None):
 assert ok,(name,detail)
 counts[name]+=1
def make(mode=1,g=1,image=IMAGE,capture=False,page=2):
 v=VM(image,capture=capture);v.wb(0x5fd,0);v.wb(0x51b,mode);v.wb(0x55b,g);v.create(page);v.render();clean(v);return v
def snap(v):return bytes(v.u.mem_read(RAM+0x500,0x70))
def value(v):return [v.text(v.rw(o)) for o in [0x1860,0x1864,0x1868,0x186c]]
def save(v):return bytes(v.u.mem_read(RAM,0x100000))
def restore(v,s):v.u.mem_write(RAM,s)
def crop(v,o):
 x,y,r,b=v.coords(o)
 return b''.join(v.pixels[(yy*320+x)*3:(yy*320+r+1)*3] for yy in range(y,b+1))
def preview(v,name):v.render(OUT/name);previews.append(name)

print('Exact native RX badge pixels',flush=True)
for g in range(1,5):
 ref=make(g=g,image=RAW,capture=True)
 for mode in [0,1,2]:
  v=make(page=1,capture=True);v.wb(0x51c+g,mode)
  for code in [1,8,4]:v.event(v.rw(0x1630+4*g),code)
  v.render();badge=v.child(v.modal(),0)
  check(v.text(v.child(badge,0))==ref.text(ref.rw(0x18dc))=='MABCD'[g],'native_RX_badge_text')
  check(v.coords(badge)==(12,2,55,45),'native_44x44_badge_header_geometry')
  check(crop(v,badge)==crop(ref,ref.rw(0x18d8)),'exact_RX_badge_shape_font_colour_pixels',(g,mode))
  # LVGL native hit-test must pass through the decorative badge.
  v.u.mem_write(RAM+0xe0000,struct.pack('<hh',30,20))
  check(v.call(0x8039194,v.rw(0x664),RAM+0xe0000)!=badge,'badge_is_not_interactive')
  if mode==1:preview(v,'group_'+'MABCD'[g]+'.png')

print('RX all native parameter values and groups',flush=True)
for g,mode in product(range(1,6),[0,1]):
 a,b=make(mode,g),make(mode,g,image=RAW);bases=[save(a),save(b)]
 for step,n,direction in product([0,1],range(-18,19,2) if mode==0 else range(81),[0,1]):
  for w,s in zip([a,b],bases):
   restore(w,s);w.wb(0x5e,step);w.wb(0x543 if mode==0 else 0x528+g,n)
  before=snap(a);b.wb(0x53d,6 if mode==0 else 2)
  address=[0x8010850,0x800b9f0][direction]
  for w in [a,b]:w.call(address)
  b.wb(0x53d,0)
  check(snap(a)==snap(b),'all_values_match_explicit_native_RX_adjustment',(g,mode,step,n,direction))
  after=snap(a);parameter=(0x543 if mode==0 else 0x528+g)-0x500
  check(all(x==y for i,(x,y) in enumerate(zip(before,after)) if i!=parameter),'no_other_group_or_mode_changes')
  check(a.rb(0x53d)==0 and a.u.reg_read(UC_ARM_REG_PRIMASK)==0,'temporary_selection_and_PRIMASK_restored')

print('RX full GPIO -> consumer -> GUI and displayed values',flush=True)
for g,mode in product(range(1,6),[0,1]):
 a,b=make(mode,g),make(mode,g,image=RAW)
 for w in [a,b]:consumer_stubs(w);poll(w)
 b.call(0x803767c,b.rw(0x185c));b.event(b.rw(0x185c),keyboard=True)
 b.wb(0x53d,6 if mode==0 else 2);b.call(0x803763c,b.rw(0xa60),1)
 bases=[save(a),save(b)]
 for direction,batch,step,gui_first in product([0,1],[1,7,20],[0,1],[False,True]):
  for w,s in zip([a,b],bases):restore(w,s);w.wb(0x5e,step);w.wb(0x528+g,40);w.wb(0x543,0)
  before=snap(a);focus=a.focus()
  for w in [a,b]:detents(w,direction,batch,gui_first)
  b.wb(0x53d,0)
  check(snap(a)==snap(b),'full_RX_pipeline_native_parameter_parity',(g,mode,direction,batch,step,gui_first))
  check(a.focus()==focus and not a.rb(0x53d) and not a.rw(0x28) and not a.rw(0xa5c),'RX_rotation_does_not_navigate')
  check(snap(a)!=before,'RX_rotation_changes_requested_parameter')

# Every visible TTL sign/third must equal the original hotshoe formatter.
a=make(0)
for n in range(-18,19,2):
 a.wb(0x543,n);a.call(0x8043240)
 # Independent native formatter oracle in its own RX object tree; the test
 # changes only the oracle page byte, never the candidate's runtime page.
 ref=make(0,image=RAW);ref.wb(0x543,n);ref.wb(0x5fb,0)
 ref.call(0x801f424,ref.rw(0x1860),ref.rw(0x1864),ref.rw(0x1868),ref.rw(0x186c),0,ref.rw(0x1874),0,RAM+0x543)
 check(value(a)==value(ref),'RX_TTL_display_uses_native_numeric_sign_and_thirds',(n,value(a),value(ref)))
 check(a.rb(0x5fb)==2 and a.rb(0x350)==4,'display_does_not_spoof_page_or_role')
for mode,name in [(0,'receiver_ttl.png'),(1,'receiver_manual.png')]:
 v=make(mode,capture=True);consumer_stubs(v);poll(v);detents(v,0,7);v.call(0x8043240);preview(v,name)

print('RX scope guards, explicit selection, decoder residue, ABI',flush=True)
a=make();base=save(a)
guards=[(0x5fb,1,1),(0x3af,1,1),(0x350,3,1),(0x53d,1,1),(0x53d,14,1),(0x53d,24,1),(0x51b,2,1),(0x51b,3,1),(0x55b,0,1),(0x55b,6,1),(0x668,0,4),(0x18e0,RAM+0xf000,4),(0x1bb4,RAM+0xf100,4),(0x15e4,RAM+0xf200,4)]
guards += [(off,1,1) for off in [0x5a3,0x576,0x358,0x589,0x5f5,0x5f6,0x18,0x7ae,0x7b0,0x7b1]]+[(0x31,8,1),(0x3a,2,1)]
for off,n,size in guards:
 restore(a,base);(a.ww if size==4 else a.wb)(off,n)
 check(a.function('receiver_target')==0,'RX_excluded_state_has_no_direct_target',hex(off))
# Real native modal chooser and explicit ZOOM editing remain operational.
for obj_off,selector in [(0x18bc,1),(0x18a0,14),(0x18d8,24)]:
 a,b=make(),make(image=RAW)
 for w in [a,b]:w.call(0x803767c,w.rw(obj_off));w.event(w.rw(obj_off),keyboard=True)
 check(a.rb(0x53d)==b.rb(0x53d)==selector,'explicit_RX_selection_stays_native',hex(obj_off))
 for direction in [0,1]:
  for w in [a,b]:w.call([0x8010850,0x800b9f0][direction])
  check(snap(a)==snap(b),'selected_ZOOM_mode_group_adjustment_matches_stock')
# Touch opens native group / ZOOM chooser with selector zero; neither may
# accidentally use direct power while the chooser is on screen.
for obj_off,modal_off in [(0x18d8,0x18e0),(0x18bc,0x1bb4)]:
 a,b=make(),make(image=RAW)
 for w in [a,b]:w.event(w.rw(obj_off),1);w.event(w.rw(obj_off),4);consumer_stubs(w);poll(w)
 check(bool(a.rw(modal_off)) and not a.rb(0x53d) and not a.function('receiver_target'),'native_RX_chooser_blocks_direct_rotary')
 for direction in [0,1]:
  before=snap(a)
  for w in [a,b]:detents(w,direction,7)
  check(snap(a)==snap(b) and a.rb(0x543)==before[0x43] and bytes(a.u.mem_read(RAM+0x528,6))==before[0x28:0x2e],'RX_chooser_rotary_does_not_adjust_power')
for mode in [0,1]:
 a=make(mode)
 for primask,direction in product([0,1],[0,1]):
  a.u.reg_write(UC_ARM_REG_PRIMASK,primask);a.call([0x8010850,0x800b9f0][direction])
  check(a.u.reg_read(UC_ARM_REG_PRIMASK)==primask and not a.rb(0x53d),'RX_adjust_preserves_entry_PRIMASK_and_ABI')
 for delta,primask in product([-65537,-1,0,1,65537],[0,1]):
  a.ww(0x28,delta);a.u.reg_write(UC_ARM_REG_PRIMASK,primask)
  for phase in [0,1,3,2,0]:a.u.mem_write(0x40020410,struct.pack('<I',phase));a.call(0x800b4f0)
  check(a.rw(0x28)==delta&0xffffffff and a.u.reg_read(UC_ARM_REG_PRIMASK)==primask,'RX_decoder_preserves_preexisting_GUI_delta_and_PRIMASK')
report=dict(status='PASS_V480_R10A_RX_AND_BADGE',candidate_sha256=sha(IMAGE),total=sum(counts.values()),counts=dict(counts),hardware_verified=False,reference_original_sha256=sha(RAW),preview_sha256={n:sha((OUT/n).read_bytes()) for n in previews})
(OUT/'RX_BADGE_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
