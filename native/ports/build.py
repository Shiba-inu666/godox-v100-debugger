"""Build one exact V100 C/N/S/O input. No device I/O or model auto-detection."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
BASE=0x08008000

def sha(b):return hashlib.sha256(b).hexdigest()
def load(name):return json.loads((ROOT/'profiles'/(name+'.json')).read_text())
def original(p,path):
 b=Path(path).read_bytes()
 if len(b)!=p['size'] or sha(b)!=p['original_sha256']:raise ValueError('Exact original model/version SHA-256 required')
 return b

def branch(site,target):
 d=target-site-4
 if d%2 or not -(1<<24)<=d<(1<<24):raise ValueError('Invalid branch range')
 v=d&0x1ffffff;s=v>>24;i1=v>>23&1;i2=v>>22&1
 return struct.pack('<HH',0xf000|(s<<10)|(v>>12&1023),0x9000|((1^(i1^s))<<13)|((1^(i2^s))<<11)|(v>>1&2047))

def tool(name,env,defaults):
 candidates=[os.environ.get(env),*(str(Path(d)/name) for d in defaults),shutil.which(name)]
 for p in candidates:
  if p and Path(p).is_file():return p
 raise RuntimeError('Missing '+name+'; set '+env)

def build(name,input_path,output):
 p=load(name);raw=original(p,input_path);output=Path(output);output.mkdir(parents=True,exist_ok=True)
 src=ROOT/'src'/name
 for f,h in p['source_sha256'].items():
  if sha((src/f).read_bytes())!=h:raise ValueError('Source identity differs: '+f)
 llvm=['/opt/homebrew/opt/llvm@20/bin','/usr/lib/llvm-20/bin']
 cc=tool('clang','PORT_CLANG',llvm);ld=tool('ld.lld','PORT_LD',['/opt/homebrew/opt/lld/bin',*llvm]);objcopy=tool('llvm-objcopy','PORT_OBJCOPY',llvm);nm=tool('llvm-nm','PORT_NM',llvm)
 image=bytearray(raw);patches=[];symbols={}
 def apply(a,old,new,label):
  off=a-BASE
  if len(old)!=len(new) or bytes(image[off:off+len(old)])!=old:raise ValueError('Patch preimage mismatch: '+label)
  for q in patches:
   if max(a,int(q['address'],16))<min(a+len(old),int(q['address'],16)+q['size']):raise ValueError('Overlapping patch')
  image[off:off+len(new)]=new
  patches.append(dict(name=label,address=hex(a),size=len(new),before_sha256=sha(old),after_sha256=sha(new)))
 with tempfile.TemporaryDirectory(prefix='v100-port-') as td:
  tmp=Path(td);bm=p['bitmap'];a=int(bm['address'],16)-BASE;bitmap=raw[a:a+bm['size']]
  if sha(bitmap)!=bm['sha256']:raise ValueError('Native S bitmap mismatch')
  pix=[v for b in bitmap for v in (b>>4,b&15)];scaled=[]
  for y in range(29):
   sy=y*23*256//28;y0=sy//256;fy=sy%256
   for x in range(23):
    sx=x*18*256//22;x0=sx//256;fx=sx%256
    a=pix[y0*19+x0];b=pix[y0*19+min(x0+1,18)];c=pix[min(y0+1,23)*19+x0];d=pix[min(y0+1,23)*19+min(x0+1,18)]
    scaled.append((a*(256-fx)*(256-fy)+b*fx*(256-fy)+c*(256-fx)*fy+d*fx*fy+32768)//65536)
  packed=bytes((scaled[i]<<4)|(scaled[i+1] if i+1<len(scaled) else 0) for i in range(0,len(scaled),2))
  (tmp/'s_bitmap.h').write_text('static const B s_bitmap[]={'+','.join(map(str,packed))+'};\n')
  flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-Oz','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-stack-protector','-Wall','-Wextra','-Werror','-Wno-deprecated-non-prototype','-I',str(tmp)]
  for family,files,addr,limit,entry in [('ui',['ui.c','ui_trampolines.S'],0x80be800,0x1800+0x1000,'sub_sender'),('rotary',['rotary.S'],0x80bdd00,0x300,'positive_wrapper'),('fire',['fire.S'],0x80be000,0x800,'ttl_wrapper')]:
   objs=[]
   for f in files:
    o=tmp/(f+'.o');subprocess.run([cc,*flags,'-c',str(src/f),'-o',str(o)],check=True);objs.append(str(o))
   script=tmp/(family+'.ld');script.write_text('SECTIONS { . = '+hex(addr)+'; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.ARM.attributes*) *(.comment*) } }')
   elf=tmp/(family+'.elf');blob=tmp/(family+'.module');subprocess.run([ld,'-T',str(script),'--entry='+entry,*objs,'-o',str(elf)],check=True);subprocess.run([objcopy,'-O','binary',str(elf),str(blob)],check=True)
   data=blob.read_bytes()
   if len(data)>limit:raise ValueError('Module exceeds reserved region')
   apply(addr,b'\xff'*len(data),data,family+'_module')
   symbols[family]={r[2]:int(r[0],16) for line in subprocess.check_output([nm,'-n',str(elf)],text=True).splitlines() if len(r:=line.split())==3}
  for h in p['hooks']:
   a=int(h['address'],16);old=bytes.fromhex(h['old_bytes']);target=symbols[h['module']][h['symbol']]&~1
   apply(a,old,branch(a,target)+b'\x00\xbf'*((len(old)-4)//2),h['family']+'_'+h['name'])
  # All addresses embedded by UI trampolines point to these rotary entry offsets.
  for symbol,addr in [('positive_wrapper',0x80bdd00),('negative_wrapper',0x80bdd3c),('decoder_wrapper',0x80bdd78),('gui_wrapper',0x80bdda4)]:
   if symbols['rotary'][symbol]!=addr:raise ValueError('Rotary ABI moved')
 result=bytes(image);mask=bytearray(len(raw))
 for q in patches:
  off=int(q['address'],16)-BASE;mask[off:off+q['size']]=b'\1'*q['size']
 if len(result)!=len(raw) or any(a!=b and not m for a,b,m in zip(raw,result,mask)):raise ValueError('Unexpected image change')
 if raw[:0x1e0]!=result[:0x1e0] or raw[0xc1000:]!=result[0xc1000:]:raise ValueError('Vector or auxiliary payload changed')
 manifest=dict(model=p['model'],firmware_version=p['firmware_version'],filename=p['output_filename'],size=len(result),original_sha256=sha(raw),candidate_sha256=sha(result),hardware_verified=False,profile_sha256=sha((ROOT/'profiles'/(name+'.json')).read_bytes()),source_sha256=p['source_sha256'],patches=patches,compiler=subprocess.check_output([cc,'--version'],text=True).splitlines()[0])
 (output/p['output_filename']).write_bytes(result);(output/'symbols.json').write_text(json.dumps(symbols['ui'],indent=2)+'\n');(output/'PATCH_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (output/'SHA256SUMS').write_text(sha(result)+'  '+p['output_filename']+'\n')
 return manifest
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('model',choices=[p.stem for p in (ROOT/'profiles').glob('*.json')]);a.add_argument('original');a.add_argument('output');x=a.parse_args();m=build(x.model,x.original,x.output);print(m['model'],m['filename'],m['candidate_sha256'])
