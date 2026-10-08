import sys,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'debug'))
from device_engine import Engine
class Sessions(unittest.TestCase):
    def test_v2_saved_session_loads(self):
        e=Engine();e.action('touch','SUB');e.action('rotate',1)
        data=e.session();data['schema']=2;r=Engine.restore(data)
        self.assertEqual(r.vm.rb(0x4c0),47);self.assertEqual(r.snapshot()['screen'],'sender')
    def test_menu_undo_role_change(self):
        e=Engine();e.action('role','hotshoe');e.action('menu');e.action('touch','SCREEN_SLEEP')
        e.action('setting',dict(key='SCREEN_SLEEP',index=3));e.action('role','receiver');e.action('undo')
        self.assertEqual(e.snapshot()['screen'],'hotshoe');self.assertEqual(e.snapshot()['panel'],'menu');self.assertEqual(e.snapshot()['focus'],'SCREEN_SLEEP')
        e.action('redo');self.assertEqual(e.snapshot()['screen'],'receiver')
    def test_invalid_settings_rollback(self):
        e=Engine();e.action('menu');before=e.session();memory=e.capture()
        with self.assertRaises(ValueError):e.action('setting',dict(key='BRIGHTNESS',index=200))
        self.assertEqual(e.capture(),memory);self.assertEqual(e.session(),before)
if __name__=='__main__':unittest.main()
