"""Rebuild the V480 v2 helper and compare it to the published patch bytes."""
from pathlib import Path
import argparse,json,os,shutil,subprocess
from patcher import ROOT,load_spec,sha,require

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--llvm-bin',type=Path,default=os.environ.get('GODOX_LLVM_BIN'))
    args=ap.parse_args();out=ROOT/'.build';out.mkdir(exist_ok=True)
    source=ROOT/'src/rotary_direct.S';spec=load_spec()
    require(sha(source.read_bytes())==spec['source_sha256']['rotary_direct.S'],'Source changed')
    def tool(name):
        path=str(args.llvm_bin/name) if args.llvm_bin else shutil.which(name)
        require(path and Path(path).is_file(),'Missing LLVM tool: '+name)
        return path
    subprocess.run([tool('llvm-mc'),'-triple=thumbv7m-none-eabi','-mcpu=cortex-m4','-filetype=obj',str(source),'-o',str(out/'helper.o')],check=True)
    rel=subprocess.check_output([tool('llvm-readobj'),'--relocations',str(out/'helper.o')],text=True)
    require('R_ARM_' not in rel,'Unresolved relocations')
    subprocess.run([tool('llvm-objcopy'),'-O','binary','--only-section=.text',str(out/'helper.o'),str(out/'helper.module')],check=True)
    blob=(out/'helper.module').read_bytes()
    require(blob==bytes.fromhex(spec['patches'][-1]['new_bytes']),'Rebuild differs from v2')
    report=dict(status='PASS_EXACT_V480_V2_SOURCE_BUILD',helper_size=len(blob),helper_sha256=sha(blob),
                source_sha256=sha(source.read_bytes()),llvm_version=subprocess.check_output([tool('llvm-mc'),'--version'],text=True).splitlines()[0])
    (out/'BUILD_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
