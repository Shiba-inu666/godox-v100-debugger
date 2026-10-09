import copy,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patcher import *

class ExactPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=Path(os.environ.get('GODOX_FIRMWARE',ROOT.parent/'firmware/V100F_V1.03.bin'))
        if not path.exists():raise unittest.SkipTest('Supply the exact local firmware; no vendor image is distributed')
        cls.raw=path.read_bytes();original(cls.raw);cls.spec=load_spec();cls.candidate=transform(cls.raw)

    def test_exact_candidate_and_inverse(self):
        self.assertEqual(sha(self.candidate),R7_SHA256)
        self.assertEqual(transform(self.candidate,restore=True),self.raw)

    def test_unknown_truncated_extended_and_already_patched_rejected(self):
        for data in [self.raw[:-1],self.raw+b'\0',bytes([self.raw[0]^1])+self.raw[1:],self.candidate]:
            with self.subTest(size=len(data)),self.assertRaises(ValueError):transform(data)

    def test_damaged_candidate_restore_rejected(self):
        damaged=bytearray(self.candidate);damaged[0x42020]^=1
        with self.assertRaises(ValueError):transform(bytes(damaged),restore=True)

    def test_old_bytes_check(self):
        spec=copy.deepcopy(self.spec);spec['patches'][0]['old_bytes']='00000000'
        with self.assertRaisesRegex(ValueError,'Expected bytes'):transform(self.raw,spec)

    def test_overlapping_ranges_rejected(self):
        spec=copy.deepcopy(self.spec);spec['patches'].append(spec['patches'][0])
        with self.assertRaisesRegex(ValueError,'Overlapping'):transform(self.raw,spec)

    def test_missing_context_rejected(self):
        spec=copy.deepcopy(self.spec);spec['contexts'][0]['context']='00000000'
        with self.assertRaisesRegex(ValueError,'context'):transform(self.raw,spec)

    def test_outside_range_rejected(self):
        spec=copy.deepcopy(self.spec);spec['patches'][0]['offset']=hex(SIZE)
        with self.assertRaisesRegex(ValueError,'range'):transform(self.raw,spec)

    def test_new_bytes_tamper_rejected(self):
        spec=copy.deepcopy(self.spec);x=bytearray.fromhex(spec['patches'][0]['new_bytes']);x[0]^=1;spec['patches'][0]['new_bytes']=x.hex()
        with self.assertRaisesRegex(ValueError,'hash'):transform(self.raw,spec)

    def test_output_manifest_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'candidate';report=emit(self.raw,dest)
            self.assertEqual((dest/NAME).read_bytes(),self.candidate)
            self.assertEqual(json.loads((dest/'PATCH_MANIFEST.json').read_text()),report)
            with self.assertRaises(FileExistsError):emit(self.raw,dest)
            self.assertEqual((dest/NAME).read_bytes(),self.candidate)

    def test_restore_file_and_sum(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'original';emit(self.candidate,dest,True)
            self.assertEqual((dest/'V100F_V1.03_RESTORED.bin').read_bytes(),self.raw)
            self.assertIn(ORIGINAL_SHA256,(dest/'SHA256SUMS.txt').read_text())

if __name__=='__main__':unittest.main()
