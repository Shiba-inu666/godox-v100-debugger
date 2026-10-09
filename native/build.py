"""Rebuild all three R7 helpers and match the recorded patch bytes exactly."""
from pathlib import Path
import argparse,json,os,shutil,subprocess
from patcher import ROOT,load_spec,require,sha

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--llvm-bin',type=Path,default=os.environ.get('GODOX_LLVM_BIN'))
    ap.add_argument('--linker',default=os.environ.get('GODOX_LD_LLD','ld.lld'))
    args=ap.parse_args();out=ROOT/'.build';out.mkdir(exist_ok=True)
    spec=load_spec();sources=ROOT/'src'
    for filename,digest in spec['source_sha256'].items():
        require(sha((sources/filename).read_bytes())==digest,'Source changed: '+filename)
    def tool(name):
        candidate=str(args.llvm_bin/name) if args.llvm_bin else shutil.which(name)
        require(candidate and Path(candidate).is_file(),'Missing LLVM tool: '+name)
        return candidate
    def run(command):subprocess.run(command,check=True,capture_output=True,text=True)
    for name in ['fixed_main','fire_su1']:
        run([tool('llvm-mc'),'-triple=thumbv7m-none-eabi','-mcpu=cortex-m4','-filetype=obj',str(sources/(name+'.S')),'-o',str(out/(name+'.o'))])
        rel=subprocess.check_output([tool('llvm-readobj'),'--relocations',str(out/(name+'.o'))],text=True)
        require('R_ARM_' not in rel,'Unresolved assembly relocations')
        run([tool('llvm-objcopy'),'-O','binary','--only-section=.text',str(out/(name+'.o')),str(out/(name+'.module'))])
    cc=[tool('clang'),'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfloat-abi=soft','-Oz','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fno-stack-protector','-Wall','-Wextra','-Wno-deprecated-non-prototype','-c']
    for source,name in [('native_sub.c','native_sub'),('native_trampolines.S','trampolines')]:
        run(cc+[str(sources/source),'-o',str(out/(name+'.o'))])
    linker=shutil.which(args.linker) or args.linker
    require(Path(linker).is_file(),'Missing ld.lld; use --linker')
    run([linker,'-T',str(sources/'native.ld'),'--entry=sub_sender',str(out/'native_sub.o'),str(out/'trampolines.o'),'-o',str(out/'native_sub.elf')])
    run([tool('llvm-objcopy'),'-O','binary',str(out/'native_sub.elf'),str(out/'native_sub.module')])
    records={}
    for purpose,name in [('fixed_main:helper','fixed_main'),('su1_fire:helper','fire_su1'),('native_ui:helper','native_sub')]:
        matches=[x for x in spec['patches'] if x['purpose']==purpose];require(len(matches)==1,'Missing helper record')
        blob=(out/(name+'.module')).read_bytes();expected=bytes.fromhex(matches[0]['new_bytes'])
        require(blob==expected,'Compiler output differs from validated R7: '+name)
        records[name]=dict(size=len(blob),sha256=sha(blob),exact_R7_match=True)
    report=dict(status='PASS_EXACT_R7_SOURCE_BUILD',modules=records,
                clang_version=subprocess.check_output([tool('clang'),'--version'],text=True).splitlines()[0],
                source_sha256=spec['source_sha256'])
    (out/'BUILD_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        print('ABORT:',error)
        if getattr(error,'stderr',None):print(error.stderr)
        raise SystemExit(2)
