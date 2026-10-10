"""Compile R10 UI on the exact public R7 base; no device I/O."""
from pathlib import Path
import argparse,json,os,subprocess,sys,struct
ROOT=Path(__file__).resolve().parent;NATIVE=ROOT.parent
sys.path.insert(0,str(NATIVE))
from patcher import original,transform,load_spec,sha,require,R7_SHA256
BASE=0x080be800

def branch(site,target):
 d=target-site-4;require(d%2==0 and -(1<<24)<=d<(1<<24),'branch range')
 v=d&0x1ffffff;s=v>>24;i1=v>>23&1;i2=v>>22&1
 return struct.pack('<HH',0xf000|(s<<10)|(v>>12&1023),0x9000|((1^(i1^s))<<13)|((1^(i2^s))<<11)|(v>>1&2047))

def build(firmware=None,github_base=None):
 raw=Path(firmware or NATIVE.parent/'firmware/V100F_V1.03.bin').read_bytes();original(raw)
 r7=transform(raw);require(sha(r7)==R7_SHA256,'R7 mismatch')
 if github_base: require(Path(github_base).read_bytes()==r7,'GitHub base does not match R7')
 out=ROOT/'.build';out.mkdir(exist_ok=True)
 llvm=Path(os.environ.get('GODOX_LLVM_BIN','/opt/homebrew/opt/llvm@20/bin'))
 linker=os.environ.get('GODOX_LD_LLD','/opt/homebrew/opt/lld/bin/ld.lld')
 # Exact R7 S bitmap (19x24, 4 bpp); bilinear fixed-point resize to the
 # native M/A-D cap height 29. The native glyph callbacks are tested separately.
 source=raw[0x080ba01c-0x08008000:0x080ba01c-0x08008000+228]
 pixels=[p for b in source for p in (b>>4,b&15)]
 scaled=[]
 for y in range(29):
  sy=y*23*256//28; y0=sy//256; fy=sy%256
  for x in range(23):
   sx=x*18*256//22;x0=sx//256;fx=sx%256
   a=pixels[y0*19+x0];b=pixels[y0*19+min(x0+1,18)]
   c=pixels[min(y0+1,23)*19+x0];d=pixels[min(y0+1,23)*19+min(x0+1,18)]
   scaled.append((a*(256-fx)*(256-fy)+b*fx*(256-fy)+c*(256-fx)*fy+d*fx*fy+32768)//65536)
 packed=bytes((scaled[i]<<4)|(scaled[i+1] if i+1<len(scaled) else 0) for i in range(0,len(scaled),2))
 (out/'s_bitmap.h').write_text('static const B s_bitmap[] = {'+','.join(str(x) for x in packed)+'};\n')
 cc=[str(llvm/'clang'),'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-Oz','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-stack-protector','-Wall','-Wextra','-Werror','-Wno-deprecated-non-prototype','-I',str(out),'-c']
 for src,name in [('native_sub.c','native_sub'),('native_trampolines.S','trampolines')]:
  subprocess.run(cc+[str(ROOT/'src'/src),'-o',str(out/(name+'.o'))],check=True)
 subprocess.run([linker,'-T',str(ROOT/'src/native.ld'),'--entry=sub_sender',str(out/'native_sub.o'),str(out/'trampolines.o'),'-o',str(out/'native_sub.elf')],check=True)
 subprocess.run([str(llvm/'llvm-objcopy'),'-O','binary',str(out/'native_sub.elf'),str(out/'native_sub.module')],check=True)
 blob=(out/'native_sub.module').read_bytes();off=BASE-0x08008000
 require(raw[off:off+len(blob)]==b'\xff'*len(blob),'UI helper exceeds erased flash space')
 # Keep the R7 fire and rotary helpers. Wrap the four rotary entry hooks only
 # while a dedicated editor is open; all other paths reach those same helpers.
 spec=load_spec();rotary=json.loads((NATIVE/'metadata/rotary.json').read_text());overrides={h['offset'] for h in rotary['hooks']}
 patches=[p for p in spec['patches'] if not p['purpose'].startswith('native_ui:') and p['offset'] not in overrides]
 symbols={p[2]:int(p[0],16) for line in subprocess.check_output([str(llvm/'llvm-nm'),'-n',str(out/'native_sub.elf')],text=True).splitlines() if len(p:=line.split())==3}
 meta=json.loads((NATIVE/'metadata/ui.json').read_text())
 meta['hooks']+=rotary['hooks']
 for h in meta['hooks']:
  a=int(h['address'],16);n=len(bytes.fromhex(h['old_bytes']));target=symbols['sub_'+h['name']]&~1
  h.update(target=hex(target),new_bytes=(branch(a,target)+b'\x00\xbf'*((n-4)//2)).hex())
  patches.append(dict(purpose='native_ui:'+h['name'],offset=h['offset'],old_bytes=h['old_bytes'],new_bytes=h['new_bytes']))
 patches.append(dict(purpose='native_ui:helper',offset=hex(off),old_bytes=raw[off:off+len(blob)].hex(),new_bytes=blob.hex()))
 image=bytearray(raw)
 occupied=set()
 for p in patches:
  a=int(p['offset'],16);before=bytes.fromhex(p['old_bytes']);after=bytes.fromhex(p['new_bytes'])
  require(len(before)==len(after) and raw[a:a+len(before)]==before,'patch mismatch')
  span=set(range(a,a+len(before)));require(not occupied&span,'overlapping patches');occupied|=span
  image[a:a+len(after)]=after
 image=bytes(image)
 require(image[:0x1b4]==raw[:0x1b4] and image[0xf0000:]==raw[0xf0000:],'protected payload changed')
 for p in patches:
  if not p['purpose'].startswith('native_ui:'):
   a=int(p['offset'],16);n=len(bytes.fromhex(p['new_bytes']));require(image[a:a+n]==r7[a:a+n],'R7 non-UI change')
 meta.update(symbols=symbols,helper_size=len(blob),helper_sha256=sha(blob),candidate_sha256=sha(image),base_sha256=sha(r7),status='R10_UI_EXPERIMENTAL',source_sha256={p.name:sha(p.read_bytes()) for p in sorted((ROOT/'src').iterdir())})
 (out/'ui.json').write_text(json.dumps(meta,indent=2)+'\n')
 (out/'candidate.bin').write_bytes(image)
 spec.update(modified_sha256=sha(image),source_sha256=meta['source_sha256'],patches=patches)
 (out/'r10.json').write_text(json.dumps(spec,indent=2)+'\n')
 (out/'disassembly.txt').write_text(subprocess.check_output([str(llvm/'llvm-objdump'),'-d',str(out/'native_sub.elf')],text=True))
 print(json.dumps(dict(size=len(image),sha256=sha(image),helper_size=len(blob),base_sha256=sha(r7)),indent=2))
 return image,meta
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--firmware',type=Path);p.add_argument('--github-base',type=Path);a=p.parse_args();build(a.firmware,a.github_base)
