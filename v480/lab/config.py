"""V480-only public fixtures and a frozen, exact complete candidate."""
from pathlib import Path
import os,sys,json
PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE))
from patcher import *
FIRMWARE=Path(os.environ.get('GODOX_V480_FIRMWARE',PACKAGE.parent/'firmware/V480F_V1.03.bin'))
RAW=FIRMWARE.read_bytes();verify_original(RAW)
IMAGE=transform(RAW)
SPEC=load_spec();META=json.loads((PACKAGE/'metadata/build.json').read_text())
HELPER=bytes.fromhex(SPEC['patches'][-1]['new_bytes'])
require(sha(HELPER)==META['helper_sha256'],'Helper metadata mismatch')
ROOT=PACKAGE/'.lab';(ROOT/'analysis').mkdir(parents=True,exist_ok=True)
