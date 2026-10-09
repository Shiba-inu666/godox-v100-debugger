import copy,hashlib,json,os,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patcher import *

class V480PatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=Path(os.environ.get('GODOX_V480_FIRMWARE',ROOT.parent/'firmware/V480F_V1.03.bin'))
        if not path.exists():raise unittest.SkipTest('Supply exact local V480F V1.03 firmware')
        cls.raw=path.read_bytes();verify_original(cls.raw);cls.spec=load_spec();cls.output=transform(cls.raw)

    def test_exact_candidate_and_inverse(self):
        self.assertEqual(sha(self.output),CANARY_SHA)
        self.assertEqual(transform(self.output,True),self.raw)
        self.assertEqual(verify_candidate(self.output)['original_restored_sha256'],OFFICIAL_SHA)

    def test_unknown_even_with_valid_md5_is_rejected(self):
        bad=bytearray(self.raw);bad[4]^=1;bad[PAYLOAD:PAYLOAD+16]=hashlib.md5(bad[:PAYLOAD]).digest()
        with self.assertRaises(ValueError):transform(bytes(bad))

    def test_truncated_extended_and_candidate_input_rejected(self):
        for data in [self.raw[:-1],self.raw+b'\0',self.output]:
            with self.subTest(size=len(data)),self.assertRaises(ValueError):transform(data)

    def test_corrupted_candidate_restore_rejected(self):
        bad=bytearray(self.output);bad[CAVE]^=1;bad[PAYLOAD:PAYLOAD+16]=hashlib.md5(bad[:PAYLOAD]).digest()
        with self.assertRaises(ValueError):transform(bytes(bad),True)

    def test_expected_bytes(self):
        spec=copy.deepcopy(self.spec);spec['patches'][0]['old_bytes']='00000000'
        with self.assertRaisesRegex(ValueError,'Expected bytes'):transform(self.raw,spec=spec)

    def test_overlap(self):
        spec=copy.deepcopy(self.spec);spec['patches'].append(spec['patches'][0])
        with self.assertRaisesRegex(ValueError,'Overlapping'):transform(self.raw,spec=spec)

    def test_range_and_context(self):
        spec=copy.deepcopy(self.spec);spec['patches'][0]['offset']=hex(PAYLOAD)
        with self.assertRaisesRegex(ValueError,'range'):transform(self.raw,spec=spec)
        spec=copy.deepcopy(self.spec);spec['contexts'][0]['context']='00000000'
        with self.assertRaisesRegex(ValueError,'context'):transform(self.raw,spec=spec)

    def test_output_hash_rejects_modified_patch(self):
        spec=copy.deepcopy(self.spec);x=bytearray.fromhex(spec['patches'][0]['new_bytes']);x[0]^=1;spec['patches'][0]['new_bytes']=x.hex()
        with self.assertRaisesRegex(ValueError,'SHA'):transform(self.raw,spec=spec)

    def test_emit_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'out';report=emit(self.raw,target)
            self.assertEqual((target/NAME).read_bytes(),self.output)
            self.assertEqual(report['changed_bytes'],344)
            self.assertEqual(json.loads((target/'PATCH_MANIFEST.json').read_text()),report)
            with self.assertRaises(FileExistsError):emit(self.raw,target)

    def test_checksum_protected_regions_and_restore_file(self):
        self.assertEqual(self.output[PAYLOAD:PAYLOAD+16],hashlib.md5(self.output[:PAYLOAD]).digest())
        self.assertEqual(self.output[0xb0000:0xb8000],self.raw[0xb0000:0xb8000])
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'restored';emit(self.output,target,True)
            self.assertEqual((target/'V480F_V1.03_RESTORED.bin').read_bytes(),self.raw)

if __name__=='__main__':unittest.main()
