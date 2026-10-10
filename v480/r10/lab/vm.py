"""Execute actual V480F ARM/LVGL instructions; only physical I/O is substituted."""
from pathlib import Path
import struct,json,hashlib,sys
from unicorn import *
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT.parent))
from patcher import verify_original
RAW=(REPO/'firmware/V480F_V1.03.bin').read_bytes();verify_original(RAW)
RAM=0x20000000;SP=RAM+0xf0000;STOP=0x09000000
REGS=[UC_ARM_REG_R0+i for i in range(13)]
class VM:
 def __init__(self,image=None,capture=False):
  self.u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);self.u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  for addr,size in [(0x08000000,0x200000),(RAM,0x100000),(0x10000000,0x10000),(STOP,0x1000),(0x40020000,0x10000)]:self.u.mem_map(addr,size)
  self.u.mem_write(0x8008000,image or RAW)
  for reg,val in [(UC_ARM_REG_R0,0x808cab0),(UC_ARM_REG_R1,RAM),(UC_ARM_REG_R2,0xbb0),(UC_ARM_REG_LR,STOP|1),(UC_ARM_REG_SP,SP)]:self.u.reg_write(reg,val)
  self.u.emu_start(0x80081e9,STOP,count=100000);assert self.u.reg_read(UC_ARM_REG_PC)==STOP
  for a in [0x8039214,0x803f808,0x803f85c]:self.call(a)
  self.wb(0x5fd,1);self.wb(0x1372,1);self.wb(0x55b,1);self.wb(0x51b,1)
  self.u.mem_write(RAM+0x528,bytes([40,30,20,10,0,77]));self.u.mem_write(RAM+0x51c,bytes([1]*5));self.u.mem_write(RAM+0x55c,bytes([1]*5))
  self.manifest=json.loads((ROOT/'.build/ui.json').read_text()) if image and hashlib.sha256(image).hexdigest()==json.loads((ROOT/'.build/ui.json').read_text())['candidate_sha256'] else {}
  self.capture=capture
  if capture:
   drv=int.from_bytes(self.u.mem_read(self.rw(0xb04),4),'little');buf=int.from_bytes(self.u.mem_read(drv+12,4),'little')
   self.u.mem_write(buf+4,bytes(4));self.u.mem_write(buf+8,bytes(self.u.mem_read(buf,4)))
 def wb(self,o,v):self.u.mem_write(RAM+o,bytes([v&255]))
 def ww(self,o,v):self.u.mem_write(RAM+o,struct.pack('<I',v&0xffffffff))
 def rb(self,o):return self.u.mem_read(RAM+o,1)[0]
 def rw(self,o):return struct.unpack('<I',self.u.mem_read(RAM+o,4))[0]
 def call(self,addr,*args,count=100000000):
  for i,r in enumerate(REGS):self.u.reg_write(r,0x11220000+i)
  for r,v in zip(REGS[:4],args):self.u.reg_write(r,v&0xffffffff)
  if len(args)>4:self.u.mem_write(SP,struct.pack('<'+'I'*len(args[4:]),*[a&0xffffffff for a in args[4:]]))
  self.u.reg_write(UC_ARM_REG_SP,SP);self.u.reg_write(UC_ARM_REG_LR,STOP|1);self.u.reg_write(UC_ARM_REG_XPSR,0x1000000)
  self.u.emu_start(addr|1,STOP,count=count)
  assert self.u.reg_read(UC_ARM_REG_PC)==STOP,(hex(addr),hex(self.u.reg_read(UC_ARM_REG_PC)))
  assert self.u.reg_read(UC_ARM_REG_SP)==SP
  for i in range(4,12):assert self.u.reg_read(REGS[i])==0x11220000+i,(hex(addr),i)
  return self.u.reg_read(UC_ARM_REG_R0)
 def args(self,n=8):return ([self.u.reg_read(r) for r in REGS[:4]]+list(struct.unpack('<4I',self.u.mem_read(self.u.reg_read(UC_ARM_REG_SP),16))))[:n]
 def ret(self,v=0):self.u.reg_write(UC_ARM_REG_R0,v&0xffffffff);self.u.reg_write(UC_ARM_REG_PC,self.u.reg_read(UC_ARM_REG_LR))
 def stub(self,addr,fn=None):
  def hook(u,a,s,d):self.ret(0 if fn is None else fn(self.args()))
  return self.u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
 def create(self,page=1):
  self.wb(0x5fb,page);self.wb(0x3af,page);self.wb(0x350,{0:0,1:3,2:4}[page]);self.wb(0x5f5,0);self.wb(0x5f6,0)
  self.call({0:0x804afb8,1:0x804d1b0,2:0x804d6e8}[page]);r=self.rw({0:0x63c,1:0x664,2:0x668}[page]);self.call(0x80322e8,r);self.call(0x8037994,self.rw(0xa60),0);return r
 def function(self,name,*args):return self.call(self.manifest['symbols'][name],*args)
 def modal(self):return self.function('group_modal') if self.manifest else 0
 def event(self,o,code=4,keyboard=False):return self.call(0x8036b54,o,code,self.rw(0xa58 if keyboard else 0xa54))
 def focus(self):return self.call(0x803779c,self.rw(0xa60))
 def child(self,o,i):return self.call(0x803c094,o,i)
 def coords(self,o):return struct.unpack('<4h',self.u.mem_read(o+0x14,8))
 def text(self,o):return bytes(self.u.mem_read(int.from_bytes(self.u.mem_read(o+0x24,4),'little'),100)).split(b'\0')[0].decode('utf-8')
 def render(self,path=None):
  frames=[]
  def flush(u,a,s,d):
   driver,area,pixels=self.args(3);box=struct.unpack('<4h',u.mem_read(area,8));x0,y0,x1,y1=box
   frames.append((box,bytes(u.mem_read(pixels,(x1-x0+1)*(y1-y0+1)*2))));u.reg_write(UC_ARM_REG_PC,0x80321d3)
  h=self.u.hook_add(UC_HOOK_CODE,flush,begin=0x8025c14,end=0x8025c14)
  try:self.call(0x80211b0,struct.unpack('<I',self.u.mem_read(self.rw(0xb04)+4,4))[0])
  finally:self.u.hook_del(h)
  if not self.capture:
   assert path is None
   return len(frames)
  import zlib
  rgb=getattr(self,'pixels',bytearray(320*240*3));self.pixels=rgb
  for (x0,y0,x1,y1),data in frames:
   for j,value in enumerate(struct.unpack('<'+'H'*(len(data)//2),data)):
    x=x0+j%(x1-x0+1);y=y0+j//(x1-x0+1)
    if 0<=x<320 and 0<=y<240:
     k=(y*320+x)*3;rgb[k:k+3]=bytes((((value>>11)&31)*255//31,((value>>5)&63)*255//63,(value&31)*255//31))
  def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
  scan=b''.join(b'\0'+rgb[y*960:(y+1)*960] for y in range(240))
  if path:Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',320,240,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b''))
  return len(frames)
if __name__=='__main__':
 v=VM();r=v.create();print(hex(r),v.coords(r));print('display',hex(v.rw(0xb04)))
 for g in range(5):print(g,hex(v.rw(0x1630+4*g)),v.coords(v.rw(0x1630+4*g)))
