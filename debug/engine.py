"""Bounded original Thumb execution with an explicit host-side UI adapter."""
import copy
import struct
from stock_vm import StockVM, RAM, SHA
from formatters import power_label, display
ORDER=['M','SUB','A','B','C','D','ZOOM','ALL_ADJUST']
GROUPS=['M','A','B','C','D']
MODES=['TTL','M','OFF']
WATCH={0x26:'整体调整低字节',0x27:'整体调整高字节',0x36:'输入锁',0x5a:'功率步进',0x33c:'无线角色',0x3da:'组启用位',0x496:'SU-1 连接',0x4b4:'原厂组索引',0x4c0:'SUB 功率',0x4c1:'SUB 开关',0x4ca:'ZOOM',0x4e5:'编辑 selector',0x59f:'页面',0x12f0:'功率显示',0x12f8:'ZOOM 格式',0x1306:'信道'}
for i,n in enumerate(GROUPS):
    WATCH.update({0x4c4+i:n+' 模式',0x4d0+i:n+' 功率',0x4ef+i:n+' FEC',0x504+i:n+' 启用'})
GUI_STUBS=[0x0803e6e6,0x080311d8,0x08036ab0,0x0803e87a,0x0803e6fe,0x0803c608,0x0803aa02,0x0803a0da,0x0803ce42,0x0803e0b4,0x0802492c,0x08036db8,0x08036c10]
class Engine:
    def __init__(self):
        self.timeline=[];self.cursor=0;self._initialize()
    def _initialize(self):
        self.vm=StockVM();self.vm.seed()
        self.focus=0;self.editor=False;self.active=True;self.generation=1
        self.logs=[];self.seq=0;self.radio=[];self.record=None
        self.vm.wb(0x4ca,0x14);self.vm.wb(0x4cc,4);self.vm.wb(0x12f8,1)
        self.vm.ww(0x1758,RAM+0x13000);self.vm.ww(0x1774,RAM+0x13100)
        self.vm.wb(0x5a,1)  # Seeded test fixture, not hardware defaults.
        self.vm.wb(0x3da,31)
    def capture(self):
        return {f'0x{RAM+x:08X}':self.vm.rb(x) for x in WATCH}
    def call(self,fn,*args):
        self.calls.append(f'0x{fn:08X}')
        hs=[self.vm.stub(a) for a in GUI_STUBS]
        try:return self.vm.call(fn,*args)
        finally:
            for h in hs:self.vm.u.hook_del(h)
    def callback(self,entry,target,event=4,checked=0):
        v=self.vm;checks={}
        hs=[v.stub(0x08035f3c,lambda a:event),v.stub(0x08035fb4,lambda a:target),v.stub(0x08035f44,lambda a:target),v.stub(0x08035f68,lambda a:v.rw(0x9e0)),v.stub(0x0803c620,lambda a:checked if event==0x1c else checks.get(a[0],0)&a[1]),v.stub(0x0803a14e,lambda a:checks.__setitem__(a[0],checks.get(a[0],0)|a[1]) or 0),v.stub(0x0803aa7c,lambda a:checks.__setitem__(a[0],checks.get(a[0],0)&~a[1]) or 0),v.stub(0x08051aa0)]
        try:self.call(entry,RAM+0xf500)
        finally:
            for h in hs:v.u.hook_del(h)
    def close(self):
        # Original Sender clear-selection path; SUB origin lifetime remains host-managed.
        self.callback(0x0801bf44,0)
        self.editor=False
    def open(self):
        n=ORDER[self.focus]
        if n=='SUB':
            self.vm.ww(0x1574,RAM+0x12000)
            self.callback(0x0801a490,RAM+0x12000)
        else:
            off=0x1758 if n=='ZOOM' else 0x1774 if n=='ALL_ADJUST' else 0x15b8+4*GROUPS.index(n)
            self.callback(0x0801bbe8,self.vm.rw(off))
        self.editor=True
    def action(self,action,value=None):
        if action in ['undo','redo']:
            end=self.cursor+(-1 if action=='undo' else 1)
            if not 0<=end<=len(self.timeline):raise ValueError('没有可撤销/重做的操作')
            self._initialize()
            for entry in self.timeline[:end]:self._apply(entry['action'],entry.get('value'))
            self.cursor=end
            return self.snapshot()
        if action=='reset':
            self.timeline=[];self.cursor=0;self._initialize();return self.snapshot()
        if len(self.timeline[:self.cursor])>=1000:raise ValueError('本会话已达 1000 步，请导出后重置')
        # Roll back any partially completed native call on error.
        ram=bytes(self.vm.u.mem_read(RAM,0x20000))
        ui=(self.focus,self.editor,self.active,self.generation)
        try:self._apply(action,value)
        except Exception:
            self.vm.u.mem_write(RAM,ram)
            self.focus,self.editor,self.active,self.generation=ui
            raise
        self.timeline=self.timeline[:self.cursor]+[dict(action=action,value=value)]
        self.cursor+=1
        return self.snapshot()
    def _apply(self,action,value):
        before=self.capture();self.calls=[];output=[];v=self.vm
        if action=='page':
            if value not in ['sender','away']:raise ValueError('未知页面')
            self.close();self.active=value=='sender';self.generation+=1
            v.wb(0x59f,1 if self.active else 0)
            if self.active:self.focus=0
        elif action in ['decimal','presence','lock','sensor']:
            if type(value) is not bool:raise ValueError('选项需要布尔值')
            off={'decimal':0x12f0,'presence':0x496,'lock':0x36,'sensor':0x12f8}[action]
            v.wb(off,(2 if value else 0) if action=='lock' else int(value))
        elif action=='step':
            if type(value) is not int or value not in [0,1]:raise ValueError('未知步进')
            v.wb(0x5a,value)
        elif not self.active:raise ValueError('请先返回 Sender 页面')
        elif action in ['select','touch']:
            if value not in ORDER:raise ValueError('未知目标')
            if self.editor:self.close()
            self.focus=ORDER.index(value)
            if action=='touch':self.open()
        elif action=='back':
            if self.editor:self.close()
        elif action=='set':
            self.close() if self.editor else self.open()
        elif action=='rotate':
            if type(value) is not int or value not in [-1,1]:raise ValueError('旋转方向无效')
            if self.editor:self.call(0x08010924 if value==1 else 0x0800ba84)
            elif not v.rb(0x36)&2:self.focus=max(0,min(7,self.focus+value))
        elif action=='mode':
            n=ORDER[self.focus]
            if n not in GROUPS or value not in MODES:raise ValueError('只能设置原有五个目标的模式')
            i=GROUPS.index(n);obj=v.rw(0x15b8+4*i)
            for _ in range(3):
                if v.rb(0x4c4+i)==MODES.index(value):break
                self.callback(0x0801bbe8,obj,5)
                self.callback(0x0801bbe8,obj,6)
            self.callback(0x0801bbe8,obj,5)
        elif action=='toggle':
            if not self.editor or ORDER[self.focus]!='SUB':raise ValueError('请先打开 SUB 编辑页')
            self.callback(0x0801a924,RAM+0x12000,0x1c,1-v.rb(0x4c1))
        elif action=='zoom_auto':
            if not self.editor or ORDER[self.focus]!='ZOOM':raise ValueError('请先打开 ZOOM')
            if type(value) is not bool:raise ValueError('无效 ZOOM 选项')
            # Explicit host fixture selection; rotary changes still execute stock code.
            v.wb(0x4ca,v.rb(0x4cc) if value else (0x10|(v.rb(0x4ca)&15)))
        elif action=='channel':
            if type(value) is not int or not 1<=value<=32:raise ValueError('信道范围 1–32')
            old=v.rb(0x4e5);v.wb(0x4e5,10)
            try:
                for _ in range(32):
                    if v.rb(0x1306)==value-1:break
                    self.call(0x08010924)
            finally:v.wb(0x4e5,old)
            if v.rb(0x1306)!=value-1:raise ValueError('输入锁定，信道未改变')
        elif action=='radio':
            self.calls.append('0x080184D4');result=v.packets()
            output=result['frames'];self.radio=result['frames']
        elif action=='serialize':
            self.call(0x0800b7c0,RAM+0x1a000)
            self.record=bytes(v.u.mem_read(RAM+0x1a000,0x4f)).hex()
            output=['79-byte settings record',self.record]
        else:raise ValueError('不支持的操作')
        after=self.capture();self.seq+=1
        self.logs.append(dict(seq=self.seq,action=action,value=value,calls=self.calls.copy(),diff={k:[val,after[k]] for k,val in before.items() if after[k]!=val},output=output,generation=self.generation))
        self.logs=self.logs[-300:]
    def session(self):
        return dict(schema=2,firmware_sha256=SHA,actions=copy.deepcopy(self.timeline[:self.cursor]))
    @classmethod
    def restore(cls,data):
        if not isinstance(data,dict) or data.get('schema')!=2 or data.get('firmware_sha256')!=SHA:raise ValueError('会话格式或固件哈希不匹配')
        actions=data.get('actions')
        if not isinstance(actions,list) or len(actions)>1000:raise ValueError('会话操作数无效')
        result=cls()
        for item in actions:
            if not isinstance(item,dict) or set(item)-{'action','value'} or item.get('action') in ['reset','undo','redo']:raise ValueError('会话操作无效')
            result.action(item.get('action'),item.get('value'))
        return result
    def snapshot(self):
        v=self.vm;decimal=v.rb(0x12f0);groups=[]
        for i,n in enumerate(GROUPS):
            mode=v.rb(0x4c4+i);raw=v.rb(0x4d0+i);fec=v.rb(0x4ef+i)
            groups.append(dict(name=n,stock_index=i,mode=mode,mode_label=MODES[mode],raw=raw,fec=fec,label=display('fec',fec) if mode==0 else power_label(raw,decimal) if mode==1 else 'OFF'))
        amount=struct.unpack('<h',v.u.mem_read(RAM+0x26,2))[0]
        p=v.rb(0x4c0)
        return dict(version=2,focus=ORDER[self.focus],editor=self.editor,active=self.active,generation=self.generation,decimal=decimal,presence=bool(v.rb(0x496)),locked=bool(v.rb(0x36)&2),step=v.rb(0x5a),sensor=bool(v.rb(0x12f8)),channel=v.rb(0x1306)+1,zoom=dict(raw=v.rb(0x4ca),auto=v.rb(0x4ca)<16,label=display('zoom',v.rb(0x4ca),v.rb(0x12f8))),all_adjust=f'{amount/10:+.1f}',sub=dict(raw=p,enabled=bool(v.rb(0x4c1)),label=power_label(p,decimal)),groups=groups,memory=self.capture(),watch={f'0x{RAM+k:08X}':val for k,val in WATCH.items()},logs=self.logs,radio=self.radio,record=self.record,sha256=SHA,undo=self.cursor>0,redo=self.cursor<len(self.timeline),steps=self.cursor,hardware=False,fire=False)
