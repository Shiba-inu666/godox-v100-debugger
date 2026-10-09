"""Deliver a real stock ISR at every instruction boundary, honoring PRIMASK.
The interrupt scheduler/exception context and UART bytes remain synthetic.
"""
import collections,json
from candidate_vm import *

if not __debug__:raise SystemExit('Assertions required')
DEST=ROOT/'analysis/interrupt_tests.json';DEST.write_text('{"status":"RUNNING_NOT_PASS"}\n')
results=[]
for model in Q:
    v=VM(model);p=v.p;q=v.q
    next_byte=[0];writer_hits=[]
    def io(u,a,s,d):
        ret=next_byte[0] if a==q['rx_data'] else 0 if a==q['tx'] else 1
        u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    for fn in [q['rx_status'],q['rx_data'],q['tx'],q['tx_status']]:v.u.hook_add(UC_HOOK_CODE,io,begin=fn,end=fn)
    v.u.hook_add(UC_HOOK_CODE,lambda u,a,s,d:writer_hits.append(a),begin=q['writer'],end=q['writer'])
    def prepare(mode,target):
        v.seed(mode,value=0 if mode==0 else 40);v.wb(q['consumer_enable'],8)
        v.u.reg_write(UC_ARM_REG_PRIMASK,0);writer_hits.clear()
        data=bytearray(25);data[0]=0xb0;data[2]=target;data[3]=1;data[8]=0x40
        data[24]=(0xb1+sum(data[1:24]))&255
        for byte in data[:-1]:next_byte[0]=byte;v.call(q['isr'])
        assert v.rb(q['index'])==24 and not writer_hits
        return data
    for mode,target in [(0,1),(1,0)]:
        for direction in ['positive','negative']:
            packet=prepare(mode,target);v.run_trace(p[direction]);boundaries=len(v.trace)
            delayed=immediate=0;observed_delayed_max=0
            for arrival in range(boundaries):
                packet=prepare(mode,target)
                for i,r in enumerate(REGS):v.u.reg_write(r,0x11220000+i)
                v.u.reg_write(UC_ARM_REG_SP,SP);v.u.reg_write(UC_ARM_REG_LR,STOP|1)
                v.u.reg_write(UC_ARM_REG_XPSR,0x01000000)
                state=dict(index=0,pending=False,fired=False,paused=False,wait=0,stores=[])
                def code(u,a,s,d):
                    if state['index']==arrival and not state['fired']:state['pending']=True
                    state['index']+=1
                    if state['pending'] and not state['fired']:
                        if u.reg_read(UC_ARM_REG_PRIMASK)==0:
                            state['paused']=True;u.emu_stop()
                        else:state['wait']+=1
                def write(u,access,a,size,value,d):
                    pc=u.reg_read(UC_ARM_REG_PC)
                    if a in [RAM+p['fec'],RAM+p['power']] and (p['positive']<=pc<p['positive']+0x500 or p['negative']<=pc<p['negative']+0x500):
                        current=v.rb(p['mode'])&3
                        assert current==(0 if a==RAM+p['fec'] else 1),(model,mode,direction,arrival,hex(pc),current)
                        assert u.reg_read(UC_ARM_REG_PRIMASK)==1
                        state['stores'].append(dict(pc=hex(pc),parameter='FEC' if a==RAM+p['fec'] else 'POWER',mode=current))
                hc=v.u.hook_add(UC_HOOK_CODE,code);hw=v.u.hook_add(UC_HOOK_MEM_WRITE,write)
                v.u.emu_start(p[direction]|1,STOP,count=5000)
                assert state['paused'],(model,mode,direction,arrival,state)
                context=v.u.context_save();resume=v.u.reg_read(UC_ARM_REG_PC)
                v.u.hook_del(hc)
                v.u.reg_write(UC_ARM_REG_SP,v.u.reg_read(UC_ARM_REG_SP)-0x100)
                v.u.reg_write(UC_ARM_REG_LR,STOP|1);next_byte[0]=packet[-1]
                v.u.emu_start(q['isr']|1,STOP,count=20000)
                assert v.u.reg_read(UC_ARM_REG_PC)==STOP and len(writer_hits)==1
                assert v.rb(p['mode'])&3==target
                state['fired']=True
                v.u.context_restore(context)
                v.u.emu_start(resume|1,STOP,count=5000)
                v.u.hook_del(hw)
                assert v.u.reg_read(UC_ARM_REG_PC)==STOP and v.u.reg_read(UC_ARM_REG_SP)==SP
                assert v.u.reg_read(UC_ARM_REG_PRIMASK)==0 and v.rb(p['selector'])==0
                assert state['stores']
                for i in range(4,12):assert v.u.reg_read(REGS[i])==0x11220000+i
                delayed+=bool(state['wait']);immediate+=not bool(state['wait'])
                observed_delayed_max=max(observed_delayed_max,state['wait'])
            results.append(dict(model=model,case='TC-04' if model=='V100F' else 'TC-08',from_mode=mode,to_mode=target,
                direction=direction,arrival_boundaries=boundaries,delayed=delayed,immediate=immediate,
                maximum_deferred_instructions=observed_delayed_max,stale_mode_stores=0))
    # Existing masked context must not be accidentally enabled by any wrapper.
    for direction in ['positive','negative','decoder']:
        v.seed();v.u.reg_write(UC_ARM_REG_PRIMASK,1);v.call(p[direction])
        assert v.u.reg_read(UC_ARM_REG_PRIMASK)==1
    v.u.reg_write(UC_ARM_REG_PRIMASK,0)
report=dict(candidate_sha256=sha(IMAGE),publication_scope='V480F_ONLY_PUBLIC_RERUN',status='PASS_CONDITIONAL_IRQ_MODEL',injection_cases=sum(r['arrival_boundaries'] for r in results),results=results,
    helper_hashes={m:META['helper_sha256'] for m in Q},
    closure={'TC-08':'CLOSED_FOR_V2_INSTRUCTION_MODEL'},
    real_stock_isr_and_checksum=True,stale_mode_stores=0,hardware_tested=False,
    limitations=['UART calls stubbed; synthetic full valid packet','Pending IRQ delivery follows PRIMASK in harness; not peripheral/NVIC emulation',
                 'NMI/HardFault are not masked; no identified normal UI mode writer through those exceptions',
                 'No measured wall-clock IRQ latency or hardware acceptance proof'])
DEST.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
