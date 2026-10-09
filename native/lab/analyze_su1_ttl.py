"""Read-only feasibility observations; no TTL patch and no hardware writes.

Execute native camera parser/RF dispatcher and observe real joint-routine inputs.
Packets and peripheral readiness are synthetic, not a captured Fuji transaction.
"""
from fire_vm import *
from itertools import product
from collections import Counter

counts=Counter();records=[]
class Probe(FireVM):
    def __init__(self,image):
        self.joint=[];super().__init__(image)
    def observe(self,u,a,s,d):
        if a==0x0802a9ea:
            self.joint.append(dict(sub_duration_code=u.reg_read(UC_ARM_REG_R0),main_duration_code=u.reg_read(UC_ARM_REG_R1)))
        super().observe(u,a,s,d)
    def clear_trace(self):
        super().clear_trace();self.joint=[]
def feed(v,cmd,payload):
    p=v.p;v.stub(p['spi_irq_status'],lambda a:1);v.stub(p['spi_status'],lambda a:1);v.stub(p['spi_write'])
    packet=[cmd,*payload,(cmd+1+sum(payload))&255]
    for byte in packet:
        v.stub(p['spi_read'],lambda a,b=byte:b);v.call(p['parser'])
    return bytes(packet).hex()
def record(v,r,**context):
    records.append(dict(**context,main_trigger_requests=r['main_trigger_set_requests'],sub_trigger_request=r['sub'],main_duration_code=r['local_main_energy']['prepared_duration_code'],joint_inputs=v.joint.copy(),local_SUB_power=v.rb(0x4c0),radio_serial=r['radio_serial_hex']))
def joint_check(v,power):
    expect=struct.unpack_from('<H',RAW,0x080528d6-0x08008000+2*(80-power))[0]
    assert len(v.joint)==1 and v.joint[0]['sub_duration_code']==expect

for version,role,power in product(['stock','R7'],[0,3],[0,30,70]):
    v=Probe(RAW if version=='stock' else IMAGE);v.setup(role,0,power);v.wb(0x3d6,5);v.wb(0x512,0)
    packet=feed(v,0xb1,[40]);assert(v.rb(0x3e9),v.rb(0x512))==(1,8)
    v.clear_trace();r=v.run(0x0800edd4)
    assert r['main_trigger_set_requests']==1 and not r['sub'] and not v.joint and v.rb(0x4c0)==power
    counts['native_B1_camera_preflash_MAIN_only']+=1
    record(v,r,version=version,role=role,event='camera_B1_preflash',packet=packet)

main_values={}
for version,role,power,meter in product(['stock','R7'],[0,3],[0,30,70],[40,80,100]):
    v=Probe(RAW if version=='stock' else IMAGE);v.setup(role,0,power);v.wb(0x3d6,5);v.wb(0x512,0)
    packet=feed(v,0xb6,[0,0,meter,0,0,0,0]);assert(v.rb(0x3e9),v.rb(0x512),v.rb(0x513))==(0,10,meter)
    v.clear_trace();r=v.run(0x0800edd4);has_joint=(role==0 or version=='R7')
    assert r['main_trigger_set_requests']==1 and r['sub']==has_joint and v.rb(0x4c0)==power
    if has_joint:joint_check(v,power)
    else:assert not v.joint
    main_values.setdefault((version,role,power),set()).add(r['local_main_energy']['prepared_duration_code'])
    counts['camera_TTL_input_changes_MAIN_but_SUB_stays_manual']+=1
    record(v,r,version=version,role=role,event='camera_B6_normal_exposure',packet=packet,meter_input=meter)
assert all(len(values)==3 for values in main_values.values())

for version,power,meter in product(['stock','R7'],[0,30,70],[40,80,100]):
    v=Probe(RAW if version=='stock' else IMAGE);v.setup(4,0,power);v.wb(0x54c,5)
    v.packet([0xa9,10,0xb9,meter]);assert v.rb(0x514)==meter and v.rb(0x4c0)==power
    v.clear_trace();r=v.packet([0xa9,10,0xb4,1]);assert r['main_trigger_set_requests']==1 and not r['sub'] and not v.joint
    counts['RX_addressed_preflash_MAIN_only']+=1
    record(v,r,version=version,role=4,event='RF_B4_01_preflash',meter_input=meter)
    v.wb(0x50c,1);v.clear_trace();r=v.packet([0xa9,10,0xb4,9])
    assert r['main_trigger_set_requests']==1 and r['sub']==(version=='R7') and v.rb(0x4c0)==power
    if version=='R7':joint_check(v,power)
    else:assert not v.joint
    counts['RX_TTL_parameter_does_not_create_SUB_metering_channel']+=1
    record(v,r,version=version,role=4,event='RF_B4_09_exposure',meter_input=meter)

for version,power in product(['stock','R7'],[0,30,70]):
    v=Probe(RAW if version=='stock' else IMAGE);v.setup(3,0,power);v.wb(0x3d6,5);v.wb(0x512,0);v.wb(0x504,0)
    feed(v,0xb1,[40]);v.clear_trace();r=v.run(0x0800edd4)
    assert not r['main_trigger_set_requests'] and not r['sub'] and not v.joint
    counts['Sender_MAIN_OFF_has_no_local_SUB_preflash']+=1
    record(v,r,version=version,role=3,event='camera_B1_MAIN_OFF')

# No new TTL code: public candidate is hash-locked to R7.
assert sha(IMAGE)==load_spec()['modified_sha256']
report=dict(status='OBSERVATIONS_CONFIRMED_WITHIN_BOUNDED_MODEL_SU1_TTL_NOT_IMPLEMENTED',candidate_sha256=sha(IMAGE),original_sha256=sha(RAW),counts=dict(counts),total=sum(counts.values()),records=records,TTL_patch_generated=False,hardware_verified=False,limits=['Synthetic checked camera bytes and RF FIFO, no physical Fuji handshake or optical exposure measurement','Native arithmetic and joint pulse inputs executed; timing/transport and selected completion services stubbed','Only identified standard preflash and normal-sync routes; B4 camera alternate purpose and entire protocol not proven','Independent SUB TTL is not obtained by copying MAIN output; preflash participation and optical calibration remain unproven'])
(ROOT/'analysis/TTL_FEASIBILITY_RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','total','counts']},indent=2))
