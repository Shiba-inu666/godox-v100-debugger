"""Exact-image, unchanged R7 helper, branch and inverse-patch verification."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];NATIVE=ROOT.parent
sys.path.insert(0,str(NATIVE))
from patcher import original,transform,sha,load_spec,R7_SHA256
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
raw=(NATIVE.parent/'firmware/V100F_V1.03.bin').read_bytes();original(raw)
image=(ROOT/'.build/candidate.bin').read_bytes();spec=json.loads((ROOT/'.build/r10.json').read_text())
meta=json.loads((ROOT/'.build/ui.json').read_text());r7=transform(raw);checks=[]
def check(ok,name):
 assert ok,name
 checks.append(name)
check(sha(r7)==R7_SHA256,'Exact public R7 base')
check(len(image)==len(raw)==1002732,'Full image size unchanged')
check(transform(raw,spec)==image,'Forward patch exact')
check(transform(image,spec,restore=True)==raw,'Inverse restores exact official original')
check(image[:0x1b4]==raw[:0x1b4],'Original vector table unchanged')
check(image[0xf0000:]==raw[0xf0000:],'Original auxiliary payload unchanged')
check(sha(image)==meta['candidate_sha256']==spec['modified_sha256'],'All image digests agree')
changed={i for i,(a,b) in enumerate(zip(r7,image)) if a!=b}
allowed=set()
for p in load_spec()['patches']:
 a=int(p['offset'],16);n=len(bytes.fromhex(p['new_bytes']))
 if p['purpose'].startswith('native_ui:'):allowed.update(range(a,a+n))
 elif p['purpose'].endswith('helper') or not p['purpose'].startswith('fixed_main:'):
  check(image[a:a+n]==r7[a:a+n],p['purpose']+' retained from R7')
# New UI and narrowly wrapped rotary entry sites are the only R10 change spans.
for p in spec['patches']:
 if p['purpose'].startswith('native_ui:'):
  a=int(p['offset'],16);allowed.update(range(a,a+len(bytes.fromhex(p['new_bytes']))))
check(changed<=allowed,'No unlisted changes from R7')
for a,b in [(0x0801bbe8,0x0801bf44),(0x08017038,0x080175e8),(0x0801c0dc,0x0801c0f4)]:
 check(image[a-0x08008000:b-0x08008000]==r7[a-0x08008000:b-0x08008000],'Stock gesture callback unchanged '+hex(a))
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
for h in meta['hooks']:
 a=int(h['address'],16);o=a-0x8008000;i=next(md.disasm(image[o:o+4],a))
 check(i.mnemonic=='b.w' and int(i.op_str.lstrip('#'),16)==int(h['target'],16),'Hook target '+h['name'])
for name,digest in meta['source_sha256'].items():check(sha((ROOT/'src'/name).read_bytes())==digest,'Compiled source '+name)
report=dict(status='PASS_R10_IMAGE_INTEGRITY',candidate_sha256=sha(image),base_sha256=sha(r7),original_sha256=sha(raw),total=len(checks),checks=checks,
 changed_bytes_from_R7=len(changed),hardware_verified=False)
out=ROOT/'.lab';out.mkdir(exist_ok=True);(out/'IMAGE_INTEGRITY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
