import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'debug'))
from device_engine import Engine
from formatters import display
class Workflows(unittest.TestCase):
    def test_all_modes_and_fec_limits(self):
        for name in ['M','A','B','C','D']:
            e=Engine();e.action('touch',name)
            e.action('mode','TTL');self.assertEqual(e.snapshot()['groups'][['M','A','B','C','D'].index(name)]['mode_label'],'TTL')
            for _ in range(12):e.action('rotate',1)
            g=next(g for g in e.snapshot()['groups'] if g['name']==name)
            self.assertEqual(g['label'],'+3.0 EV')  # Original glyph U+E685 is plus; raw FEC is inverted.
            for _ in range(25):e.action('rotate',-1)
            g=next(g for g in e.snapshot()['groups'] if g['name']==name)
            self.assertEqual(g['label'],'−3.0 EV')
            e.action('mode','OFF');before=e.capture();e.action('rotate',1);self.assertEqual(before,e.capture())
            e.action('mode','M');self.assertEqual(e.vm.rb(0x4c0),50)
    def test_zoom_and_footer_selector(self):
        e=Engine();e.action('touch','ZOOM');self.assertEqual(e.vm.rb(0x4e5),1)
        self.assertEqual(e.snapshot()['zoom']['label'],'M 50 mm')
        for _ in range(10):e.action('rotate',1)
        self.assertEqual(e.vm.rb(0x4ca),0x17)
        e.action('zoom_auto',True);self.assertTrue(e.snapshot()['zoom']['auto'])
        e.action('rotate',1);self.assertEqual(e.vm.rb(0x4ca),0x12)
        e.action('back');self.assertEqual(e.vm.rb(0x4e5),0)
        e.action('touch','ALL_ADJUST');self.assertEqual(e.vm.rb(0x4e5),25)
    def test_all_adjust_block_at_boundary(self):
        e=Engine();e.action('touch','ALL_ADJUST');before=[g['raw'] for g in e.snapshot()['groups']]
        e.action('rotate',1) # D already max, whole set cannot increase
        self.assertEqual(before,[g['raw'] for g in e.snapshot()['groups']])
        e.action('rotate',-1)
        self.assertEqual([43,33,23,13,3],[g['raw'] for g in e.snapshot()['groups']])
        self.assertEqual(e.vm.rb(0x4c0),50)
    def test_channel_step_undo_restore(self):
        e=Engine();e.action('channel',32);self.assertEqual(e.snapshot()['channel'],32)
        e.action('channel',1);e.action('step',0);e.action('touch','A');e.action('rotate',1)
        self.assertEqual(e.vm.rb(0x4d1),29)
        e.action('undo');self.assertEqual(e.vm.rb(0x4d1),30)
        e.action('redo');self.assertEqual(e.vm.rb(0x4d1),29)
        r=Engine.restore(e.session());self.assertEqual(e.capture(),r.capture())
        e.action('undo');e.action('rotate',-1);self.assertFalse(e.snapshot()['redo'])
    def test_reject_and_lock(self):
        e=Engine();e.action('touch','SUB');e.action('lock',True);before=e.capture();e.action('rotate',1);self.assertEqual(e.capture(),before)
        with self.assertRaises(ValueError):e.action('channel',5)
        self.assertEqual(e.capture(),before)
        with self.assertRaises(ValueError):Engine.restore({'schema':2,'firmware_sha256':'wrong','actions':[]})
    def test_display_all_fec_values(self):
        self.assertEqual(display('fec',0),'0.0 EV')
        self.assertEqual(display('fec',2),'−0.3 EV')
        self.assertEqual(display('fec',254),'+0.3 EV')
        for x in range(0,19,2):self.assertIn('EV',display('fec',x))
if __name__=='__main__':unittest.main()
