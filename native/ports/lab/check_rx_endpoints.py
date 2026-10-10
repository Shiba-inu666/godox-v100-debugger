"""Native RX group endpoints: Canon 0..4, other models 1..5."""
from check_ui import UI
from port_input import consumer_stubs,detents
from port_vm import M
import sys,json,hashlib
name=sys.argv[1];count=0
for group in ([0,4] if name.startswith('V100C') else [1,5]):
 for mode in [0,1]:
  v=UI(name);v.wb(0x5a1,0);v.create(2);v.clean();v.wb(0x503,group);v.wb(0x4c3,mode);v.wb(0x4e5,0);consumer_stubs(v)
  for direction in [0,1]:
   v.wb(0x4d0+group,30);v.wb(0x4eb,0);sub=v.rb(0x4c0);detents(v,direction,7)
   assert (v.rb(0x4d0+group)!=30 if mode else v.rb(0x4eb)!=0),(name,group,mode,direction);count+=1
   assert v.rb(0x4c0)==sub;count+=1
r=dict(status='PASS_RX_GROUP_ENDPOINTS',model=name,checks=count,hardware_verified=False,candidate_sha256=hashlib.sha256((M/name/v.profile['output_filename']).read_bytes()).hexdigest());(M/name/'rx-endpoint-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
