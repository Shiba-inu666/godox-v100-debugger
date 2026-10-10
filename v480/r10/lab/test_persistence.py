"""Cold-boot RX group persistence through native records and ARM flash stores.

Only the MCU size register, flash W1C/erase effects and RF wake I/O are modeled.
The original serializer, comparer, rotating writer, program-word instructions,
boot scanner and deserializer execute. Each reboot creates entirely fresh RAM.
This cannot establish retention, brownout atomicity or erase timing on hardware.
"""
from vm import *
from input_driver import clean,Touch
from collections import Counter
from itertools import product
IMAGE=(ROOT/'.build/candidate.bin').read_bytes()
OUT=ROOT/'.lab';OUT.mkdir(exist_ok=True);counts=Counter()
def check(ok,name,detail=None):
 assert ok,(name,detail)
 counts[name]+=1
class Device:
 def __init__(self,image=IMAGE,bank=None,capacity=0x400):
  self.v=v=VM(image);self.capacity=capacity
  self.base=0x81ff000 if capacity in [0x800,0xc00] else 0x80ff000
  self.words=[];self.erases=[]
  v.u.mem_map(0x1fff7000,0x1000);v.u.mem_write(0x1fff7a20,struct.pack('<I',capacity<<16))
  v.u.mem_write(self.base,bank if bank is not None else b'\xff'*4096)
  # FLASH_SR is write-one-to-clear; ordinary emulated RAM cannot implement it.
  v.stub(0x802bba0,lambda a:v.u.mem_write(0x40023c0c,bytes(4)) or 0)
  v.stub(0x802bbbc,self.erase)
  v.stub(0x801e424) # Native Receiver notification/wake service, not persistence.
  v.u.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=self.base,end=self.base+4095)
  v.call(0x8015570)
 def erase(self,a):
  assert a[0]==self.base
  self.erases.append(a[0]);self.v.u.mem_write(self.base,b'\xff'*4096);return 0
 def write(self,u,access,a,size,value,data):
  assert size==4 and self.base+0x800<=a<self.base+0x1000
  assert u.reg_read(UC_ARM_REG_PC)==0x802bcd2 # Actual native program-word store.
  assert u.reg_read(UC_ARM_REG_PRIMASK)==1
  old=int.from_bytes(u.mem_read(a,4),'little');assert old&value==value
  self.words.append((a,value))
 def bank(self):return bytes(self.v.u.mem_read(self.base,4096))
 def reboot(self,image=IMAGE):return Device(image,self.bank(),self.capacity)
 def service(self,n=1):
  for _ in range(n):self.v.call(0x80121a0)
 def flush(self):self.v.wb(0x33b,1);self.service()
 def record(self):
  off=0x800+self.v.rb(0x339)*80
  return self.bank()[off:off+80]
 def receiver(self,mode=1):
  self.v.wb(0x51b,mode);self.v.wb(0x5fd,0);self.v.create(2);clean(self.v)
 def choose(self,g,physical=False):
  v=self.v
  if physical:
   t=Touch(v);v.render()
   box=v.coords(v.rw(0x18d8));t.tap((box[0]+box[2])//2,(box[1]+box[3])//2);v.render()
   box=v.coords(v.rw(0x18e4+4*(g-1)));t.tap((box[0]+box[2])//2,(box[1]+box[3])//2);t.close()
  else:
   for c in [1,4]:v.event(v.rw(0x18d8),c)
   for c in [1,4]:v.event(v.rw(0x18e4+4*(g-1)),c)
  assert v.rb(0x55b)==g and not v.rw(0x18e0)

def restored(d,g,role,mode):
 v=d.v
 check(v.rb(0x55b)==g and v.rb(0x352)==g+9 and v.rb(0x137e)==g+9,'cold_boot_group_radio_and_colour_agree',(g,role,mode))
 check(v.rb(0x350)==role and v.rb(0x51b)&3==mode,'cold_boot_preserves_role_and_mode')
 v.create(2)
 check(v.text(v.rw(0x18dc))=='ABCDE'[g-1],'cold_boot_native_RX_badge_matches_saved_group')

print('Original reproduction and compatibility',flush=True)
old=Device(RAW);old.receiver();old.choose(5);old.service()
check(old.v.rb(0xff5)==1,'original_touch_choice_does_not_request_commit')
old.flush();old.v.wb(0x350,0);old.flush()
check(old.reboot(RAW).v.rb(0x55b)==1,'original_non_RX_boot_resets_saved_E_to_A')
check(old.reboot().v.rb(0x55b)==5,'candidate_reads_existing_native_record_without_migration')

print('A-E touch choice, TTL/M, all boot roles and flash capacities',flush=True)
for capacity,g,mode in product([0x400,0x800,0xc00],range(1,6),[0,1]):
 d=Device(capacity=capacity);d.receiver(mode);v=d.v
 # Establish settings to prove selection preserves unrelated serialized fields.
 v.wb(0x351,7);v.wb(0x137d,7);v.wb(0x353,42);v.wb(0x137f,42)
 v.u.mem_write(RAM+0x528,bytes([10,20,30,40,50,60]));v.wb(0x543,6);d.flush()
 before=d.record();n=len(d.words);d.choose(g,physical=True);d.service()
 after=d.record()
 check(after[9]==g and after[70]==g+9,'confirmed_touch_choice_commits_native_record')
 check(all(a==b for i,(a,b) in enumerate(zip(before,after)) if i not in [9,70]),'group_commit_preserves_other_record_bytes')
 check(len(d.words)-n==(0 if g==1 else 20),'one_native_record_per_changed_confirmed_group')
 n=len(d.words);d.service(60);d.choose(g);d.service()
 check(len(d.words)==n,'idle_and_same_group_do_not_write_again')
 for role in [0,3,4]:
  v.wb(0x350,role);v.wb(0x137c,role);d.flush();r=d.reboot();restored(r,g,role,mode)
  check(r.v.rb(0x351)==7 and r.v.rb(0x353)==42 and r.v.rb(0x543)==6 and bytes(r.v.u.mem_read(RAM+0x528,6))==bytes([10,20,30,40,50,60]),'cold_boot_preserves_channel_ID_FEC_and_each_power')

print('Native encoder selection and commit guards',flush=True)
for direction in [0,1]:
 d=Device();d.receiver();v=d.v;d.flush();n=len(d.words)
 v.call(0x803767c,v.rw(0x18d8));v.event(v.rw(0x18d8),keyboard=True)
 check(v.rb(0x53d)==24,'native_SET_selects_RX_group')
 for _ in range(3):v.call([0x8010850,0x800b9f0][direction]);d.service()
 check(len(d.words)==n,'active_group_encoder_edit_does_not_force_flash_write')
 # Native second SET confirms the selected parameter and leaves edit mode.
 v.event(v.rw(0x18d8),keyboard=True)
 check(v.rb(0x53d)==0,'native_SET_confirms_RX_group')
 g=v.rb(0x55b);d.service();check(d.record()[9]==g,'confirmed_encoder_choice_commits');restored(d.reboot(),g,4,1)
for role,g,chooser in [(0,3,0),(3,3,0),(4,0,0),(4,6,0),(4,255,0),(4,3,RAM+0xf000)]:
 d=Device();v=d.v;v.wb(0x350,role);v.wb(0x55b,g);v.ww(0x18e0,chooser);n=len(d.words);d.service()
 check(len(d.words)==n,'save_request_scope_guard',(role,g,chooser))

print('Original debounce and shutdown remain native',flush=True)
d=Device();d.receiver();d.flush();v=d.v;v.wb(0x543,8);v.call(0x8019f38);n=len(d.words)
d.service(49);check(len(d.words)==n,'ordinary_parameters_retain_native_debounce')
d.service();check(len(d.words)==n+20 and d.record()[5]==8,'native_debounce_eventually_commits_other_parameters')
v.wb(0x543,10);v.u.mem_write(RAM+0x33c,struct.pack('<H',1));d.service()
check(d.record()[5]==10,'native_shutdown_flush_counter_still_commits')

print('Record rotation and cold boot with only flash carried over',flush=True)
for capacity in [0x400,0x800]:
 d=Device(capacity=capacity);d.receiver();d.flush();initial=d.v.rb(0x339);n=len(d.words);erases=len(d.erases)
 for i in range(60):
  g=(i+1)%5+1;d.v.wb(0x55b,g);d.v.wb(0x352,g+9);d.v.wb(0x137e,g+9);d.service()
  check(d.v.rb(0x339)==(initial+i+1)%25,'native_25_record_wear_rotation')
  r=d.reboot();check(r.v.rb(0x55b)==g,'latest_group_survives_record_rotation_and_cold_boot')
 check(len(d.words)==n+60*20 and len(d.erases)==erases+2,'native_rotation_program_and_erase_counts')

print('Saved-byte bounds across every value and boot role',flush=True)
seed=Device();bank=bytearray(seed.bank())
for role,g in product([0,3,4],range(256)):
 b=bytearray(bank);b[0x806]=role;b[0x809]=g
 r=Device(bank=bytes(b));expected=g if 1<=g<=5 else 1
 check(r.v.rb(0x55b)==expected and r.v.rb(0x352)==expected+9 and r.v.rb(0x137e)==expected+9,'native_group_bounds_retained_for_all_saved_bytes',(role,g))
for capacity in [0x400,0x800,0xc00]:
 d=Device(capacity=capacity)
 check(d.v.rb(0x55b)==1 and d.record()[9]==1,'blank_flash_keeps_factory_A_default')
 d.v.wb(0x55b,5);d.v.call(0x80089e8)
 check(d.v.rb(0x55b)==1 and d.reboot().v.rb(0x55b)==1,'factory_reset_still_clears_remembered_group')
report=dict(status='PASS_V480_R10B_RX_GROUP_PERSISTENCE',candidate_sha256=hashlib.sha256(IMAGE).hexdigest(),total=sum(counts.values()),counts=dict(counts),hardware_verified=False,flash_model='MCU capacity, W1C status and 4 KiB erase-window effects substituted; native ARM serializer, comparer, flash word stores, record rotation and cold-boot scanner execute',limits=['No physical NVM retention or timing measurement','Power loss during the native flash write/erase remains unverified; no atomicity guarantee'])
(OUT/'RX_PERSISTENCE_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
