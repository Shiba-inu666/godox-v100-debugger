"""Verify actual native glyph lookup and bitmap, not just label text/geometry."""
from revision_vm import *
from unicorn import UC_HOOK_CODE
from collections import Counter
from itertools import product
import struct,zlib

counts=Counter();glyphs=[];samples=[]
raw=RAW
def glyph(v,font,ch):
    callback,bitmap=struct.unpack_from('<2I',raw,font-0x08008000)
    v.u.mem_write(0x200e0000,bytes(32))
    ok=v.call(callback,font,0x200e0000,ord(ch),0)
    desc=bytes(v.u.mem_read(0x200e0000,16))
    if not ok:return dict(font=hex(font),letter=ch,found=False)
    _,advance,w,h,x,y,bpp,_=struct.unpack('<IHHHhhBB',desc)
    ptr=v.call(bitmap,font,ord(ch));assert ptr and w and h and bpp==4
    pixels=bytes(v.u.mem_read(ptr,(w*h+1)//2))
    levels=[k for b in pixels for k in [b>>4,b&15]][:w*h]
    assert min(levels)==0 and max(levels)==15
    return dict(font=hex(font),letter=ch,found=True,advance=advance,width=w,height=h,x=x,y=y,bitmap_address=hex(ptr),bitmap_sha256=sha(pixels),levels=levels)

v=RevisionVM()
for c in 'SUB':
    g=glyph(v,0x0805b304,c);assert not g['found'];glyphs.append(g)
    counts['R6_sender_numeric_font_has_no_letter_glyph']+=1
for font in [0x080bbbe8,0x08053084]:
    g=glyph(v,font,'S');assert g['found'];glyphs.append(g)
    counts['R7_real_native_S_bitmap_exists']+=1
    # A direct bitmap proof of S, not a simulated LCD screenshot.
    scale=8;w,h=g['width']*scale,g['height']*scale
    scan=b''.join(b'\0'+bytes(g['levels'][(y//scale)*g['width']+x//scale]*17 for x in range(w)) for y in range(h))
    def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b))
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',w,h,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(scan))+chunk(b'IEND',b'')
    (ROOT/'analysis'/f'S_glyph_{font:08x}.png').write_bytes(png)

for page,language,on,decimal in product([1,2],[0,1],[0,1],[0,1]):
    v=RevisionVM();fonts={}
    def watch(u,a,s,d):
        obj,font,_=v.args(3);fonts[obj]=font
    hook=v.u.hook_add(UC_HOOK_CODE,watch,begin=0x0803e85c,end=0x0803e85c)
    v.wb(0x12fa,language);v.wb(0x12f0,decimal);v.wb(0x4c1,on);v.create(page);v.render()
    title=v.rw(0x1554);font=fonts[title]
    assert v.text(title)=='S' and font==(0x080bbbe8 if page==1 else 0x08053084)
    g=glyph(v,font,'S');assert g['found']
    x,y,right,bottom=v.coords(title);rx,ry,rr,rb=v.coords(v.rw(0x1550))
    assert rx<=x<=right<=rr and ry<=y<=bottom<=rb
    if page==1:assert right<rx+46 and abs((x+right)/2-(rx+23))<=2
    samples.append(dict(page=page,language=language,on=on,decimal=decimal,font=hex(font),title_rect=[x,y,right,bottom]))
    counts['native_page_label_glyph_style_and_bounds']+=1
    v.wb(0x4c0,47);v.function('sub_refresh');v.event(v.rw(0x1550));v.event(v.rw(0x1570));v.render()
    assert v.text(title)=='S' and fonts[title]==font
    assert v.coords(title)==(x,y,right,bottom)
    counts['native_refresh_editor_close_preserves_S']+=1
    v.u.hook_del(hook)

r=dict(status='PASS_R7_NATIVE_S_GLYPH',candidate_sha256=sha(IMAGE),counts=dict(counts),total=sum(counts.values()),glyphs=[{k:v for k,v in g.items() if k!='levels'} for g in glyphs],samples=samples,hardware_verified=False,limits=['Native font callbacks and bitmap bytes verified; no physical LCD confirmation','R6 checked label strings and geometry but did not check font character coverage; this test closes that gap'])
(ROOT/'analysis/GLYPH_RESULTS.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['status','total','counts']},indent=2))
