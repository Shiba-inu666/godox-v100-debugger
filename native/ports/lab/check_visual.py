"""Capture full native LCD output and require visible controls, not only hitboxes."""
from check_ui import UI
from port_vm import M
import sys,json,hashlib
name=sys.argv[1];count=0;previews={}
for label,mode in [('manual',1),('ttl',0),('paused',2)]:
 v=UI(name);v.wb(0x5a1,0);v.create(1);v.clean();v.render();v.wb(0x4c4+1,mode);v.wb(0x4d0+1,57);v.wb(0x4ef+1,252);v.open(1)
 path=M/name/(label+'.png');v.render(path)
 for x0,y0,x1,y1 in [(420,8,463,42),(25,105,75,150),(405,105,455,150),(40,290,270,325),(320,290,440,325)]:
  lit=sum(any(v.framebuffer[(y*480+x)*3:(y*480+x)*3+3]) for y in range(y0,y1) for x in range(x0,x1))
  assert lit>40,(name,label,'control not visible',x0,y0,lit);count+=1
 previews[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
r=dict(status='PASS_VISIBLE_CONTROLS',model=name,checks=count,hardware_verified=False,candidate_sha256=hashlib.sha256((M/name/v.profile['output_filename']).read_bytes()).hexdigest(),preview_sha256=previews)
(M/name/'visual-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
