"""Local fixture discovery and immutable R7 reconstruction for the public lab."""
from pathlib import Path
import os,sys,json
NATIVE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(NATIVE))
from patcher import sha,require,original,transform,load_spec,ORIGINAL_SHA256
need=require
FIRMWARE=Path(os.environ.get('GODOX_FIRMWARE',NATIVE.parent/'firmware/V100F_V1.03.bin'))
RAW=FIRMWARE.read_bytes();original(RAW)
IMAGE=transform(RAW)
ROOT=NATIVE/'.lab';PARENT=NATIVE
(ROOT/'analysis').mkdir(parents=True,exist_ok=True)
def compose(raw):return transform(raw),load_spec()['patches'],None,dict(sha256=sha(transform(raw)))
