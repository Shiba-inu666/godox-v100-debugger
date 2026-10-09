"""Execute native RX drawer layout, sibling order, touch search, focus and events.

Touch search is the stock recursive routine, not a rectangle model. LCD transfer
and raw touch-controller input are outside this bounded offline test.
"""
from revision_vm import *
from itertools import product
from collections import Counter
import struct

counts=Counter(); evidence=[]
def snapshot(v):
    return [bytes(v.u.mem_read(a,n)) for a,n in [(0x20000000,0x100000),(0x10000000,0x10000)]]
def restore(v,data):
    for a,b in zip([0x20000000,0x10000000],data):v.u.mem_write(a,b)
def index(v,obj):return v.call(0x0803b6e2,obj)
def hit(v,root,x,y):
    v.u.mem_write(0x200e0000,struct.pack('<hh',x,y))
    return v.call(0x08038604,root,0x200e0000)
def descendant(v,obj,ancestor):
    for _ in range(32):
        if obj==ancestor:return True
        if not obj:return False
        obj=v.call(0x0803b788,obj)
    raise AssertionError('Parent cycle')
def drawer(v,opened):
    v.event(v.rw(0x13b4),9)
    v.call(0x0803e0b4,v.rw(0x13b8 if opened else 0x13bc),0)
    v.event(v.rw(0x13b4),11)
    v.event(v.rw(0x13b4),10)
    v.render()
    assert v.rb(0x748)==int(opened)
def group(v):
    g=v.rw(0x9e8);node=v.call(0x080218f6,g);out=[]
    for _ in range(32):
        if not node:return out
        out.append(struct.unpack('<I',v.u.mem_read(node,4))[0])
        node=v.call(0x0802191e,g,node)
    raise AssertionError('Focus cycle too large')
def make(image=IMAGE,page=2):
    v=RevisionVM(image=image);v.wb(0x5a1,0);root=v.create(page);v.render();return v,root

# Reproduce the user's overlap in the previously delivered complete binary.
r5=transform(RAW,load_spec('r5'));assert sha(r5)=='7cb6a3a634a366adc0ae166ae6e1c35781a6e2989020db45fe1b2d3647a23244'
old,oldroot=make(r5);drawer(old,True)
assert index(old,old.rw(0x1550))>index(old,old.rw(0x13b4))
assert hit(old,oldroot,380,320)==old.rw(0x1550)
counts['R5_observed_overlap_reproduced_native_touch_search']+=1
evidence.append(dict(version='R5',SUB_index=index(old,old.rw(0x1550)),drawer_index=index(old,old.rw(0x13b4)),target_at_380_320='SUB'))

v,root=make();base=snapshot(v)
assert v.coords(v.rw(0x1550))==(324,304,479,358)
assert index(v,v.rw(0x1550))+1==index(v,v.rw(0x13b4))
counts['R6_same_geometry_immediately_below_native_drawer']+=1
evidence.append(dict(version='R7',SUB_index=index(v,v.rw(0x1550)),drawer_index=index(v,v.rw(0x13b4)),SUB_rectangle=v.coords(v.rw(0x1550))))
points=[(330,310),(380,320),(400,330),(420,322),(470,350)]
for mode,decimal,language,on,present in product([0,1],[0,1],[0,1],[0,1],[0,1]):
    restore(v,base)
    for o,b in [(0x4c3,mode),(0x12f0,decimal),(0x12fa,language),(0x4c1,on),(0x496,present)]:v.wb(o,b)
    v.wb(0x38c,255);v.function('sub_refresh');v.render()
    if present:assert hit(v,root,380,320)==v.rw(0x1550)
    else:assert not descendant(v,hit(v,root,380,320),v.rw(0x1550))
    drawer(v,True)
    for x,y in points:
        target=hit(v,root,x,y)
        assert descendant(v,target,v.rw(0x13b4)) and not descendant(v,target,v.rw(0x1550))
        counts['open_drawer_native_touch_priority_matrix']+=1
    assert hit(v,root,380,320)==v.rw(0x148c)
    assert v.coords(v.rw(0x148c))==(66,303,413,336)
    assert v.focus()==v.rw(0x13c8)
    assert v.rw(0x1550) not in group(v)
    counts['brightness_slider_and_drawer_focus_matrix']+=1
    power=v.rb(0x4c0)
    # A click delivered to the actual target must not open the hidden SUB editor.
    v.event(hit(v,root,380,320))
    assert not v.rw(0x156c) and v.rb(0x4c0)==power
    counts['actual_brightness_target_click_cannot_open_SUB']+=1
    drawer(v,False)
    assert bool(v.rw(0x1550) in group(v))==bool(present)
    if present:
        assert hit(v,root,380,320)==v.rw(0x1550)
        v.event(hit(v,root,380,320));assert v.rw(0x156c)
        v.event(v.rw(0x1570));assert not v.rw(0x156c)
    counts['close_restores_main_focus_and_SUB_modal_matrix']+=1

# Full native periodic refresh, attachment changes and scroll transition flags.
for page in [1,2]:
    w,wroot=make(page=page);drawer(w,True)
    initial_group=group(w);focus=w.focus()
    for present,power in product([0,1],[0,3,7,30,70]):
        w.wb(0x496,present);w.wb(0x4c0,power);w.call(0x080426bc);w.render()
        assert w.focus()==focus and group(w)==initial_group
        assert not w.rw(0x156c)
        counts['full_tick_attachment_power_changes_keep_drawer_focus']+=1
    drawer(w,False)
    assert w.rw(0x1550) in group(w)
    counts['native_close_restores_focus_after_hot_attachment']+=1
for flag in [0x74a,0x74b]:
    restore(v,base);v.wb(flag,1);focus=v.focus();g=group(v)
    v.wb(0x496,0);v.function('sub_refresh')
    assert v.focus()==focus and group(v)==g
    counts['scroll_in_progress_never_rebuilds_focus']+=1

restore(v,base)
for cycle in range(12):
    drawer(v,True);assert hit(v,root,380,320)==v.rw(0x148c)
    drawer(v,False);assert hit(v,root,380,320)==v.rw(0x1550)
    assert index(v,v.rw(0x1550))+1==index(v,v.rw(0x13b4))
    counts['repeated_open_close_stable_layer_and_hit_target']+=1

# Screens deliberately constructed without the optional drawer remain valid.
w=RevisionVM();wr=w.create(2);w.render();row=w.rw(0x1550)
assert hit(w,wr,380,320)==row
w.call(0x0800d574,wr);w.render()
assert index(w,w.rw(0x13b4))>index(w,row)
drawer(w,True);assert hit(w,wr,380,320)==w.rw(0x148c)
counts['absent_then_late_native_drawer_safe']+=1

# A live pointer from a different screen must never reorder that screen's child.
w,prior=make(page=0);foreign=w.rw(0x13b4);before=index(w,foreign)
w.wb(0x5a1,1);wr=w.create(2);w.render()
assert w.rw(0x13b4)==foreign and w.call(0x0803b788,foreign)==prior
assert index(w,foreign)==before and w.call(0x0803b788,w.rw(0x1550))==wr
assert hit(w,wr,380,320)==w.rw(0x1550)
counts['foreign_screen_drawer_ownership_guard']+=1

r=dict(status='PASS_R6_NATIVE_DRAWER_LAYER_AND_HIT_TEST',candidate_sha256=sha(IMAGE),baseline_sha256=sha(r5),counts=dict(counts),total=sum(counts.values()),evidence=evidence,hardware_verified=False,limits=['Executes native LVGL sibling ordering, recursive touch search, immediate scroll, callbacks and focus','Physical LCD compositing, touch controller and animated gesture timing require hardware confirmation','No firing logic change in this revision'])
(ROOT/'analysis/DRAWER_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
