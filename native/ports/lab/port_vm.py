"""Exact-model offline VM. Logical operation keys retain the existing F lab API."""
from pathlib import Path
import json,struct,sys,os
from machine import *
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'.lab';BASE=0x08008000
class PortVM(StockVM):
 def __init__(self,name):
  super().__init__();self.name=name;self.profile=json.loads((ROOT/'profiles'/(name+'.json')).read_text());p=self.profile
  self.data=Path(os.environ.get('V100_PORT_ORIGINAL',str(ROOT.parents[1]/'firmware/upstream-v100-2026-10-10'/p['original_filename']))).read_bytes()
  import hashlib
  assert len(self.data)==p['size'] and hashlib.sha256(self.data).hexdigest()==p['original_sha256'],'Exact original required'
  self.u.mem_write(BASE,self.data);self.func={int(a,16):int(b,16) for a,b in p['lab_abi']['functions'].items()};self.globals={int(a,16):int(b,16) for a,b in p['lab_abi']['ram'].items()};self.shift=p['lab_abi']['ui_ram_shift']
  boot=p['startup']
  for reg,val in [(UC_ARM_REG_R0,int(boot['source'],16)),(UC_ARM_REG_R1,int(boot['destination'],16)),(UC_ARM_REG_R2,boot['size']),(UC_ARM_REG_LR,STOP|1),(UC_ARM_REG_SP,SP)]:self.u.reg_write(reg,val)
  self.u.emu_start(int(boot['entry'],16)|1,STOP,count=100000);assert self.u.reg_read(UC_ARM_REG_PC)==STOP
  for a in [0x08038684,0x0803ec78,0x0803ecd8]:self.callf(a)
  for a,b in [(0x496,1),(0x544,1),(0x4c0,30),(0x4c1,1),(0x4c3,1),(0x5a1,1),(0x12fa,1),(0x503,1)]:self.setf(a,b)
  for off,data in [(0x4d0,bytes([40,30,20,10,0,77])),(0x4c4,bytes([1]*5)),(0x504,bytes([1]*5))]:self.u.mem_write(RAM+self.ram(off),data)
 def flash(self,a):
  try:return self.func[a&~1]|(a&1)
  except KeyError:raise ValueError('Unmapped operation '+hex(a))
 def address(self,a):return self.flash(a)
 def ram(self,off):
  if off in self.globals:return self.globals[off]
  if 0x598<=off<=0x1c00:return off+self.shift
  for a,n in [(0x4c4,5),(0x4d0,6),(0x4ef,5),(0x504,5)]:
   if a<=off<a+n:return self.globals[a]+off-a
  try:return self.globals[off]
  except KeyError:raise ValueError('Unmapped field '+hex(off))
 def setf(self,off,value):super().wb(self.ram(off),value)
 def getf(self,off):return super().rw(self.ram(off))
 def callf(self,a,*args):return self.call(self.flash(a),*args,count=100000000)
 def render(self,path=None):
  import zlib
  from unicorn import UC_HOOK_CODE
  drv=int.from_bytes(self.u.mem_read(self.getf(0xa8c),4),"little")
  buf=int.from_bytes(self.u.mem_read(drv+12,4),"little")
  self.u.mem_write(buf+4,bytes(4));self.u.mem_write(buf+8,bytes(self.u.mem_read(buf,4)))
  frames=[]
  def flush(u,a,s,d):
   driver,area,pixels=self.args(3);box=struct.unpack("<4h",u.mem_read(area,8));x0,y0,x1,y1=box
   frames.append((box,bytes(u.mem_read(pixels,(x1-x0+1)*(y1-y0+1)*2))))
   u.reg_write(UC_ARM_REG_PC,self.address(0x08031646)|1)
  a=self.address(0x080250fc);h=self.u.hook_add(UC_HOOK_CODE,flush,begin=a,end=a)
  try:self.callf(0x08020b24,int.from_bytes(self.u.mem_read(self.getf(0xa8c)+4,4),"little"))
  finally:self.u.hook_del(h)
  rgb=getattr(self,"framebuffer",bytearray(480*360*3))
  for (x0,y0,x1,y1),data in frames:
   for j,value in enumerate(struct.unpack("<"+"H"*(len(data)//2),data)):
    x=x0+j%(x1-x0+1);y=y0+j//(x1-x0+1)
    if 0<=x<480 and 0<=y<360:
     k=(y*480+x)*3;rgb[k:k+3]=bytes((((value>>11)&31)*255//31,((value>>5)&63)*255//63,(value&31)*255//31))
  def chunk(kind,data):return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data))
  scan=b"".join(b"\0"+rgb[y*1440:(y+1)*1440] for y in range(360))
  self.framebuffer=rgb
  if path:Path(path).write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">2I5B",480,360,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(scan))+chunk(b"IEND",b""))
  return len(frames)
 def create(self,page):
  for a,b in [(0x59f,page),(0x398,page),(0x33c,{0:0,1:3,2:4}[page]),(0x599,0),(0x59a,0)]:self.setf(a,b)
  self.callf({0:0x0804a548,1:0x0804c75c,2:0x0804cc88}[page])
  root=self.getf({0:0x5d8,1:0x600,2:0x604}[page]);self.callf(0x0803175c,root);self.callf(0x08036e08,self.getf(0x9e8),0)
  assert root and self.callf(0x0803cdbc,root)==1
  return root
