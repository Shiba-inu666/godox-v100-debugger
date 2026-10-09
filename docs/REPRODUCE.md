# 复现与验证 / Reproduction and validation

[文档索引 / Docs](README.md) · [V100 工具 / Tool](../native/README.md) · [V480 工具 / Tool](../v480/README.md)

## 1. 准备 / Prepare

使用 Python 3.11+。从[原件准备页](../firmware/README.md)核对两款官方输入的大小与 SHA-256。官方输入由使用者自行准备；直接获取修改版见[下载页](DOWNLOADS.md)。

Use Python 3.11+. Check the size and SHA-256 of each official input against the [input guide](../firmware/README.md). Supply your own originals locally. Ready-made modified files are on the [download page](DOWNLOADS.md).

```sh
git clone https://github.com/Shiba-inu666/godox-firmware-mods.git
cd godox-firmware-mods
```

## 2. 在内存验证或生成新文件 / Verify in memory or generate new files

从仓库根目录执行。第一组只校验；第二组写入全新目录。输入不会覆盖，已有输出目录会被拒绝。

Run from the repository root. The first pair validates in memory; the second writes new directories. Inputs are not overwritten and existing output directories are rejected.

```sh
python3 native/patcher.py firmware/V100F_V1.03.bin
python3 v480/patcher.py firmware/V480F_V1.03.bin

python3 native/patcher.py firmware/V100F_V1.03.bin --output-dir native/out/r7
python3 v480/patcher.py firmware/V480F_V1.03.bin --output-dir v480/out/v2
```

各工具生成对应 BIN、`SHA256SUMS.txt`、`PATCH_MANIFEST.json`，并核对完整结果 SHA。未知版本或不匹配的原字节会停止；不会连接设备。两个 `--restore` 的精确文件逆变换命令见各型号工具说明，**文件还原不等于失败设备恢复**。

Each tool emits its BIN, `SHA256SUMS.txt` and `PATCH_MANIFEST.json`, and checks the complete output hash. Unknown versions or mismatched original bytes stop processing. Neither tool connects to hardware. Each model guide documents `--restore`; **reversing a file is not recovering a failed device**.

## 3. 从源码核对机器码 / Rebuild native code

应用已记录补丁仅需标准库；验证源码与机器码一致还需 LLVM / Clang 20.1.8，以及 V100 链接器 `ld.lld`。工具位于 PATH 时：

Applying recorded changes needs only Python's standard library. Auditing source-to-byte correspondence requires LLVM / Clang 20.1.8 and, for V100, `ld.lld`. With tools on PATH:

```sh
python3 native/build.py
python3 v480/build.py
```

也可传 `--llvm-bin /path/to/llvm/bin`；V100 支持 `--linker /path/to/ld.lld`。构建必须与各型号已记录的 helper 完全相同，不能静默生成不同版本。详细参数见对应 README。

Use `--llvm-bin /path/to/llvm/bin` if needed; V100 also accepts `--linker /path/to/ld.lld`. Rebuilt helpers must exactly match the recorded versions. See each source guide for details.

## 4. 离线验证 / Offline checks

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r native/requirements.txt -r v480/requirements.txt
.venv/bin/python -m unittest discover -s native/tests -v
.venv/bin/python -m unittest discover -s v480/tests -v
.venv/bin/python native/lab/run.py
.venv/bin/python v480/lab/run.py
.venv/bin/python -m unittest discover -s tests -v
```

| 范围 / Scope | 已记录公开结果 / Recorded public result |
|---|---|
| V100 patcher | 10 tests |
| V100 portable execution | 9,399 functional checks; 90 separate TTL observations |
| V480 patcher | 10 tests |
| V480 execution | 12,489 functional; 746 IRQ injections; 1,386 whole-image checks |
| Desktop workbench | 26 tests |

结果分别写入 `native/.lab/` 与 `v480/.lab/`；不要使用 `python -O` 关闭断言。90 项 TTL 观测是研究记录，不表示副灯 TTL 已实现。各集合有不同作用域和重叠，不能相加冒充实机次数。

Results go to `native/.lab/` and `v480/.lab/`. Do not disable assertions with `python -O`. The 90 TTL observations are research evidence, not implemented SU-1 TTL. Counts have distinct and overlapping scopes; they are not a hardware-test total.

仅修改文档或目录索引时，运行下面的标准库检查即可检查本地链接、JSON、型号目录及既有源码证据摘要；它不运行设备仿真、不下载固件，也不连接硬件：

For documentation/catalog work, this standard-library check validates local links, JSON, model entries and saved source/evidence hashes. It does not emulate devices, download firmware or access hardware:

```sh
python3 scripts/check_repository.py
```
