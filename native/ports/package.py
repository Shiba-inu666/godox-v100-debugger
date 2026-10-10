"""Stage only a validated experimental modified BIN and its public evidence."""
from pathlib import Path
import argparse,json,shutil
from build import ROOT,load,sha
from validate import sources

def package(name,destination):
 p=load(name);out=ROOT/'.lab'/name;report=json.loads((out/'VALIDATION.json').read_text());image=out/p['output_filename']
 if report['status']!='PASS_OFFLINE_EXPERIMENTAL' or report['hardware_verified'] or report['source_sha256']!=sources(name) or sha(image.read_bytes())!=report['candidate_sha256']:raise RuntimeError('Validation must match current sources and BIN')
 for suite in report['suites'].values():
  if sha((out/suite['result']).read_bytes())!=suite['result_sha256']:raise RuntimeError('Suite evidence changed')
 evidence=ROOT/'evidence'/name;evidence.mkdir(parents=True,exist_ok=True)
 for f in ['VALIDATION.json','PATCH_MANIFEST.json',*[s['result'] for s in report['suites'].values()]]:shutil.copyfile(out/f,evidence/f)
 target=Path(destination)/name;target.mkdir(parents=True,exist_ok=True)
 for f in [p['output_filename'],'VALIDATION.json','PATCH_MANIFEST.json']:
  shutil.copyfile(out/f,target/f)
 for source,output in [('integrity-results.json','IMAGE_INTEGRITY.json'),('lifecycle-results.json','UI_LIFECYCLE.json')]:shutil.copyfile(out/source,target/output)
 manifest=json.loads((out/'PATCH_MANIFEST.json').read_text());version=p['firmware_version'];model=p['model']
 notes=f'''{model} v{version}r10 · 实验版\n\n仅用于 {model}，基于原厂 V{version}。请核对机身型号后缀，勿混刷。\n\n主控保留原厂长按和滑动，单击灯组进入独立功率页；左侧 TTL/M，右侧暂停/恢复，旋钮只调当前灯的功率或补偿。组名字体与颜色沿用本型号原厂资源，主控 S 行和副灯页支持拖动。包含从属“副灯”命名、退出显示、S 字号以及普通闪光和独立副灯功率路径的移植。C 版保留 A–E，N/S/O 保留 M/A–D。\n\n离线检查：{report['functional_checks']} 项功能检查，{report['image_checks']} 项镜像检查。完整 SHA 和逐套件记录见附件。\n\n尚无本型号实机验收，也没有执行刷机。副灯仍为手动，未实现副灯 TTL/HSS/Multi。离线结果不代表已验证相机时序、光量、热行为、长时间连拍或升级恢复。\n\n文件：`{p['output_filename']}`\n大小：{p['size']} bytes\nSHA-256：`{report['candidate_sha256']}`\n\n[源码、复现与操作说明](https://github.com/Shiba-inu666/godox-firmware-mods/tree/main/native/ports)\n\nEnglish: exact-model R10 experimental port, offline-validated only. No {model} hardware was available. No device write or physical output measurement is claimed. SUB remains manual; no SUB TTL/HSS/Multi extension.\n'''
 (target/'RELEASE_NOTES.md').write_text(notes)
 files=sorted(x for x in target.iterdir() if x.name!='SHA256SUMS');(target/'SHA256SUMS').write_text(''.join(sha(f.read_bytes())+'  '+f.name+'\n' for f in files))
 return target
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('model');a.add_argument('destination');x=a.parse_args();print(package(x.model,x.destination))
