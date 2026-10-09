from revision_vm import *
from itertools import product
from collections import Counter
counts=Counter();samples=[];raw=RAW
offs=[0x1578,0x157c,0x1580,0x1584,0x1588,0x158c,0x1594,0x159c,0x15a4,0x15ac]
def snap(vm):
 vm.render();return {hex(o):dict(rect=vm.coords(vm.rw(o)),**({'text':vm.text(vm.rw(o))} if o in offs[:4] else {})) for o in offs}
def format(vm):vm.call(0x0801249c,*[vm.rw(o) for o in [0x1578,0x157c,0x1580,0x1584,0x1588,0x158c,0x1590]],0x200004c0)
for page,language,decimal in product([1,2],[0,1],[0,1]):
 ref=NativeVM(image=raw);v=RevisionVM()
 for vm,p in [(ref,0),(v,page)]:
  vm.wb(0x5a1,0);vm.wb(0x12fa,language);vm.wb(0x12f0,decimal);vm.create(p);vm.event(vm.rw(0x1550))
 assert snap(v)==snap(ref);counts['modal_initial_exact_hotshoe_geometry']+=1
 for power in [x for x in range(71) if x%10 in [0,3,7]]:
  for vm in [ref,v]:vm.wb(0x4c0,power);format(vm)
  a,b=snap(ref),snap(v);assert a==b,(page,language,decimal,power,a,b)
  bar=b['0x158c']['rect']
  for o in offs[:4]:
   z=b[hex(o)]['rect'];assert z[1]>=0 and (z[2]<z[0] or z[3]<bar[1]),(o,z,bar)
  counts['all_SUB_values_exact_hotshoe_no_visual_overlap']+=1
  if power==40 and not decimal:samples.append(dict(page=page,language=language,geometry=b))
  for vm in [ref,v]:vm.wb(0x386,255);vm.call(0x080426bc)
  assert snap(v)==snap(ref);counts['full_tick_preserves_SUB_modal_geometry']+=1
 for target in [0x1594,0x159c,0x15a4]:
  ref.event(ref.rw(target));v.event(v.rw(target))
  for vm in [ref,v]:vm.call(0x080426bc)
  assert snap(v)==snap(ref);counts['native_touch_plus_minus_switch_geometry']+=1
 for vm in [ref,v]:vm.event(vm.rw(0x1570));vm.event(vm.rw(0x1550))
 assert snap(v)==snap(ref);counts['close_reopen_geometry']+=1
r=dict(status='PASS_R4_MODAL_EXACT_HOTSHOE_GEOMETRY',candidate_sha256=sha(IMAGE),total=sum(counts.values()),counts=dict(counts),samples=samples,hardware_verified=False,root_cause='Generic formatter sets center Y: Wi-Off -66, RX -20, Sender 0; inherited SUB modal bar stays Y182..189. R4 restores Wi-Off font/anchors only for owned SUB modal.',limits=['Actual LVGL objects, labels and native events execute','Geometry/render layout validated; incomplete native framebuffer model not treated as LCD acceptance'])
(ROOT/'analysis/MODAL_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
