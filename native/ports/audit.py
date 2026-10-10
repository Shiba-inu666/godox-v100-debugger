"""Check pinned V100 C/N/S/O inputs against the F-only R10 patch contracts.

Read-only preflight: this neither relocates patches nor emits firmware. An
instruction-context match is not evidence that a model has been ported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parent
NATIVE = ROOT.parent
sys.path.insert(0, str(NATIVE))
from patcher import ORIGINAL_SHA256, original


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit(directory: Path) -> dict:
    catalog = json.loads((ROOT / 'upstream.json').read_text())
    hooks = []
    for family in ('rotary', 'fire', 'ui'):
        meta = json.loads((NATIVE / 'metadata' / f'{family}.json').read_text())
        if meta['original_sha256'] != ORIGINAL_SHA256:
            raise ValueError('Unexpected F baseline in hook metadata')
        hooks.extend((family, h) for h in meta['hooks'])
    results = []
    for model in catalog['models']:
        raw = (directory / model['filename']).read_bytes()
        if len(raw) != model['size'] or digest(raw) != model['sha256']:
            raise ValueError(f"Wrong original image: {model['model']}")
        marker = ('Model: V100 ' + model['model'][-1]).encode() + b'\0'
        if raw.count(marker) != 1:
            raise ValueError(f"Wrong model marker: {model['model']}")
        checks = []
        for family, hook in hooks:
            offset = int(hook['context_offset'], 16)
            context = bytes.fromhex(hook['context'])
            checks.append({
                'family': family,
                'hook': hook['name'],
                'f_address': hook['address'],
                'same_context_at_f_offset': raw[offset:offset + len(context)] == context,
                'exact_context_occurrences': raw.count(context),
            })
        try:
            original(raw)
        except ValueError as exc:
            rejected = True
            rejection = str(exc)
        else:
            raise ValueError('F-only patcher unexpectedly accepted another model')
        results.append({
            'model': model['model'],
            'firmware_version': model['firmware_version'],
            'original_sha256': digest(raw),
            'size': len(raw),
            'model_marker_offset': hex(raw.index(marker)),
            'initial_sp': hex(struct.unpack_from('<I', raw)[0]),
            'reset_vector': hex(struct.unpack_from('<I', raw, 4)[0]),
            'f_patcher_rejects': rejected,
            'rejection': rejection,
            'contexts_at_f_offsets': sum(c['same_context_at_f_offset'] for c in checks),
            'required_hook_contexts': len(checks),
            'hooks': checks,
            'r10_status': 'not_evaluated_by_input_preflight',
            'functional_validation': 'not_run_by_input_preflight',
            'hardware_verified': False,
            'candidate_emitted': False,
        })
    return {
        'status': 'INPUT_IDENTITIES_VERIFIED',
        'checked_on': catalog['checked_on'],
        'scope': 'Exact identities, model markers and F patch contract incompatibility only',
        'models': results,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware_dir', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.firmware_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    for item in result['models']:
        print(f"{item['model']} {item['firmware_version']}: original verified; "
              f"F contexts {item['contexts_at_f_offsets']}/{item['required_hook_contexts']}; "
              'F patcher rejects; port validation is recorded separately')
