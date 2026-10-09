"""Exact-version provenance, ABI and new guard coverage at both role-load hooks."""
from fire_vm import *
from itertools import product
from collections import Counter
counts=Counter();v=FireVM();manifest=json.loads((NATIVE/'metadata/fire.json').read_text());base=int(manifest['helper_base'],16)
def run(kind,role=3,mode=1,leaf=None,outer=0x08011231,primask=1,changes=None):
 v.setup(role,mode)
 for off,val in (changes or {}).items():v.wb(off,val)
 sp=RAM+0xe0000;v.u.mem_write(sp-64,b'\xa5'*192)
 lo,up,expected,end=(4,28,0x0800f017,0x0800d7ca) if kind=='ttl' else (36,60,0x0800efe9,0x08012202)
 v.u.mem_write(sp+lo,struct.pack('<I',expected if leaf is None else leaf));v.u.mem_write(sp+up,struct.pack('<I',outer))
 for i,r in enumerate(REGS):v.u.reg_write(r,0x11220000+i)
 v.u.reg_write(UC_ARM_REG_R10,RAM+0x33c);v.u.reg_write(UC_ARM_REG_SP,sp);v.u.reg_write(UC_ARM_REG_LR,0x08012327)
 v.u.reg_write(UC_ARM_REG_XPSR,0xa1000000);v.u.reg_write(UC_ARM_REG_PRIMASK,primask)
 before_regs=[v.u.reg_read(r) for r in REGS];before=bytes(v.u.mem_read(RAM,0x100000))
 target=base+manifest['symbols'][kind+'_wrapper'];v.u.emu_start(target|1,end,count=500)
 assert v.u.reg_read(UC_ARM_REG_PC)==end and v.u.reg_read(UC_ARM_REG_SP)==sp
 assert v.u.reg_read(UC_ARM_REG_LR)==0x08012327 and v.u.reg_read(UC_ARM_REG_PRIMASK)==primask
 assert [v.u.reg_read(r) for r in REGS[1:]]==before_regs[1:]
 after=bytes(v.u.mem_read(RAM,0x100000));i=sp-RAM
 assert before[:i-16]==after[:i-16] and before[i:]==after[i:],'Unexpected RAM write'
 assert v.rb(0x33c)==role and not v.gpio
 return v.u.reg_read(UC_ARM_REG_R0)
for kind,role,primask in product(['ttl','manual'],range(256),[0,1]):
 out=run(kind,role=role,primask=primask)
 assert out==(0 if role in [0,3,4] else role)
 counts['all_role_values_ABI_no_global_writes']+=1
for kind,role in product(['ttl','manual'],[3,4]):
 expected=0x0800f017 if kind=='ttl' else 0x0800efe9
 for bit in range(32):
  assert run(kind,role,leaf=expected^(1<<bit))==role
  assert run(kind,role,outer=0x08011231^(1<<bit))==role
  counts['caller_provenance_bit_mutations_reject']+=2
 for mode in range(256):
  eligible=(mode&3)<=1 and not(mode&0x10)
  assert run(kind,role,mode=mode)==(0 if eligible else role)
  counts['mode_flags_HSS_Multi_filter']+=1
 # Gate is a conjunction: corrupt either source value even when another
 # stale stack word happens to look like a physical return address.
 assert run(kind,role,leaf=STOP|1)==role and run(kind,role,outer=STOP|1)==role
 counts['direct_leaf_or_dispatch_reject']+=2
# Patch tool refuses wrong model/version/content and already-patched images.
for name,data in [('candidate',IMAGE),('truncated',RAW[:-1]),('extended',RAW+b'\x00'),('model',RAW[:0x42028]+b'Z'+RAW[0x42029:]),('hook',RAW[:0x57c6]+bytes([RAW[0x57c6]^1])+RAW[0x57c7:])]:
 try:compose(data)
 except ValueError:counts['patch_input_fails_closed']+=1
 else:raise AssertionError(name)
r=dict(status='PASS_EXACT_VERSION_WRAPPER_ABI_AND_SOURCE',candidate_sha256=sha(IMAGE),counts=dict(counts),total=sum(counts.values()),extra_stack_bytes=16,global_RAM_writes=0,PRIMASK_modified=False,limits=['Frame offsets apply only to the exact SHA-256-locked V100F V1.03','Stack provenance constrains control flow; this is not an adversarial security boundary','Offline emulator registers, not physical MCU instrumentation'])
(ROOT/'analysis/WRAPPER_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
