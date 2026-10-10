"""Exact-image, branch, protected-region and inverse verification."""
from pathlib import Path
import sys,json,hashlib
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT.parent))
from patcher import verify_original,verify_layout,sha,PAYLOAD,load_spec
raw=(ROOT.parents[1]/'firmware/V480F_V1.03.bin').read_bytes();verify_original(raw)
image=(ROOT/'.build/candidate.bin').read_bytes();meta=json.loads((ROOT/'.build/ui.json').read_text())
checks=[]
def check(ok,label):assert ok,label;checks.append(label)
verify_layout(image);check(sha(image)==meta['candidate_sha256'],'Candidate SHA and V480 payload MD5/footer match')
check(len(raw)==len(image)==753705,'Original length preserved')
for p in (ROOT/'src').iterdir():check(sha(p.read_bytes())==meta['source_sha256'][p.name],'Built source '+p.name)
restore=bytearray(image);allowed=set(range(PAYLOAD,PAYLOAD+16));md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
for p in meta['patches']:
 a=int(p['offset'],16);old=bytes.fromhex(p['old_bytes']);new=bytes.fromhex(p['new_bytes']);span=set(range(a,a+len(old)))
 check(not allowed&span and len(old)==len(new),'Disjoint, equal-length '+p['purpose']);allowed|=span
 check(raw[a:a+len(old)]==old and image[a:a+len(new)]==new,'Exact bytes '+p['purpose']);restore[a:a+len(old)]=old
 if p['purpose']=='rx_ttl_numeric':
  ins=next(md.disasm(new,0x8008000+a));check(ins.mnemonic=='beq' and int(ins.op_str[1:],16)==0x801f496,'Receiver uses native numeric TTL formatter')
 elif p['purpose']=='rx_group_restore':
  check(new==bytes.fromhex('00bf') and image[0xd876:0xd88e]==raw[0xd876:0xd88e],'Retain RX group with original range validation and radio synchronization')
 elif p['purpose'] not in ['group_ui','v2_rotary_helper']:
  ins=next(md.disasm(new,0x8008000+a));check(ins.mnemonic=='b.w' and int(ins.op_str[1:],16)==(meta['symbols']['sub_'+p['purpose']]&~1),'Hook target '+p['purpose'])
restore[PAYLOAD:PAYLOAD+16]=hashlib.md5(restore[:PAYLOAD]).digest()
check(bytes(restore)==raw,'Exact inverse equals official original')
check(all(i in allowed for i,(a,b) in enumerate(zip(raw,image)) if a!=b),'Every changed byte inside manifest')
for lo,hi,label in [(0,0x280,'vectors'),(0x84980,0x84e34,'scatter and initialization'),(0xb0000,0xb8000,'auxiliary image'),(0xb8010,len(raw),'version footer')]:check(raw[lo:hi]==image[lo:hi],label+' unchanged')
v2=load_spec()['patches'][-1];a=int(v2['offset'],16);blob=bytes.fromhex(v2['new_bytes']);check(image[a:a+len(blob)]==blob,'Published v2 helper preserved byte-for-byte')
check(image[0x85200:0x85200+meta['helper_size']]==(ROOT/'.build/ui.module').read_bytes(),'Linked module matches complete image')
report=dict(status='PASS_V480_R10_IMAGE_INTEGRITY',candidate_sha256=sha(image),total=len(checks),checks=checks,changed_bytes=sum(a!=b for a,b in zip(raw,image)),hardware_verified=False)
(ROOT/'.lab').mkdir(exist_ok=True);(ROOT/'.lab/IMAGE_INTEGRITY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
