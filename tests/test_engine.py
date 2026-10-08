import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'debug'))
from device_engine import Engine
class Tests(unittest.TestCase):
    def test_sub_isolation_and_lifecycle(self):
        e=Engine(); before=e.snapshot()['groups'];e.action('rotate',1)
        self.assertEqual(e.vm.rb(0x4c0),50)
        for _ in range(20):
            e.action('set');e.action('rotate',1);e.action('back')
            self.assertEqual(e.snapshot()['focus'],'SUB');self.assertFalse(e.editor)
        self.assertEqual(e.vm.rb(0x4c0),0);self.assertEqual(before,e.snapshot()['groups'])
        e.action('set');e.action('toggle');self.assertEqual(e.vm.rb(0x4c1),1)
        e.action('page','away');self.assertFalse(e.editor)
        with self.assertRaises(ValueError):e.action('rotate',1)
        e.action('page','sender');self.assertEqual(e.snapshot()['focus'],'M')
    def test_absence_and_boundary(self):
        e=Engine();e.action('select','SUB');e.action('set');e.action('presence',False)
        e.action('rotate',1);self.assertEqual(e.vm.rb(0x4c0),50)
        e.action('presence',True)
        for _ in range(30):e.action('rotate',-1)
        self.assertEqual(e.vm.rb(0x4c0),70)
    def test_group_index_and_save(self):
        e=Engine()
        for i,n in enumerate(['M','A','B','C','D']):
            e.action('select',n);e.action('set');self.assertEqual(e.vm.rb(0x4b4),i)
            sub=e.vm.rb(0x4c0);e.action('rotate',1);self.assertEqual(e.vm.rb(0x4c0),sub);e.action('back')
        e.action('serialize');self.assertEqual(e.vm.rb(0x1a03f),50)
    def test_radio_sub_no_group_packet(self):
        e=Engine();e.action('radio');e.action('radio');self.assertEqual(e.logs[-1]['output'],[])
        e.action('select','SUB');e.action('set');e.action('rotate',1);e.action('toggle');e.action('radio')
        self.assertEqual(e.logs[-1]['output'],[])
if __name__=='__main__':unittest.main()
