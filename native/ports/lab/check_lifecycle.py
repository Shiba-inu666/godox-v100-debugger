"""Native badge pixels, labels, all-role encoder, guarded state and screen lifetime."""
from check_ui import UI
from port_vm import M,RAM
from port_input import Touch,detents,consumer_stubs,poll
from itertools import product
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PRIMASK
from collections import Counter
import sys,json,hashlib
name=sys.argv[1];counts=Counter()
def check(ok,label,detail=None):
 assert ok,(name,label,detail)
 counts[label]+=1

def make(page=1,stock=False,language=0):
 v=UI(name)
 if stock:v.u.mem_write(0x8008000,v.data)
 v.wb(0x5a1,0);v.wb(0x12fa,language);v.create(page);v.clean();v.render();return v

def crop(v,obj):
 x,y,r,b=v.coords(obj)
 return b''.join(v.framebuffer[(yy*480+x)*3:(yy*480+r+1)*3] for yy in range(y,b+1))

for g in range(0 if name.startswith('V100C') else 1,5):
 letter=('ABCDE' if name.startswith('V100C') else 'MABCD')[g]
 ref=make(2,stock=True);ref.event(ref.rw(0x1860));popup=ref.rw(0x1868)
 found=False
 for i in range(2,7):
  obj=ref.child(popup,i)
  if obj and ref.text(ref.child(obj,0))==letter:ref.event(obj);found=True;break
 check(found,'native_group_picker_contains_letter',letter)
 # Choosing a group focuses its RX selector; move focus to the native value
 # field before comparing the badge's normal (unfocused) visual state.
 ref.callf(0x8036af0,ref.rw(0x17e4));ref.callf(0x8041d58,300);ref.callf(0x80233fc,0);ref.render()
 check(ref.rb(0x503)==g,'native_group_index',letter)
 for mode in [0,1,2]:
  v=make();v.wb(0x4c4+g,mode);v.callf(0x80426bc);v.open(g);v.render();badge=v.child(v.modal(),0)
  check(v.text(v.child(badge,0))==ref.text(ref.rw(0x1864))==letter,'badge_text',letter)
  check(crop(v,badge)==crop(ref,ref.rw(0x1860)),'exact_native_badge_pixels',(g,mode))
  if mode==1:v.render(M/name/('group_'+letter+'.png'))
print(name,'native badges',sum(counts.values()),flush=True)
for language in [0,1]:
 a,b=make(0,language=language),make(2,language=language)
 check(a.text(a.rw(0x1554))==b.text(b.rw(0x1554))==('副灯' if language==0 else 'SUB'),'RX_and_hotshoe_label')
v=make();_,y,_,b=v.coords(v.rw(0x1554));_,gy,_,gb=v.coords(v.rw(0x15f4))
check((y,b)==(gy+86,gb+86) and b-y+1==29,'S_native_group_cap_height')
for page in range(3):
 v=make(page);v.event(v.rw(0x1550));v.render();t=Touch(v);hooks=consumer_stubs(v)
 for dx in [-100,100]:
  v.wb(0x4c0,30);old=v.state();t.drag(220,180,dx);v.callf(0x80426bc)
  check(v.rb(0x4c0)!=30 and v.state()[1:]==old[1:],'SUB_modal_drag_isolated',page)
  for off in [0x1574,0x15a4,0x1570]:
   v.callf(0x8036af0,v.rw(off));v.wb(0x4c0,30);v.wb(0x4e5,0);old=v.state();detents(v,0,7)
   check(v.rb(0x4c0)!=30 and v.state()[0][1]==old[0][1] and v.state()[1:]==old[1:] and v.rb(0x4e5)==18,'SUB_encoder_fixed_after_control_focus',page)
 t.close()
 for h in hooks:v.u.hook_del(h)
# The legacy direct main encoder covers each native RX group including Canon A and E.
for page,g,mode,direction in product([0,2],range(5),[0,1],[0,1]):
 if not name.startswith('V100C') and g==0 and page==2:continue
 v=make(page);v.wb(0x503,g);v.wb(0x4c3,mode);v.wb(0x4c4+g,mode);v.wb(0x4b4,g);v.wb(0x4e5,0);v.wb(0x4d0+g,30);v.wb(0x4ef+g,0);v.wb(0x4eb,0)
 if page==0:v.wb(0x4d0,30);v.wb(0x4ef,0)
 hooks=consumer_stubs(v);before=v.state();oldfec=v.rb(0x4eb);detents(v,direction,7);after=v.state();target=g if page==2 else 0;field=2 if mode else 3
 check((after[field][target]!=before[field][target]) if mode else v.rb(0x4eb)!=oldfec,'main_encoder_current_RX_group',(page,g,mode,direction))
 check(after[0]==before[0],'main_encoder_preserves_SUB')
 for h in hooks:v.u.hook_del(h)
print(name,'all-role rotary',sum(counts.values()),flush=True)
for off,mask in [(0x54b,1),(0x51e,1),(0x342,1),(0x531,1),(0x599,1),(0x59a,1),(0x18,1),(0x31,8),(0x36,2),(0x748,1),(0x74a,1),(0x74b,1)]:
 v=make();v.open(0);old=v.state();v.wb(off,mask)
 for a in [0x8010924,0x800ba84]:v.callf(a)
 check(v.state()==old,'locked_busy_no_encoder_change',hex(off))
v=make();v.open(0)
for primask,a in product([0,1],[0x8010924,0x800ba84,0x800b564,0x8029c0c]):
 v.u.reg_write(UC_ARM_REG_PRIMASK,primask);v.callf(a,*((0,RAM+0xe0000) if a==0x8029c0c else ()));check(v.u.reg_read(UC_ARM_REG_PRIMASK)==primask,'PRIMASK_preserved')
for source,target in product(range(3),[0,1,2,5]):
 if source==target:continue
 v=make(source);old=v.rw({0:0x5d8,1:0x600,2:0x604}[source]);row=v.rw(0x1550);v.callf(0x801d008,target,6)
 if target!=1:check(v.callf(0x803cdbc,row) and not v.callf(0x803c616,row,1),'SUB_retained_during_exit')
 new=v.rw({0:0x5d8,1:0x600,2:0x604,5:0x5fc}[target]);v.callf(0x803f714,new,0,0,0,1);check(not v.callf(0x803cdbc,old),'old_screen_freed')
for target in [0,2,5]:
 v=make();v.open(4);m=v.modal();deleted=[];a=v.flash(0x803ab3c);h=v.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:deleted.append(v.args(1)[0]),begin=a,end=a)
 v.callf(0x801d008,target,6);v.u.hook_del(h);check(m in deleted,'modal_freed_before_page_change')
v=make(2);row=v.rw(0x1550);hs=[v.stubf(0x8037e78,lambda _:0),v.stubf(0x8037e84,lambda _:2)];v.event(v.rw(0x604),0xc)
check(v.rb(0x59f)==5 and v.callf(0x803cdbc,row),'RX_power_key_retains_SUB')
v=make()
for i in range(30):
 v.open(i%5);m=v.modal();v.close();v.callf(0x8041d58,100);v.callf(0x80233fc,0);check(not v.callf(0x803cdbc,m),'repeated_editor_free')
v.open(2);v.wb(0x4c3,2);v.callf(0x80426bc);check(not v.modal(),'Multi_closes_editor')
r=dict(status='PASS_LIFECYCLE_AND_BADGES',model=name,checks=sum(counts.values()),counts=dict(counts),hardware_verified=False,candidate_sha256=hashlib.sha256((M/name/v.profile['output_filename']).read_bytes()).hexdigest())
(M/name/'lifecycle-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
