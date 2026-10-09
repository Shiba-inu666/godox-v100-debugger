"""Exact-image V100F V1.03 patch reproduction; no device or network access."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parent
ORIGINAL_SHA256 = 'fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787'
R7_SHA256 = '8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761'
SIZE = 1002732
NAME = 'V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def original(data):
    require(len(data) == SIZE and sha(data) == ORIGINAL_SHA256,
            'Unknown firmware/model/version: exact original V100F V1.03 required')
    require(data[0x42020:0x4202e] == b'Model: V100 F\0', 'Model marker mismatch')
    require(struct.unpack_from('<4I', data) ==
            (0x200ad668, 0x0800829d, 0x08013d95, 0x0800fb9f), 'Vector mismatch')

def load_spec(revision='r7'):
    pins = json.loads((ROOT / 'patches/INDEX.json').read_text())
    require(revision in pins, 'Unknown patch revision')
    data = (ROOT / 'patches' / (revision + '.json')).read_bytes()
    require(sha(data) == pins[revision]['spec_sha256'], 'Patch specification changed')
    spec = json.loads(data)
    require(spec['original_sha256'] == ORIGINAL_SHA256 and spec['size'] == SIZE,
            'Specification identity mismatch')
    require(spec['modified_sha256'] == pins[revision]['output_sha256'], 'Output identity mismatch')
    if revision == 'r7':
        require(spec['modified_sha256'] == R7_SHA256, 'Unknown R7 output')
    return spec

def transform(data, spec=None, restore=False):
    spec = load_spec() if spec is None else spec
    if restore:
        require(len(data) == SIZE and sha(data) == spec['modified_sha256'],
                'Restore requires the exact known candidate')
    else:
        original(data)
        for c in spec.get('contexts', []):
            context = bytes.fromhex(c['context']); offset = int(c['context_offset'], 16)
            require(data[offset:offset + len(context)] == context and data.count(context) == 1,
                    'Original instruction context missing or ambiguous')
    output = bytearray(data); occupied = set()
    for patch in spec['patches']:
        offset = int(patch['offset'], 16)
        before = bytes.fromhex(patch['new_bytes' if restore else 'old_bytes'])
        after = bytes.fromhex(patch['old_bytes' if restore else 'new_bytes'])
        require(len(before) == len(after) and before and 0 <= offset < SIZE and offset + len(before) <= SIZE,
                'Invalid patch range')
        span = set(range(offset, offset + len(before)))
        require(not occupied.intersection(span), 'Overlapping patch ranges')
        require(data[offset:offset + len(before)] == before, 'Expected bytes mismatch')
        occupied.update(span); output[offset:offset + len(after)] = after
    result = bytes(output)
    expected = ORIGINAL_SHA256 if restore else spec['modified_sha256']
    require(len(result) == SIZE and sha(result) == expected, 'Unexpected complete output hash')
    require(result[:0x1b4] == data[:0x1b4] and result[0xf0000:] == data[0xf0000:],
            'Vector or auxiliary payload changed')
    if restore:
        original(result)
    return result

def emit(data, directory, restore=False):
    spec = load_spec(); result = transform(data, spec, restore)
    inverse = transform(result, spec, not restore)
    require(inverse == data, 'File-level inverse mismatch')
    filename = 'V100F_V1.03_RESTORED.bin' if restore else NAME
    report = dict(model='V100F',firmware_version='1.03',patch_revision='R7',
                  patch_tool_version='1.0.0-public',direction='restore' if restore else 'apply',
                  input_sha256=sha(data),output_sha256=sha(result),size=len(result),
                  changed_bytes=sum(a != b for a,b in zip(data,result)),patches=spec['patches'],
                  checksum_changes=[],checksum_status='UNKNOWN_NOT_BYPASSED',
                  digital_signature='UNKNOWN_NOT_BYPASSED',hardware_verified=False,
                  device_written=False,recovery_guaranteed=False,SU1_TTL_implemented=False)
    payloads = {filename:result, 'SHA256SUMS.txt':(sha(result)+'  '+filename+'\n').encode(),
                'PATCH_MANIFEST.json':(json.dumps(report,indent=2)+'\n').encode()}
    directory = Path(directory)
    directory.parent.mkdir(parents=True,exist_ok=True)
    directory.mkdir()  # Existing directories are rejected, never reused or overwritten.
    for name,content in payloads.items():
        with (directory/name).open('xb') as stream:
            stream.write(content)
    require((directory/filename).read_bytes() == result, 'Output readback mismatch')
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output-dir',type=Path,help='New directory; omitted means verify in memory only')
    parser.add_argument('--restore',action='store_true',help='Restore known R7 bytes to the exact original file')
    args=parser.parse_args()
    try:
        data=args.input.read_bytes()
        if args.output_dir:
            report=emit(data,args.output_dir,args.restore)
        else:
            result=transform(data,restore=args.restore)
            report=dict(status='VERIFIED_IN_MEMORY_NO_FILE_WRITTEN',sha256=sha(result),size=len(result))
        print(json.dumps(report if not args.output_dir else {k:report[k] for k in ['output_sha256','size','changed_bytes']},indent=2))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('ABORT:',error)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
