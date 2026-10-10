from port_vm import M
from check_ui import UI
from port_input import Touch,detents,consumer_stubs,clean
from pathlib import Path
from itertools import product
import sys,json,hashlib
name=sys.argv[1];count=0

def make(page=1,stock=False):
 v=UI(name)
 if stock:v.u.mem_write(0x08008000,v.data)
 v.wb(0x5a1,0);v.wb(0x12fa,0);v.create(page);v.render();v.clean();return v

def check(ok,label,detail=None):
 global count
 assert ok,(name,label,detail)
 count+=1

def y(v,g):
 row=v.rw(0x15b8+4*g);v.callf(0x0803e0b4,row,0);v.render();return v.coords(row)[1]+40

v,ref=make(),make(stock=True);t,rt=Touch(v),Touch(ref)
for g in range(5):
 yy,ry=y(v,g),y(ref,g)
 for mode in [0,1,2]:
  for w in [v,ref]:w.wb(0x4c4+g,mode);w.wb(0x504+g,int(mode!=2));w.callf(0x0801687c);w.callf(0x08016cf4)
  for k in range(3):
   t.hold(220,yy);rt.hold(220,ry)
   check(v.state()==ref.state(),'long press parity',(g,mode,k));check(not v.modal(),'long press does not open')
  for dx in [-80,80]:
   t.drag(220,yy,dx);rt.drag(220,ry,dx);check(v.state()==ref.state(),'native group drag parity',(g,mode,dx));check(not v.modal(),'drag does not open')
  old=v.state();t.tap(220,yy);v.render();check(bool(v.modal()),'real short tap opens',(g,mode));check(v.state()==old,'short tap isolation')
  if v.rb(0x4c4+g)==2:t.tap(380,307)
  for k in range(2):
   prev=v.rb(0x4c4+g);t.tap(150,307);check(v.rb(0x4c4+g)==1-prev,'touch mode switch')
  old=v.state();current=v.rb(0x4c4+g);t.drag(220,210,80);check(v.state()[2 if current else 3][g]!=old[2 if current else 3][g],'editor drag')
  hooks=consumer_stubs(v);old=v.state();detents(v)
  check(v.state()[2 if current else 3][g]!=old[2 if current else 3][g],'full encoder route after drag')
  for h in hooks:v.u.hook_del(h)
  t.tap(380,307);old=v.state();t.drag(220,210,100);check(v.state()==old,'paused slider blocked')
  t.tap(440,25);v.render();check(not v.modal(),'touch back')
  # Keep the original reference synchronized for the next independent sample.
  for w in [v,ref]:
   w.wb(0x4c4+g,1);w.wb(0x504+g,1);w.wb(0x4d0+g,30);w.wb(0x4ef+g,0);w.wb(0x3da,31)
   w.callf(0x0801687c);w.callf(0x08016cf4)
  yy,ry=y(v,g),y(ref,g)
t.close();rt.close()
print(name,'native group touch',count,flush=True)
v=make();t=Touch(v);yy=v.coords(v.rw(0x1550))[1]+40
for power,dx in product([0,3,10,30,67,70],[-100,100]):
 v.wb(0x4c0,power);old=v.state();expected=power
 for k in range(5):
  if dx<0 and expected>=70:break
  expected=min(70,ref.callf(0x0801d7fc,int(dx<0),expected,3))
 t.drag(220,yy,dx);check(v.rb(0x4c0)==expected,'SUB relative drag',(power,dx,v.rb(0x4c0),expected));check(v.state()[1:]==old[1:],'SUB isolation');check(not v.rw(0x156c),'SUB drag release no modal')
t.tap(220,yy);v.render();check(bool(v.rw(0x156c)),'SUB tap opens');hooks=consumer_stubs(v);old=v.rb(0x4c0);detents(v,1);check(v.rb(0x4c0)!=old,'SUB fixed encoder')
for h in hooks:v.u.hook_del(h)
t.close()
r=dict(status='PASS_NATIVE_TOUCH',model=name,checks=count,hardware_verified=False,candidate_sha256=hashlib.sha256((M/name/v.profile['output_filename']).read_bytes()).hexdigest());(M/name/'partial-touch-results.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
