"""Build the V480F-specific R10 group editor over the exact published v2."""
from pathlib import Path
import sys,os,json,subprocess,struct,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT.parent))
from patcher import verify_original,verify_layout,transform,load_spec,sha,require,PAYLOAD,OFFICIAL_SHA,CANARY_SHA
BASE=0x0808d200
HOOKS=[('sender',0x804d1b0,'2de9f04f'),('focus',0x802d788,'70b5484d'),('tick',0x8043240,'2de9f04f'),('page',0x801d3ec,'0c2828bf7047'),('sender_event',0x801c368,'2de9f041'),('gui',0x802a79c,'2de9f047'),('save',0x80121a0,'70b5424d')]
def branch(site,target):
 d=target-site-4;require(d%2==0 and -(1<<24)<=d<(1<<24),'branch range');v=d&0x1ffffff;s=v>>24;i1=v>>23&1;i2=v>>22&1
 return struct.pack('<HH',0xf000|(s<<10)|(v>>12&1023),0x9000|((1^(i1^s))<<13)|((1^(i2^s))<<11)|(v>>1&2047))
def build():
 raw=(ROOT.parents[1]/'firmware/V480F_V1.03.bin').read_bytes();verify_original(raw);v2=transform(raw);out=ROOT/'.build';out.mkdir(exist_ok=True)
 llvm=Path(os.environ.get('GODOX_LLVM_BIN','/opt/homebrew/opt/llvm@20/bin'));linker=os.environ.get('GODOX_LD_LLD','/opt/homebrew/opt/lld/bin/ld.lld')
 cc=[str(llvm/'clang'),'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-Oz','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-stack-protector','-Wall','-Wextra','-Werror','-Wno-deprecated-non-prototype','-c']
 for f in ['group_ui.c','trampolines.S']:subprocess.run(cc+[str(ROOT/'src'/f),'-o',str(out/(f+'.o'))],check=True)
 subprocess.run([linker,'-T',str(ROOT/'src/ui.ld'),'--entry=sub_sender',str(out/'group_ui.c.o'),str(out/'trampolines.S.o'),'-o',str(out/'ui.elf')],check=True)
 subprocess.run([str(llvm/'llvm-objcopy'),'-O','binary',str(out/'ui.elf'),str(out/'ui.module')],check=True)
 blob=(out/'ui.module').read_bytes();off=BASE-0x8008000
 require(off+len(blob)<0xb0000 and raw[off:off+len(blob)]==b'\xff'*len(blob),'Not erased main flash')
 symbols={p[2]:int(p[0],16) for line in subprocess.check_output([str(llvm/'llvm-nm'),'-n',str(out/'ui.elf')],text=True).splitlines() if len(p:=line.split())==3}
 spec=load_spec();patches=[dict(p,purpose='v2_rotary_helper') for p in spec['patches'] if int(p['offset'],16)==0x85000]
 hooks=list(HOOKS)+[(h['name'],int(h['address'],16),h['original']) for h in json.loads((ROOT.parent/'metadata/build.json').read_text())['hooks']]
 for name,a,before in hooks:
  n=len(bytes.fromhex(before));patches.append(dict(purpose=name,offset=hex(a-0x8008000),old_bytes=before,new_bytes=(branch(a,symbols['sub_'+name]&~1)+b'\x00\xbf'*((n-4)//2)).hex()))
 patches.append(dict(purpose='group_ui',offset=hex(off),old_bytes=raw[off:off+len(blob)].hex(),new_bytes=blob.hex()))
 # The native TTL formatter deliberately displays only "TTL" on Receiver.
 # Route its page-2 branch through the existing numeric/sign formatter. This
 # changes no role/page RAM and retains the native RX alignment and colours.
 patches.append(dict(purpose='rx_ttl_numeric',offset=hex(0x801f47e-0x8008000),old_bytes='74d0',new_bytes='0ad0'))
 # Retain the saved RX group even when booting into Wi-Off or Sender.
 # Only remove the role-dependent reset; native 1..5 validation still runs.
 patches.append(dict(purpose='rx_group_restore',offset=hex(0x8015874-0x8008000),old_bytes='04d1',new_bytes='00bf'))
 image=bytearray(raw);occupied=set()
 for p in patches:
  a=int(p['offset'],16);old=bytes.fromhex(p['old_bytes']);new=bytes.fromhex(p['new_bytes']);span=set(range(a,a+len(old)))
  require(len(old)==len(new) and raw[a:a+len(old)]==old and not occupied&span,'Patch context/overlap mismatch: '+p['purpose']);occupied|=span;image[a:a+len(old)]=new
 image[PAYLOAD:PAYLOAD+16]=hashlib.md5(image[:PAYLOAD]).digest();image=bytes(image);verify_layout(image)
 for lo,hi in [(0,0x280),(0x84980,0x84e34),(0xb0000,0xb8000),(0xb8010,len(raw))]:require(raw[lo:hi]==image[lo:hi],'Protected range changed')
 meta=dict(model='V480F',version='1.03',revision='R10B_RX_GROUP_PERSIST_EXPERIMENTAL',original_sha256=OFFICIAL_SHA,base_sha256=CANARY_SHA,candidate_sha256=sha(image),helper_size=len(blob),helper_sha256=sha(blob),symbols=symbols,patches=patches,source_sha256={p.name:sha(p.read_bytes()) for p in sorted((ROOT/'src').iterdir())},hardware_verified=False)
 (out/'ui.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'candidate.bin').write_bytes(image)
 (out/'disassembly.txt').write_text(subprocess.check_output([str(llvm/'llvm-objdump'),'-d',str(out/'ui.elf')],text=True))
 print(json.dumps({k:meta[k] for k in ['candidate_sha256','helper_size','hardware_verified']},indent=2));return image,meta
if __name__=='__main__':build()
