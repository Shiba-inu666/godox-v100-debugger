"""Excluded Multi/HSS mode dispatch must retain stock GPIO and radio requests."""
from fire_probe import FireVM
from port_vm import M
import sys,json,hashlib
name=sys.argv[1];s,v=FireVM(name,False),FireVM(name,True);count=0
for mode in [2,3,16,17]:
 for role in [3,4]:
  out=[]
  for w in [s,v]:
   w.setup(role,mode);w.wf(0x54c,5);w.wf(0x4fd,10);w.wf(0x512,10);out.append(w.runf(0x8020534 if role==4 else 0x800b1ec))
  a,b=out
  assert a['gpio']==b['gpio'],(name,mode,role,'GPIO');count+=1
  assert a['radio_serial_hex']==b['radio_serial_hex'],(name,mode,role,'RF');count+=1
  assert a['main_trigger_set_requests']==b['main_trigger_set_requests'],(name,mode,role,'main');count+=1
r=dict(status='PASS_EXCLUDED_DISPATCH',model=name,checks=count,hardware_verified=False,candidate_sha256=hashlib.sha256(v.image).hexdigest())
(M/name/'excluded-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
