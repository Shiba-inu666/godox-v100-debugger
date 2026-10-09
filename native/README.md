# R7 原生补丁 / Native patch kit

[中文项目说明](../README.md) · [English overview](../README.en.md)

## 中文

本目录独立复现 V100F V1.03 R7。`src/` 是三段原生辅助代码，`patches/r7.json` 记录完整修改区域、原字节、新字节和源文件摘要。`metadata/` 保留原工程的符号/钩子记录，里面的旧 builder 摘要仅作历史标识；公开构建入口是 `build.py`。

### 1. 验证或生成

原件必须是 1,002,732 字节，SHA-256 为：

`fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787`

从仓库根目录执行：

```sh
python3 native/patcher.py firmware/V100F_V1.03.bin
python3 native/patcher.py firmware/V100F_V1.03.bin --output-dir native/out/r7
```

不带输出目录时只在内存验证；带输出目录才写新文件。已有目录、未知固件、上下文不唯一、原字节不符、补丁重叠或结果摘要异常都会停止。对不同版本没有自动扫描后盲目适配功能。

结果 SHA-256 必须为：

`8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761`

工具同时生成 `SHA256SUMS.txt` 与 `PATCH_MANIFEST.json`。没有修改未知 checksum 或绕过签名；清单把这两项记录为未解决。此处精确复现的是已知实验候选，不是证明其设备端完整性策略已被完全理解。

### 2. 文件级逆变换

```sh
python3 native/patcher.py native/out/r7/V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin --restore --output-dir native/out/restored
```

只有精确 R7 文件可逆变换，结果与原件 SHA 完全一致。**恢复文件不等于恢复设备**：若设备无法进入升级模式，本工具不会使其重新进入，也没有 USB、SWD 或硬件写入功能。

### 3. 重编译原生辅助代码

应用记录好的补丁不需要编译器。审核源码与机器码对应关系时，使用 LLVM / Clang 20.1.8、`llvm-mc`、`llvm-readobj`、`llvm-objcopy` 和 `ld.lld`：

```sh
python3 native/build.py
```

如果工具不在 PATH，可传 `--llvm-bin /path/to/llvm/bin --linker /path/to/ld.lld`，或设置 `GODOX_LLVM_BIN` / `GODOX_LD_LLD`。构建输出在 `native/.build/`，每段必须与 R7 记录字节完全一致；编译器差异或源文件变更会失败，不会悄悄生成另一个“R7”。

| 模块 | 长度 | 作用 |
|---|---:|---|
| `fixed_main.S` | 508 | 目标页面旋钮直调和回落 |
| `fire_su1.S` | 476 | TEST、普通曝光/RX、副灯单独路径 |
| `native_sub.c` + `native_trampolines.S` | 3,003 | 原生副灯 UI、生命周期、层级、字形 |

### 4. 运行公开离线验证

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r native/requirements.txt
.venv/bin/python -m unittest discover -s native/tests -v
.venv/bin/python native/lab/run.py
.venv/bin/python -m unittest discover -s tests -v
```

默认原件路径为 `firmware/V100F_V1.03.bin`；原生 lab 可通过 `GODOX_FIRMWARE` 指向别处。不要用 Python `-O` 跳过断言。原生结果生成到 `native/.lab/`；源码和补丁在运行前后均记录摘要。

公开 runner 复现 9,399 项功能检查与 90 项 TTL 研究观测。它使用原厂指令、模拟 RAM、虚拟时钟和外设替身，不连接设备。历史完整工程的 39,851 项记录另存于 `evidence/`，不是此 runner 一次运行的数量。[验证边界](../docs/native/VALIDATION.md)。

`r4.json`、`r5.json` 用于测试旧路径的对照，公开 CLI 固定生成 R7。不要把这些对照记录当作推荐降级版本。

## English

This directory reproduces R7 for one exact V100F V1.03 image. The source, complete changed ranges, expected bytes and source digests are included. Historical symbol/hook metadata is retained for inspection; `build.py` is the public build entry point.

Use the commands above from the repository root. The standard-library patcher verifies in memory unless `--output-dir` is supplied. It rejects unknown images, ambiguous contexts, mismatched original bytes, overlapping ranges, unexpected output hashes and existing output directories. It writes the candidate, `SHA256SUMS.txt` and `PATCH_MANIFEST.json` to a new directory only.

The exact original and result hashes appear above. Unknown device-side checksum/signature behavior is not “repaired” or bypassed. Reproducing an established experimental file does not prove that all device integrity mechanisms are understood.

`--restore` accepts only the exact known R7 and reconstructs the original file. **File restoration is not device recovery.** This package does not contain device-writing, USB or SWD code.

Applying recorded changes needs no compiler. To audit source-to-byte correspondence, install LLVM/Clang 20.1.8 and the listed tools, then run `build.py`. Use `--llvm-bin` and `--linker`, or `GODOX_LLVM_BIN` / `GODOX_LD_LLD`, if needed. All three helpers must match the recorded bytes exactly. Other compiler versions have not been qualified; changed output is rejected.

The public lab defaults to the repository's local firmware file and optionally accepts `GODOX_FIRMWARE`. Do not disable assertions with Python `-O`. It executes original instructions with simulated memory, timing and peripheral stand-ins, without hardware I/O. Results and source digests go to `native/.lab/`.

The portable runner covers **9,399 functional checks and 90 separate TTL research observations**. The **39,851-check historical engineering run** is an overlapping, broader archived set. R4/R5 patch records reconstruct comparison inputs in memory; the public patcher CLI generates R7 only. Neither baseline is a downgrade recommendation. See [validation limits](../docs/native/VALIDATION.md).
