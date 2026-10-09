"""Machine-code regressions for v2, including source-channel ownership.
No device access; GUI styling is stubbed, numeric consumer helpers execute.
"""
import collections,json,struct
from candidate_vm import *

if not __debug__:raise SystemExit('Assertions required')
DEST=ROOT/'analysis/functional_tests.json'
DEST.write_text('{"status":"RUNNING_NOT_PASS"}\n')
counts=collections.Counter();examples=[];bounds={}
for model in Q:
    a=VM(model,False);b=VM(model);p=b.p
    maximum_masked=maximum_stack=0
    # Includes legal values and every sentinel/invalid byte; native handling wins.
    for mode,values in [(0,range(256)),(1,range(256))]:
        for step in ([0] if mode==0 else [0,1,2,255]):
            for direction in ['positive','negative']:
                for value in values:
                    a.seed(mode,6 if mode==0 else 2,value,step);b.seed(mode,0,value,step)
                    a.call(p[direction]);b.run_trace(p[direction])
                    assert a.snap(True)==b.snap(True),(model,mode,step,direction,value)
                    assert b.rb(p['selector'])==0 and b.u.reg_read(UC_ARM_REG_PRIMASK)==0
                    writes=[w for w in b.memory_writes if w[0] in [RAM+p['fec'],RAM+p['power']]]
                    assert writes and all(w[3]==1 for w in writes)
                    masked=sum(m==1 for _,m,_ in b.trace)
                    maximum_masked=max(maximum_masked,masked)
                    maximum_stack=max(maximum_stack,SP-min(s for _,_,s in b.trace))
                    counts['all_parameter_byte_equivalence']+=1
                    if value in [0,18,238,40,80] and step in [0,1]:
                        examples.append(dict(model=model,mode=mode,step=step,direction=direction,
                            before=value,after=b.rb(p['fec'] if mode==0 else p['power'])))
    guard=b.base+b.m['symbols']['scope_guard']
    for selector in range(1,256):
        b.seed(selector=selector);assert b.call(guard)==0;counts['nonzero_selector_guard']+=1
    for off in p['zero_byte_guards']:
        for value in range(1,256):
            for mode in [0,1]:
                b.seed(mode);b.wb(off,value);assert b.call(guard)==0
                counts['all_excluded_byte_values']+=1
    for mode in range(256):
        b.seed(mode);assert b.call(guard)=={0:6,1:2}.get(mode&3,0);counts['all_mode_bits']+=1
    for off,mask in [(0x31,8),(p['flags2'],2)]:
        for value in range(256):
            b.seed();b.wb(off,value);assert b.call(guard)==(0 if value&mask else 6)
            counts['flags']+=1
    exclusions=[(off,1,1) for off in p['zero_byte_guards']]+[(off,RAM+0x8800,4) for off in p['modals']]+[(p['root'],0,4),(p['mode'],2,1),(p['mode'],3,1),(p['selector'],2,1),(p['selector'],6,1),(0x31,8,1),(p['flags2'],2,1)]
    for off,value,width in exclusions:
        for direction in ['positive','negative']:
            for v in [a,b]:
                v.seed(value=40);(v.wb if width==1 else v.ww)(off,value);v.call(p[direction])
            assert a.snap()==b.snap(),(model,off,value,direction)
            counts['actual_dispatch_fallback']+=1
        for pressed in [0,1]:
            for v in [a,b]:
                v.seed();(v.wb if width==1 else v.ww)(off,value);v.ww(0x28,-3)
                v.u.mem_write(p['key_gpio'],struct.pack('<I',0 if pressed else p['key_bit']))
                v.call(p['gui'],0,RAM+0xf000)
            assert a.snap()==b.snap() and a.stub_calls==b.stub_calls
            counts['unchanged_GUI_SET_fallback']+=1
    # Exhaust every previous decoder state and each current GPIO phase.
    # Direct events preserve pre-existing GUI delta instead of adding a replay.
    for direct in [True,False]:
        for prev in range(256):
            for phase in range(4):
                for v in [a,b]:
                    v.seed();v.wb(0x13,prev);v.ww(0x28,123)
                    v.wb(0x16,254);v.wb(0x17,255)
                    if not direct:v.wb(p['page'],3)
                    v.phase(phase)
                expected=bytearray(a.snap())
                if direct:struct.pack_into('<i',expected,0x28,123)
                assert bytes(expected)==b.snap(),(model,direct,prev,phase)
                assert b.u.reg_read(UC_ARM_REG_PRIMASK)==0
                counts['decoder_all_states']+=1
    for primask in [0,1]:
        for fn in [p['positive'],p['negative'],p['decoder']]:
            for excluded in [False,True]:
                b.seed();b.u.reg_write(UC_ARM_REG_PRIMASK,primask)
                if excluded:b.wb(p['page'],3)
                b.run_trace(fn)
                assert b.u.reg_read(UC_ARM_REG_PRIMASK)==primask
                maximum_masked=max(maximum_masked,sum(m==1 for _,m,_ in b.trace))
                maximum_stack=max(maximum_stack,SP-min(s for _,_,s in b.trace))
                counts['PRIMASK_preservation']+=1
    b.u.reg_write(UC_ARM_REG_PRIMASK,0)
    for mode in [0,1]:
        for step in [0,1]:
            for direction,seq in [('positive',[0,1,3,2,0]),('negative',[0,2,3,1,0])]:
                for cycles in [1,2,4,8,16]:
                    for order in ['GUI-first','consumer-first']:
                        for v in [a,b]:
                            v.seed(mode,(6 if mode==0 else 2) if v is a else 0,0 if mode==0 else 40,step)
                            for _ in range(cycles):
                                for ph in seq:v.phase(ph)
                        assert b.delta()==0
                        if order=='GUI-first':b.call(p['gui'],0,RAM+0xf000)
                        a.call(a.q['consumer']);b.call(b.q['consumer'])
                        if order=='consumer-first':b.call(p['gui'],0,RAM+0xf000)
                        assert a.rb(p['fec'])==b.rb(p['fec']) and a.rb(p['power'])==b.rb(p['power'])
                        assert b.u.mem_read(RAM+0xf00c,2)==b'\0\0'
                        assert b.rb(0x16)==b.rb(0x17)==0
                        counts['real_decoder_acceleration_pipeline']+=1
    # The old TC-02/06 replay disappears at the source, independently of group focus.
    for mode in [0,1]:
        for destination in [1,2,3,4,5,11]:
            for focus in [0,4]:
                for order in ['adjust-then-page','page-before-adjust']:
                    b.seed(mode,value=0 if mode==0 else 40)
                    for ph in [0,1,3]:b.phase(ph)
                    assert b.delta()==0 and b.rb(0x16)==1
                    if order=='adjust-then-page':b.call(b.q['consumer'])
                    b.wb(p['page'],destination);b.wb(p['role'],3 if destination==1 else 4 if destination==2 else 0)
                    b.u.mem_write(RAM+0xe220,struct.pack('<H',focus))
                    if order=='page-before-adjust':b.call(b.q['consumer'])
                    b.call(p['gui'],0,RAM+0xf000)
                    assert b.u.mem_read(RAM+0xf00c,2)==b'\0\0'
                    counts['TC02_TC06_no_replay_after_page_change']+=1
    bounds[model]=dict(max_observed_masked_instructions=maximum_masked,max_observed_call_stack_bytes=maximum_stack,
        wall_clock_WCET='NOT_MEASURED',note='Instruction count is not a hardware latency guarantee')
report=dict(candidate_sha256=sha(IMAGE),publication_scope='V480F_ONLY_PUBLIC_RERUN',status='PASS_OFFLINE_CANDIDATE',counts=dict(counts),total=sum(counts.values()),bounds=bounds,examples=examples,
    helper_hashes={m:META['helper_sha256'] for m in Q},
    hardware_tested=False,canary_generated=False,limitations=['Synthetic SRAM, not boot-to-state proof','Original numeric consumer helpers execute; GUI styling hook remains stubbed',
    'TC02/06 source ownership invariant does not require executing complete group lifecycle','Physical clockwise direction inherits stock editing; not measured','Touch code unchanged; complete touchscreen hardware regression not run'])
DEST.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='examples'},indent=2))
