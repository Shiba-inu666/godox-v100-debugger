from pathlib import Path
import sys,json,struct
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parent/'lab'))
from native_vm import NativeVM,UC_HOOK_CODE,UC_ARM_REG_PC
from config import sha
IMAGE=(ROOT/'.build/candidate.bin').read_bytes()
class VM(NativeVM):
 def __init__(self,image=IMAGE,capture=False):
  super().__init__(image=image);self.capture=capture
  if capture:
   # The lab does not emulate LCD double-buffer synchronization. Preview only:
   # use one buffer, preserving the original full-refresh display flags.
   drv=int.from_bytes(self.u.mem_read(self.rw(0xa8c),4),"little")
   buf=int.from_bytes(self.u.mem_read(drv+12,4),"little")
   self.u.mem_write(buf+4,bytes(4))
   self.u.mem_write(buf+8,bytes(self.u.mem_read(buf,4)))
  self.manifest=json.loads((ROOT/'.build/ui.json').read_text())
 def child(self,obj,i):return self.call(0x0803b504,obj,i)
 def modal(self):return self.function('group_modal')
 def render(self,path=None):
     frames=[]
     def flush(u,a,s,d):
         driver,area,pixels=self.args(3)
         box=struct.unpack('<4h',u.mem_read(area,8));x0,y0,x1,y1=box
         frames.append((box,bytes(u.mem_read(pixels,(x1-x0+1)*(y1-y0+1)*2))))
         # Finish through stock lv_disp_flush_ready; only LCD transfer is substituted.
         u.reg_write(UC_ARM_REG_PC,0x08031647)
     h=self.u.hook_add(UC_HOOK_CODE,flush,begin=0x080250fc,end=0x080250fc)
     try:self.call(0x08020b24,struct.unpack('<I',self.u.mem_read(self.rw(0xa8c)+4,4))[0])
     finally:self.u.hook_del(h)
     self.last_frames=[box for box,_ in frames]
     if not self.capture:
         assert path is None,"Create VM(capture=True) for LCD previews"
         return len(frames)
     import zlib
     rgb=getattr(self,"framebuffer",bytearray(480*360*3))
     self.framebuffer=rgb
     for (x0,y0,x1,y1),data in frames:
         for j,value in enumerate(struct.unpack('<'+'H'*(len(data)//2),data)):
             x=x0+j%(x1-x0+1);y=y0+j//(x1-x0+1)
             if 0<=x<480 and 0<=y<360:
                 k=(y*480+x)*3;rgb[k:k+3]=bytes((((value>>11)&31)*255//31,((value>>5)&63)*255//63,(value&31)*255//31))
     def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
     scan=b''.join(b'\0'+rgb[y*1440:(y+1)*1440] for y in range(360))
     if path:Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',480,360,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b''))
     return len(frames)
