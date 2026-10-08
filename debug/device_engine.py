"""Three-role desktop adapter. Parameter/packet functions execute unmodified code."""
import copy
from engine import Engine as SenderEngine, GROUPS, ORDER, WATCH
from stock_vm import RAM, SHA
from formatters import display, power_label

ROLES={'hotshoe':(0,0,'Wi-Off'),'sender':(1,3,'Sender'),'receiver':(2,4,'Receiver')}
FLASH_MODES=['TTL','M','Multi']
# Enumerations taken from 0804AF9C and its original option strings.
SETTINGS={
 'DISPLAY':dict(title='功率显示',off=0x12f0,options=['分数 1/256','十进制 2.0']),
 'STEP':dict(title='功率步进',off=0x5a,options=['0.1 档','1/3 档']),
 'PHOTOCELL':dict(title='光控引闪',off=0x12f1,options=['OFF','S1','S2']),
 'TCM':dict(title='TCM',off=0x12f2,options=['OFF','ON']),
 'UNITS':dict(title='距离单位',off=0x12f3,options=['m','ft']),
 'STANDBY':dict(title='待机',off=0x12f4,options=['ON','OFF']),
 'AUTO_OFF':dict(title='自动关机',off=0x55,options=['OFF','ON']),
 'OFF_TIME':dict(title='自动关机时间',off=0x12f5,options=['30 min','60 min','90 min']),
 'MODEL_LIGHT':dict(title='造型灯行为',off=0x12f6,options=['持续','闪灭']),
 'BRIGHTNESS':dict(title='屏幕亮度',off=0x12fd,options=[str(i)+'%' for i in range(1,101)],base=1),
 'SCREEN_SLEEP':dict(title='屏幕待机',off=0x12fe,options=['30 s','1 min','2 min','3 min']),
 'ZOOM_FORMAT':dict(title='ZOOM 显示格式',off=0x12f8,options=['APS-C','全画幅']),
 'LANGUAGE':dict(title='设备语言设置',off=0x12fa,options=['中文','English']),
 'INFO':dict(title='设备信息',off=None,options=['V100 F · V1.03']),
}
WATCH.update({0x4c3:'全局闪光模式',0x398:'待切换页面',0x4eb:'机顶 FEC',0x4ac:'Multi 次数',0x4ad:'Multi 频率',0x503:'Receiver 组',0x33e:'Receiver 地址',0x4d5:'E 功率',0x4dc:'Multi 主槽功率'})
for key,cfg in SETTINGS.items():
 if cfg['off'] is not None:WATCH[cfg['off']]=cfg['title']
for i in range(1,6):WATCH[0x4dc+i]='Multi '+chr(64+i)+' 功率'

class Engine(SenderEngine):
    def _initialize(self):
        super()._initialize()
        self.screen='sender';self.panel='main';self.return_focus=0
        self.vm.wb(0x503,1);self.vm.wb(0x33e,10);self.vm.wb(0x1307,10)
        self.vm.wb(0x4ac,10);self.vm.wb(0x4ad,10);self.vm.wb(0x12fd,60)
        self.vm.u.mem_write(RAM+0x4dc,bytes([50]*6))
        self.vm.wb(0x4d5,50)
        self.vm.ww(0x604,RAM+0x9400);self.vm.ww(0x608,RAM+0x9500)
        for j,off in enumerate([0x17e4,0x1828,0x1844,0x1860]):self.vm.ww(off,RAM+0x14000+j*0x100)
        self.last_rx=None
    def order(self):
        if self.panel=='menu':return list(SETTINGS)
        if self.screen=='sender' and self.vm.rb(0x4c3)&3!=2:return ORDER
        if self.vm.rb(0x4c3)&3==2:return ['MAIN','TIMES','HZ','ZOOM']+(['GROUP'] if self.screen=='receiver' else [])
        return ['MAIN','ZOOM']+(['SUB'] if self.screen=='hotshoe' else [])+(['GROUP'] if self.screen=='receiver' else [])
    def name(self):return self.order()[min(self.focus,len(self.order())-1)]
    def close(self):
        if self.panel=='main' and self.screen=='sender':super().close()
        elif self.panel=='main' and self.screen=='receiver':
            self.callback(0x0801c350,0);self.editor=False
        else:self.vm.wb(0x4e5,0);self.editor=False
    def open(self):
        n=self.name();v=self.vm
        if self.panel=='menu':self.editor=True;return
        if self.screen=='sender' and v.rb(0x4c3)&3!=2:super().open();return
        if n=='SUB':
            v.ww(0x1574,RAM+0x12000);self.callback(0x0801a490,RAM+0x12000)
        elif self.screen=='receiver' and n in ['MAIN','ZOOM','GROUP']:
            off={'MAIN':0x17e4,'ZOOM':0x1844,'GROUP':0x1860}[n]
            self.callback(0x0801c18c,v.rw(off))
        else:
            selector={'MAIN':6 if v.rb(0x4c3)&3==0 else 2,'ZOOM':1,'TIMES':4,'HZ':3}[n]
            v.wb(0x4e5,selector) # Host event routing to confirmed stock selectors.
        self.editor=True
    def action(self,action,value=None):
        host=(self.screen,self.panel,self.return_focus,copy.deepcopy(self.last_rx))
        try:return super().action(action,value)
        except Exception:
            self.screen,self.panel,self.return_focus,self.last_rx=host
            raise
    def set_setting(self,key,index):
        if key not in SETTINGS:raise ValueError('未知设置')
        cfg=SETTINGS[key]
        if cfg['off'] is None:return
        if type(index) is not int or not 0<=index<len(cfg['options']):raise ValueError('设置值超出范围')
        v=self.vm
        if key in ['TCM','STANDBY','AUTO_OFF']:
            fn={'TCM':0x0801b670,'STANDBY':0x0801b5c0,'AUTO_OFF':0x0801b20c}[key]
            self.callback(fn,RAM+0x16000,0x1c,1-index if key=='STANDBY' else index)
        elif key in ['PHOTOCELL','UNITS','ZOOM_FORMAT']:
            slots={'PHOTOCELL':[0x1a44,0x1a50,0x1a5c],'UNITS':[0x1a74,0x1a80],'ZOOM_FORMAT':[0x1b70,0x1b7c]}[key]
            for i,slot in enumerate(slots):v.ww(slot,RAM+0x16100+i*0x100)
            h=v.stub(0x08051a1c)
            try:self.callback({'PHOTOCELL':0x0801b458,'UNITS':0x0801b828,'ZOOM_FORMAT':0x0801b760}[key],v.rw(slots[index]))
            finally:v.u.hook_del(h)
        else:v.wb(cfg['off'],index+cfg.get('base',0))
    def _apply(self,action,value):
        v=self.vm;before=self.capture();self.calls=[];output=[]
        if action=='role':
            if value not in ROLES:raise ValueError('未知无线角色')
            self.close();self.screen=value;self.panel='main';self.focus=0;self.active=True;self.generation+=1
            page,role,_=ROLES[value];v.wb(0x33c,role);v.wb(0x59f,page);v.wb(0x398,page)
        elif action=='flash_mode':
            if value not in FLASH_MODES:raise ValueError('未知闪光模式')
            self.close();v.wb(0x4c3,(v.rb(0x4c3)&0xfc)|FLASH_MODES.index(value));self.focus=0
        elif action=='menu':
            if self.panel=='menu':
                if self.editor:self.close()
                self.panel='main';self.focus=min(self.return_focus,len(self.order())-1)
            else:
                self.close();self.return_focus=self.focus;self.panel='menu';self.focus=0
        elif action=='page':
            if value not in ['sender','away','resume']:raise ValueError('未知页面')
            self.close();self.active=value!='away';self.panel='main';self.focus=0;self.generation+=1
            page,role,_=ROLES[self.screen];v.wb(0x59f,page if self.active else 0);v.wb(0x398,page)
        elif not self.active and action not in ['decimal','presence','lock','sensor','step']:raise ValueError('请先返回当前页面')
        elif action in ['select','touch']:
            if value not in self.order():raise ValueError('当前页面没有此控件')
            if self.editor:self.close()
            self.focus=self.order().index(value)
            if action=='touch':self.open()
        elif action=='back':
            if self.editor:self.close()
            elif self.panel=='menu':self.panel='main';self.focus=min(self.return_focus,len(self.order())-1)
        elif action=='set':self.close() if self.editor else self.open()
        elif action=='rotate':
            if type(value) is not int or value not in [-1,1]:raise ValueError('旋转方向无效')
            if not v.rb(0x36)&2:
                if not self.editor:self.focus=max(0,min(len(self.order())-1,self.focus+value))
                elif self.panel=='menu':
                    cfg=SETTINGS[self.name()]
                    if cfg['off'] is not None:
                        index=v.rb(cfg['off'])-cfg.get('base',0)
                        self.set_setting(self.name(),max(0,min(len(cfg['options'])-1,index+value)))
                elif self.screen=='receiver' and self.name()=='MAIN' and v.rb(0x4c3)&3==0:
                    output=['RX TTL 由发射端/相机控制，本地 FEC 编辑未开放']
                else:self.call(0x08010924 if value==1 else 0x0800ba84)
        elif action=='setting':
            if not isinstance(value,dict):raise ValueError('设置请求无效')
            self.set_setting(value.get('key'),value.get('index'))
        elif action=='rx_group':
            if self.screen!='receiver' or value not in list('ABCDE'):raise ValueError('需要 Receiver A–E 组')
            old=v.rb(0x4e5);v.wb(0x4e5,24)
            try:
                for _ in range(5):
                    if v.rb(0x503)==ord(value)-64:break
                    self.call(0x08010924)
            finally:v.wb(0x4e5,old)
            if v.rb(0x503)!=ord(value)-64:raise ValueError('锁定时无法切组')
        elif action=='rx_inject':
            if self.screen!='receiver' or not isinstance(value,dict):raise ValueError('仅 Receiver 支持模拟接收')
            command=value.get('command');val=value.get('value');dest=value.get('destination',v.rb(0x33e))
            rules={'mode':(0xb1,range(3)),'power':(0xbc,range(81)),'multi_power':(0xbd,[20,30,40,50,60,70,80]),'times':(0xbe,range(1,101)),'hz':(0xbf,range(1,101))}
            if command not in rules or type(val) is not int or val not in rules[command][1] or type(dest) is not int or dest not in range(10,15):raise ValueError('接收命令超出已验证参数范围')
            self.close();self.panel='main';self.focus=0
            code=rules[command][0];self.call(0x08017c80,dest,code,val,0)
            self.last_rx=dict(destination=dest,command=command,value=val,matched=dest==v.rb(0x33e));output=[self.last_rx]
        elif action=='radio' and self.screen!='sender':raise ValueError('发送编码只在 Sender 下可用')
        elif action=='mode' and (self.screen!='sender' or self.panel!='main' or v.rb(0x4c3)&3==2):raise ValueError('请使用页面顶部的闪光模式选项')
        elif action=='toggle' and not (self.panel=='main' and self.name()=='SUB' and self.editor):raise ValueError('当前页面无 SUB 编辑入口')
        elif action=='zoom_auto':
            if not self.editor or self.name()!='ZOOM' or type(value) is not bool:raise ValueError('请先打开 ZOOM')
            v.wb(0x4ca,v.rb(0x4cc) if value else (0x10|(v.rb(0x4ca)&15)))
        elif action=='toggle':self.callback(0x0801a924,RAM+0x12000,0x1c,1-v.rb(0x4c1))
        else:
            super()._apply(action,value);return
        after=self.capture();self.seq+=1
        self.logs.append(dict(seq=self.seq,action=action,value=value,calls=self.calls.copy(),diff={k:[val,after[k]] for k,val in before.items() if after[k]!=val},output=output,generation=self.generation))
        self.logs=self.logs[-300:]
    def session(self):
        s=super().session();s['schema']=3;return s
    @classmethod
    def restore(cls,data):
        if not isinstance(data,dict) or data.get('schema') not in [2,3]:raise ValueError('不支持的会话版本')
        return super().restore({**data,'schema':2})
    def snapshot(self):
        focus=self.focus
        try:
            self.focus=0;s=super().snapshot()
        finally:self.focus=focus
        v=self.vm;mode=v.rb(0x4c3)&3;n=self.name();idx=v.rb(0x503) if self.screen=='receiver' else 0
        raw=v.rb(0x4dc+idx) if mode==2 else v.rb(0x4d0+idx)
        main_label=('TTL' if self.screen=='receiver' else display('fec',v.rb(0x4eb))) if mode==0 else ('OFF' if raw==255 else power_label(raw,v.rb(0x12f0)))
        entries=[]
        for key in self.order():
            if self.panel=='menu':
                cfg=SETTINGS[key];i=0 if cfg['off'] is None else v.rb(cfg['off'])-cfg.get('base',0)
                entries.append(dict(key=key,title=cfg['title'],label=cfg['options'][max(0,min(len(cfg['options'])-1,i))],mode='设置',options=cfg['options'],index=i))
            elif key in GROUPS:
                g=next(g for g in s['groups'] if g['name']==key);entries.append(dict(key=key,title=key,label=g['label'],mode=g['mode_label']))
            else:
                label={'MAIN':main_label,'SUB':s['sub']['label'] if s['sub']['enabled'] else 'OFF','ZOOM':s['zoom']['label'],'ALL_ADJUST':s['all_adjust'],'TIMES':str(v.rb(0x4ac))+' 次','HZ':str(v.rb(0x4ad))+' Hz','GROUP':'Group '+chr(64+v.rb(0x503))}[key]
                entries.append(dict(key=key,title={'MAIN':'主灯','TIMES':'闪光次数','HZ':'频率','GROUP':'接收组','ALL_ADJUST':'整体调整'}.get(key,key),label=label,mode=FLASH_MODES[mode] if key=='MAIN' else ''))
        s.update(version=3,screen=self.screen,screen_label=ROLES[self.screen][2],panel=self.panel,focus=n,entries=entries,flash_mode=FLASH_MODES[mode],main=dict(label=main_label,raw=raw,fec=v.rb(0x4eb),slot=idx),multi=dict(times=v.rb(0x4ac),hz=v.rb(0x4ad)),rx_group=chr(64+v.rb(0x503)),last_rx=self.last_rx,device_settings={k:(0 if c['off'] is None else v.rb(c['off'])-c.get('base',0)) for k,c in SETTINGS.items()})
        return s
