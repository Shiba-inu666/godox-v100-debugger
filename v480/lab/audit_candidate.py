"""Independently reparse/disassemble/run the complete candidate bytes.
No input path: audit RAM-built candidate; input path: reopen the actual file.
"""
import argparse,json,struct
from capstone import *
from capstone.arm import ARM_OP_IMM
from config import *
from candidate_vm import VM,RAM

if not __debug__:raise SystemExit('Assertions required')
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input',type=Path,nargs='?');args=ap.parse_args()
original=RAW
data=args.input.read_bytes() if args.input else transform(original)
identity=verify_candidate(data);checks=[]
assert len(data)==len(original)==SIZE
allowed=set(range(CAVE,CAVE+HELPER_SIZE))|set(range(PAYLOAD,PAYLOAD+16))
for off,_,_ in HOOKS:allowed.update(range(off,off+4))
changed=[i for i,(a,b) in enumerate(zip(original,data)) if a!=b]
assert set(changed)<=allowed;checks.append('Every changed byte is in an explicitly allowed range')
for lo,hi,label in [(0,0x280,'vectors'),(0x84980,0x84e34,'scatter/init'),(0xb0000,0xb8000,'auxiliary'),(0xb8010,SIZE,'footer metadata'),(0x2279c,0x22808,'GUI callback')]:
    assert data[lo:hi]==original[lo:hi];checks.append(label+' unchanged')
cs=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);cs.detail=True
base=0x08008000+CAVE
insns=list(cs.disasm(data[CAVE:CAVE+252],base))
assert sum(i.size for i in insns)==252
starts={i.address for i in insns}
branches=[];literal_targets=[]
for i in insns:
    if i.mnemonic in ['b','b.w','bl','beq','bne','cbz','cbnz']:
        target=i.operands[-1]
        assert target.type==ARM_OP_IMM and target.imm in starts,(hex(i.address),i.op_str)
        branches.append(dict(pc=hex(i.address),target=hex(target.imm),instruction=i.mnemonic))
    if i.mnemonic in ['ldr','ldr.w'] and '[pc,' in i.op_str:
        displacement=i.operands[1].mem.disp
        location=((i.address+4)&~3)+displacement
        assert base+252<=location<=base+HELPER_SIZE-4
        value=struct.unpack_from('<I',data,location-0x08008000)[0]
        if i.op_str.startswith('pc,'):
            assert value in [0x0800b4f5,0x08010855,0x0800b9f5]
            literal_targets.append(dict(pc=hex(i.address),resume=hex(value)))
assert len(literal_targets)==3
for (off,old,new),target in zip(HOOKS,[base+88,base,base+44]):
    i,=list(cs.disasm(data[off:off+4],0x08008000+off))
    assert i.mnemonic=='b.w' and i.operands[0].imm==target
    assert original[off:off+4].hex()==old
assert sum(i.mnemonic=='mrs' and 'primask' in i.op_str for i in insns)==3
assert sum(i.mnemonic=='msr' and 'primask' in i.op_str for i in insns)==6
assert sum(i.mnemonic=='cpsid' for i in insns)==3
assert not any(i.mnemonic=='cpsie' for i in insns)
checks+=['All helper instructions decode with Cortex-M mode','All direct branch targets are Thumb instruction starts',
         'All literal pools and original resumed instructions checked','PRIMASK save/restore structure verified']
# Reload the actual complete bytes into a stock VM; do not apply helper patches here.
a=VM('V480F',False);b=VM('V480F',False);b.u.mem_write(0x08008000,data[:PAYLOAD]);p=b.p
executions=0
for mode,values in [(0,[v&255 for v in range(-18,19,2)]),(1,range(81))]:
    for step in ([0] if mode==0 else [0,1]):
        for direction in ['positive','negative']:
            for value in values:
                a.seed(mode,6 if mode==0 else 2,value,step);b.seed(mode,0,value,step)
                a.call(p[direction]);b.call(p[direction])
                assert a.snap(True)==b.snap(True)
                executions+=1
for prev in range(256):
    for phase in range(4):
        for v in [a,b]:v.seed();v.wb(0x13,prev);v.ww(0x28,33);v.phase(phase)
        expected=bytearray(a.snap());struct.pack_into('<i',expected,0x28,33)
        assert b.snap()==bytes(expected);executions+=1
checks.append('Complete candidate image executes original math and decoder; callee registers/SP restored')
report=dict(status='PASS_INDEPENDENT_OFFLINE_AUDIT',source='REOPENED_FIRMWARE_FILE' if args.input else 'IN_MEMORY_PREBUILD',
    input_name=args.input.name if args.input else None,sha256=sha(data),changed_byte_count=len(changed),helper_bytes=HELPER_SIZE,
    helper_instruction_count=len(insns),patched_entry_instructions=3,entry_bytes=12,checksum_bytes=16,
    code_instructions_size=252,literal_and_guard_data_bytes=64,branches=branches,literal_returns=literal_targets,
    whole_image_execution_checks=executions,checks=checks,vector_unchanged=True,auxiliary_unchanged=True,
    bootloader_bytes='Not contained in provided image; updater erase range unverified',
    exact_hardware_model='Not physically read',device_acceptance='NOT_TESTED',hardware_safety_confirmed=False,rollback_guaranteed=False)
dest=ROOT/'analysis'/('binary_audit.json' if args.input else 'prebuild_audit.json')
dest.write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'analysis/final_helper_disassembly.txt').write_text('\n'.join(f'{i.address:08x} {i.bytes.hex():10s} {i.mnemonic} {i.op_str}' for i in insns)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['branches','checks']},indent=2))
