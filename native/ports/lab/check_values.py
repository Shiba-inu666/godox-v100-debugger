"""All native TTL/manual display encodings and both manual slider step grids."""
from check_ui import UI
from port_vm import M
import sys,json,hashlib
name=sys.argv[1];count=0
for decimal in [0,1]:
 v=UI(name);v.wb(0x5a1,0);v.wb(0x12f0,decimal);v.create(1);v.clean();v.open(0)
 for mode,values in [(0,range(-18,19,2)),(1,range(81))]:
  for n in values:
   v.wb(0x4c4,mode);v.wb(0x4ef if mode==0 else 0x4d0,n&255);v.callf(0x8016cf4)
   native=[v.text(v.rw(o)) for o in [0x161c,0x1620,0x1624,0x1628]];v.function('group_refresh');field=v.child(v.modal(),2);actual=[v.text(v.child(field,i)) for i in range(4)]
   assert actual==native,(name,decimal,mode,n,actual,native);count+=1
for step in [0,1]:
 v=UI(name);v.wb(0x5a1,0);v.create(1);v.clean();v.wb(0x5a,step);v.open(0);slider=v.child(v.modal(),7);expected=80
 for n in range(25 if step else 81):
  if n:expected=v.callf(0x801d7fc,0,expected,3 if step else 1)
  v.callf(0x803018c,slider,n,0);v.event(slider,0x1c)
  assert v.rb(0x4d0)==expected,(name,step,n,expected,v.rb(0x4d0));count+=1
r=dict(status='PASS_NATIVE_VALUE_FORMATS',model=name,checks=count,hardware_verified=False,candidate_sha256=hashlib.sha256((M/name/v.profile['output_filename']).read_bytes()).hexdigest());(M/name/'value-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
