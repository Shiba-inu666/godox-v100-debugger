import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'debug'))
from device_engine import Engine,SETTINGS
class DeviceModes(unittest.TestCase):
    def test_role_state_and_close(self):
        e=Engine()
        for name,page,role in [('hotshoe',0,0),('sender',1,3),('receiver',2,4)]:
            e.action('role',name);s=e.snapshot()
            self.assertEqual((e.vm.rb(0x59f),e.vm.rb(0x398),e.vm.rb(0x33c)),(page,page,role))
            e.action('touch',s['entries'][0]['key']);e.action('role',name)
            self.assertFalse(e.editor);self.assertEqual(e.vm.rb(0x4e5),0)
    def test_hotshoe_fec_and_power(self):
        e=Engine();e.action('role','hotshoe');e.action('flash_mode','TTL');e.action('touch','MAIN')
        for _ in range(12):e.action('rotate',1)
        self.assertEqual(e.snapshot()['main']['label'],'+3.0 EV')
        for _ in range(25):e.action('rotate',-1)
        self.assertEqual(e.snapshot()['main']['label'],'−3.0 EV')
        e.action('flash_mode','M');e.action('touch','MAIN');before=e.vm.rb(0x4c0)
        for _ in range(30):e.action('rotate',1)
        self.assertEqual(e.snapshot()['main']['label'],'1/1');self.assertEqual(e.vm.rb(0x4c0),before)
    def test_receiver_each_group_isolation(self):
        for name in 'ABCDE':
            e=Engine();e.action('role','receiver');e.action('rx_group',name);i=ord(name)-64
            before=[e.vm.rb(0x4d0+j) for j in range(6)]
            e.action('touch','MAIN');e.action('rotate',-1)
            self.assertNotEqual(e.vm.rb(0x4d0+i),before[i])
            for j in range(6):
                if j!=i:self.assertEqual(e.vm.rb(0x4d0+j),before[j])
            self.assertEqual(e.vm.rb(0x4c0),50)
            self.assertNotIn('SUB',[x['key'] for x in e.snapshot()['entries']])
    def test_receiver_address_filter(self):
        e=Engine();e.action('role','receiver');e.action('rx_group','C')
        before=e.vm.rb(0x4d3)
        e.action('rx_inject',dict(command='power',value=50,destination=10));self.assertEqual(e.vm.rb(0x4d3),before)
        e.action('rx_inject',dict(command='power',value=50,destination=12));self.assertEqual(e.vm.rb(0x4d3),50)
        e.action('rx_inject',dict(command='mode',value=2,destination=12));self.assertEqual(e.snapshot()['flash_mode'],'Multi')
        e.action('rx_inject',dict(command='times',value=25,destination=12));e.action('rx_inject',dict(command='hz',value=30,destination=12))
        self.assertEqual(e.snapshot()['multi'],dict(times=25,hz=30))
    def test_receiver_ttl_readonly(self):
        e=Engine();e.action('role','receiver');e.action('flash_mode','TTL');e.action('touch','MAIN');before=e.capture();e.action('rotate',1)
        self.assertEqual(before,e.capture());self.assertEqual(e.snapshot()['main']['label'],'TTL')
    def test_multi_ranges_all_roles(self):
        for role in ['hotshoe','sender','receiver']:
            e=Engine();e.action('role',role);e.action('flash_mode','Multi');e.action('touch','MAIN')
            for _ in range(10):e.action('rotate',1)
            self.assertEqual(e.snapshot()['main']['raw'],20)
            for _ in range(10):e.action('rotate',-1)
            self.assertEqual(e.snapshot()['main']['raw'],80)
            for key,field in [('TIMES','times'),('HZ','hz')]:
                e.action('touch',key)
                for _ in range(35):e.action('rotate',1)
                self.assertEqual(e.snapshot()['multi'][field],100)
                for _ in range(35):e.action('rotate',-1)
                self.assertEqual(e.snapshot()['multi'][field],1)
    def test_menu_fields_and_exit(self):
        e=Engine();e.action('role','hotshoe');e.action('touch','SUB');e.action('back');e.action('menu')
        for key,cfg in SETTINGS.items():
            e.action('touch',key)
            if cfg['off'] is not None:
                index=len(cfg['options'])-1;e.action('setting',dict(key=key,index=index))
                self.assertEqual(e.vm.rb(cfg['off']),index+cfg.get('base',0))
            e.action('back')
        e.action('back');self.assertEqual(e.snapshot()['panel'],'main');self.assertEqual(e.snapshot()['focus'],'SUB')
    def test_multimode_replay(self):
        e=Engine()
        for a,v in [('role','hotshoe'),('flash_mode','Multi'),('touch','TIMES'),('rotate',1),('role','receiver'),('rx_group','E'),('rx_inject',dict(command='power',value=33,destination=14)),('menu',None),('setting',dict(key='TCM',index=1))]:e.action(a,v)
        s=e.session();self.assertEqual(s['schema'],3);r=Engine.restore(s)
        self.assertEqual(e.capture(),r.capture());self.assertEqual(e.snapshot()['panel'],r.snapshot()['panel'])
        e.action('undo');self.assertEqual(e.vm.rb(0x12f2),0);e.action('redo');self.assertEqual(e.vm.rb(0x12f2),1)
    def test_invalid_rx_command_preserves_state(self):
        e=Engine();e.action('role','receiver');before=e.capture()
        with self.assertRaises(ValueError):e.action('rx_inject',dict(command='fire',value=1))
        self.assertEqual(e.capture(),before)
        with self.assertRaises(ValueError):e.action('touch','SUB')
        self.assertEqual(e.capture(),before)
if __name__=='__main__':unittest.main()
