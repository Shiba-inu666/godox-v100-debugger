"""Execute original display functions with text-widget sinks."""
from functools import lru_cache
from stock_vm import StockVM, RAM, native_formatter

power_label = lru_cache(maxsize=256)(lambda raw, decimal: native_formatter(raw, decimal)['label'])

@lru_cache(maxsize=256)
def display(kind, raw, sensor=1):
    v=StockVM();v.seed();out={}
    fn,off=(0x0801efc4,0x4ef) if kind=='fec' else (0x0800c3d4,0x4ca)
    v.wb(off,raw);v.wb(0x12f8,sensor)
    def text(args):
        fmt=bytes(v.u.mem_read(args[1],80)).split(b'\0')[0].decode('utf-8')
        count=fmt.count('%d')
        out[args[0]]=fmt%tuple(args[2:2+count]) if count else fmt
        return 0
    hs=[v.stub(a,text) for a in [0x08039520,0x08039596]]
    hs += [v.stub(a) for a in [0x0803e85c,0x0803a212,0x0803a22e,0x08047b10,0x080311fc,0x0803e844,0x0803e6e6]]
    try:v.call(fn,*[RAM+0x8000+16*i for i in range(7)],RAM+off)
    finally:
        for h in hs:v.u.hook_del(h)
    if kind=='fec':
        value=out[RAM+0x8000]
        # Original font glyphs U+E685 = plus, U+E686 = minus.
        sign='+' if out[RAM+0x8020]=='\ue685' else '−'
        return ('0.0' if value=='0.0' else sign+value)+' EV'
    return out[RAM+0x8040]+' '+out[RAM+0x8030]+' mm'
