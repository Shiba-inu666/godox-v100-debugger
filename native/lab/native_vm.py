"""Original startup data, heap, LVGL, widgets, events, and callbacks on Unicorn.

This executes UI machine code, not a Python widget model. Hardware is not emulated.
"""
from stock_vm import *
from config import NATIVE,IMAGE
class NativeVM(StockVM):
    def __init__(self,patched=True,image=None):
        super().__init__()
        self.manifest=json.loads((NATIVE/'metadata/ui.json').read_text())
        if image is not None:
            assert len(image)==len(RAW)
            self.u.mem_write(0x08008000,image)
        elif patched:
            self.u.mem_write(0x08008000,IMAGE)
        for reg,val in [(UC_ARM_REG_R0,0x080bc7e8),(UC_ARM_REG_R1,RAM),(UC_ARM_REG_R2,0xb38),(UC_ARM_REG_LR,STOP|1),(UC_ARM_REG_SP,SP)]:self.u.reg_write(reg,val)
        self.u.emu_start(0x080081e9,STOP,count=100000)
        assert self.u.reg_read(UC_ARM_REG_PC)==STOP
        for a in [0x08038684,0x0803ec78,0x0803ecd8]:self.call(a)
        self.wb(0x496,1);self.wb(0x544,1);self.wb(0x4c0,30);self.wb(0x4c1,1);self.wb(0x4c3,1)
        self.wb(0x5a1,1) # Suppress unrelated top drawer in bounded UI tests.
        self.wb(0x12fa,1);self.wb(0x503,1)
        self.u.mem_write(RAM+0x4d0,bytes([40,30,20,10,0,77]))
        self.u.mem_write(RAM+0x4c4,bytes([1]*5));self.u.mem_write(RAM+0x504,bytes([1]*5))
    def call(self,address,*args,count=100000000):return super().call(address,*args,count=count)
    def function(self,name,*args):return self.call(self.manifest['symbols'][name],*args)
    def create(self,page):
        self.wb(0x59f,page);self.wb(0x398,page);self.wb(0x33c,{0:0,1:3,2:4}[page]);self.wb(0x599,0);self.wb(0x59a,0)
        self.call({0:0x0804a548,1:0x0804c75c,2:0x0804cc88}[page])
        r=self.rw({0:0x5d8,1:0x600,2:0x604}[page]);self.call(0x0803175c,r)
        self.call(0x08036e08,self.rw(0x9e8),0)
        return r
    def event(self,obj,code=4,keyboard=False):return self.call(0x08035fc8,obj,code,self.rw(0x9e0 if keyboard else 0x9dc))
    def focus(self):return self.call(0x08036c10,self.rw(0x9e8))
    def coords(self,obj):return struct.unpack('<4h',self.u.mem_read(obj+0x14,8))
    def text(self,label):
        # Actual lv_label_t text member: established by 0x08039520 stores.
        a=struct.unpack('<I',self.u.mem_read(label+0x24,4))[0]
        return bytes(self.u.mem_read(a,100)).split(b'\0')[0].decode('utf-8')
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
        if path:
            import zlib
            rgb=bytearray(480*360*3)
            for (x0,y0,x1,y1),data in frames:
                for j,value in enumerate(struct.unpack('<'+'H'*(len(data)//2),data)):
                    x=x0+j%(x1-x0+1);y=y0+j//(x1-x0+1)
                    if 0<=x<480 and 0<=y<360:
                        k=(y*480+x)*3;rgb[k:k+3]=bytes((((value>>11)&31)*255//31,((value>>5)&63)*255//63,(value&31)*255//31))
            def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
            scan=b''.join(b'\0'+rgb[y*1440:(y+1)*1440] for y in range(360))
            Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',480,360,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b''))
        return len(frames)
if __name__=='__main__':
    for page in [1,2]:
        v=NativeVM();v.create(page)
        print('page',page,'sub',hex(v.rw(0x1550)),'group',hex(v.rw(0x9e8)))
        v.call(0x08036af0,v.rw(0x1550));v.event(v.rw(0x1550),keyboard=True)
        print('modal',hex(v.rw(0x156c)),'selector',v.rb(0x4e5),'focused',hex(v.focus()))
        v.call(0x08010924);print('power',v.rb(0x4c0))
        v.event(v.rw(0x1570));print('closed',hex(v.rw(0x156c)),hex(v.focus()))
