"""Independent full-image preservation and deterministic reconstruction checks."""
from pathlib import Path
import sys,json,hashlib,tempfile,os
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build import ROOT,BASE,load,original,build,sha
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
name=sys.argv[1];p=load(name);folder=ROOT/'.lab'/name;inp=Path(os.environ.get('V100_PORT_ORIGINAL',str(ROOT.parents[1]/'firmware/upstream-v100-2026-10-10'/p['original_filename'])));raw=original(p,inp);image=(folder/p['output_filename']).read_bytes();m=json.loads((folder/'PATCH_MANIFEST.json').read_text());checks=[]
def check(ok,label):
 assert ok,label
 checks.append(label)
check(len(raw)==len(image)==p['size'],'size');check(sha(image)==m['candidate_sha256'],'identity');marker=('Model: V100 '+p['model'][-1]).encode()+b'\0';check(image.count(marker)==raw.count(marker)==1 and image.index(marker)==raw.index(marker),'exact_model_marker_preserved')
mask=bytearray(len(raw));restored=bytearray(image)
for q in m['patches']:
 o=int(q['address'],16)-BASE;n=q['size'];check(not any(mask[o:o+n]),'disjoint_regions');mask[o:o+n]=b'\1'*n
 check(sha(raw[o:o+n])==q['before_sha256'] and sha(image[o:o+n])==q['after_sha256'],'region_hash');restored[o:o+n]=raw[o:o+n]
 if q['name'].endswith('_module'):check(raw[o:o+n]==b'\xff'*n,'unused_flash_only')
check(all(a==b for a,b,k in zip(raw,image,mask) if not k),'every_unpatched_byte_preserved');check(bytes(restored)==raw,'inverse_identity');check(raw[:0x1e0]==image[:0x1e0],'vectors_preserved');check(raw[0xc1000:]==image[0xc1000:],'auxiliary_payload_preserved')
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
for h in p['hooks']:
 a=int(h['address'],16);row=next(md.disasm(image[a-BASE:a-BASE+4],a));check(row.mnemonic=='b.w','hook_is_branch');target=int(row.op_str[1:],16);check(0x80bdd00<=target<0x80c1000,'branch_targets_helper')
with tempfile.TemporaryDirectory() as t:
 rebuild=build(name,inp,Path(t)/'rebuild');check((Path(t)/'rebuild'/p['output_filename']).read_bytes()==image,'deterministic_rebuild')
 for other in (ROOT/'profiles').glob('*.json'):
  if other.stem==name:continue
  rejected=False
  try:original(json.loads(other.read_text()),inp)
  except ValueError:rejected=True
  check(rejected,'cross_model_rejected')
 bad=bytearray(raw);bad[len(raw)//2]^=1;bp=Path(t)/'bad.bin';bp.write_bytes(bad);rejected=False
 try:original(p,bp)
 except ValueError:rejected=True
 check(rejected,'altered_input_rejected')
r=dict(status='PASS_IMAGE_INTEGRITY',model=name,checks=len(checks),candidate_sha256=sha(image),original_sha256=sha(raw),hardware_verified=False,checked=checks)
(folder/'integrity-results.json').write_text(json.dumps(r,indent=2)+'\n');print(name,r['checks'],'integrity checks passed')
