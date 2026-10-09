"""Reproduce exact V480F V1.03 v2 bytes, or reverse them. No hardware I/O."""
from pathlib import Path
import argparse
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parent
OFFICIAL_SHA = '84ca232f50a62ceb2d9b24017a3b447a7154bf63f6461ef546a30a6b29077ebf'
CANARY_SHA = '58dedf69cb23805a8cb72b9b44a4d6dafb2b7997081a7404e2a53f471ba20fb4'
SPEC_SHA = 'efe37ec930f43985ec1a4eef42bbd29f7b223ac43837c89f7d6df3576163f9ac'
SIZE, PAYLOAD, CAVE, HELPER_SIZE = 0xb8029, 0xb8000, 0x85000, 316
NAME = 'Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin'
HOOKS = [(0x34f0, 'f0b42848', '81f0b2bd'), (0x8850, 'fd480022', '7cf0d6bb'), (0x39f0, 'e3480022', '81f01cbb')]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_spec():
    data = (ROOT / 'patches/v2.json').read_bytes()
    require(sha(data) == SPEC_SHA, 'Patch specification changed')
    spec = json.loads(data)
    require(spec['original_sha256'] == OFFICIAL_SHA and spec['modified_sha256'] == CANARY_SHA,
            'Wrong patch identity')
    return spec


def verify_layout(data):
    require(len(data) == SIZE, 'Exact length mismatch')
    require(data[0x42a94:0x42a94 + 13] == b'Model: V480 F', 'Model mismatch')
    require(data[PAYLOAD + 16:] == b'V480F_V1.03.bin' + struct.pack('<H', 15) + bytes.fromhex('aa55669977882233'),
            'Version/footer mismatch')
    require(data[PAYLOAD:PAYLOAD + 16] == hashlib.md5(data[:PAYLOAD]).digest(), 'Payload MD5 mismatch')
    require(struct.unpack_from('<2I', data) == (0x2005fa98, 0x0800829d), 'Vector mismatch')


def verify_original(data):
    require(len(data) == SIZE and sha(data) == OFFICIAL_SHA, 'Exact original V480F V1.03 required')
    verify_layout(data)


def transform(data, restore=False, spec=None):
    spec = load_spec() if spec is None else spec
    if restore:
        require(sha(data) == CANARY_SHA, 'Exact known v2 candidate required for restore')
        verify_layout(data)
    else:
        verify_original(data)
        for item in spec['contexts']:
            offset = int(item['context_offset'], 16)
            context = bytes.fromhex(item['context'])
            require(data[offset:offset + len(context)] == context and data.count(context) == 1,
                    'Expected instruction context missing or ambiguous')
    result = bytearray(data)
    occupied = set()
    for patch in spec['patches']:
        offset = int(patch['offset'], 16)
        old = bytes.fromhex(patch['new_bytes' if restore else 'old_bytes'])
        new = bytes.fromhex(patch['old_bytes' if restore else 'new_bytes'])
        require(old and len(old) == len(new) and 0 <= offset < PAYLOAD and offset + len(old) <= PAYLOAD,
                'Invalid patch range')
        span = set(range(offset, offset + len(old)))
        require(not occupied.intersection(span), 'Overlapping patches')
        require(data[offset:offset + len(old)] == old, 'Expected bytes mismatch')
        occupied.update(span)
        result[offset:offset + len(old)] = new
    result[PAYLOAD:PAYLOAD + 16] = hashlib.md5(result[:PAYLOAD]).digest()
    result = bytes(result)
    require(sha(result) == (OFFICIAL_SHA if restore else CANARY_SHA), 'Complete output SHA mismatch')
    verify_layout(result)
    for lo, hi in [(0, 0x280), (0x84980, 0x84e34), (0xb0000, 0xb8000), (0xb8010, SIZE), (0x2279c, 0x22808)]:
        require(data[lo:hi] == result[lo:hi], 'Protected region changed')
    return result


def verify_candidate(data):
    restored = transform(data, restore=True)
    return dict(model='V480F', firmware_version='1.03', sha256=sha(data), bytes=len(data),
                payload_md5=data[PAYLOAD:PAYLOAD + 16].hex(), original_restored_sha256=sha(restored))


def emit(data, directory, restore=False):
    result = transform(data, restore)
    require(transform(result, not restore) == data, 'Inverse mismatch')
    name = 'V480F_V1.03_RESTORED.bin' if restore else NAME
    spec = load_spec()
    report = dict(model='V480F', firmware_version='1.03', revision='v2', patch_tool_version='1.0.0-public',
                  direction='restore' if restore else 'apply', original_sha256=OFFICIAL_SHA,
                  input_sha256=sha(data), output_sha256=sha(result), bytes=len(result),
                  changed_bytes=sum(a != b for a, b in zip(data, result)), patches=spec['patches'],
                  checksum_changes=[dict(offset=hex(PAYLOAD), algorithm='MD5', coverage=[0, PAYLOAD],
                    old_bytes=data[PAYLOAD:PAYLOAD + 16].hex(), new_bytes=result[PAYLOAD:PAYLOAD + 16].hex())],
                  device_written_by_tool=False, signature_bypass=False, recovery_guaranteed=False)
    directory = Path(directory)
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir()  # Never replace an existing output directory.
    contents = {name: result, 'PATCH_MANIFEST.json': (json.dumps(report, indent=2) + '\n').encode(),
                'SHA256SUMS.txt': (sha(result) + '  ' + name + '\n').encode()}
    for filename, content in contents.items():
        with (directory / filename).open('xb') as stream:
            stream.write(content)
    require((directory / name).read_bytes() == result, 'Output readback mismatch')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, help='New directory only; omitted means memory-only verification')
    parser.add_argument('--restore', action='store_true')
    parser.add_argument('--verify-candidate', action='store_true')
    args = parser.parse_args()
    try:
        require(not args.verify_candidate or not (args.output_dir or args.restore), 'Incompatible options')
        data = args.input.read_bytes()
        if args.verify_candidate:
            report = verify_candidate(data)
        elif args.output_dir:
            report = emit(data, args.output_dir, args.restore)
            report = {key: report[key] for key in ['output_sha256', 'bytes', 'changed_bytes']}
        else:
            result = transform(data, args.restore)
            report = dict(status='VERIFIED_IN_MEMORY_NO_FILE_WRITTEN', output_sha256=sha(result))
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('ABORT:', error)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
