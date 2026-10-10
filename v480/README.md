# V480F V1.03 · 旋钮直调 v2 / Direct rotary v2

**当前实验发布版：[R10b 主控单灯页、从属直调与组别记忆](r10/README.md)** 在保留本页 v2 机顶直调功能的基础上，加入主控 M/A–D 短按独立页、TTL/M、暂停/恢复与单灯旋钮固定调值。新增从属 TTL/M 旋钮直调及 TTL 补偿实时显示，A–D 字块与原厂从属页 44×44 外观完全一致。从属 A–E 选组确认后加入断电保存，跨机顶/主控模式关机仍保留。原厂列表长按和滑动保留，按 V480 的 320×240 屏幕排版；本版本尚待真机验收。以下内容仍说明既有 v2 发布文件，不将新功能计入旧 BIN。

[R10b BIN 下载 / Download](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v480-r10b-2026-10-10/v480f-v1.03r10b.bin) · [发布与校验 / Release](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v480-r10b-2026-10-10)

[型号说明 / Model guide](../docs/devices/V480F.md) · [统一复现 / Reproduction](../docs/REPRODUCE.md)
[项目首页](../README.md) · [English home](../README.en.md) · [BIN 下载 / Download](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin)

## 实现了什么

**在 Wi-Off 机顶主界面直接转动旋钮，即可调节 TTL 曝光补偿或 M 手动功率，不用先选控件再按 SET。**

- TTL：沿用原厂 FEC，±3 EV、1/3 EV 步进；不改 TTL 测光或相机通信算法。
- M：沿用原厂功率函数和边界，遵守当前 0.1 / 0.3 功率步进；快速旋转仍走原厂计数与消费路径。
- 主界面的直调输入不会再被当作同一次 GUI 导航输入重放，避免调完数值后焦点又跟着移动。
- MENU、MODE、ZOOM、Sender、Receiver、锁屏、下拉面板、弹窗和其他不满足条件的状态，都保留原厂路径。
- 本版**没有加入 RX 直调或 SU-1 扩展**；不要把 V100 R7 的功能表套用到 V480。

项目作者于 2026-10-09 报告 V480F 与 V100F 两台自用设备已刷入项目修改固件，这是作者自己的设备反馈。在机文件 SHA 和完整验收矩阵没有随反馈提供，见[设备状态](../docs/HARDWARE_STATUS.md)。

## 下载与身份

| 项目 | 值 |
|---|---|
| 型号 / 原厂基线 | V480F / V1.03 |
| 下载文件 | `Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin` |
| 文件大小 | 753,705 字节 |
| 原件 SHA-256 | `84ca232f50a62ceb2d9b24017a3b447a7154bf63f6461ef546a30a6b29077ebf` |
| v2 SHA-256 | `58dedf69cb23805a8cb72b9b44a4d6dafb2b7997081a7404e2a53f471ba20fb4` |
| 修改量 | 344 字节：3 个 4 字节入口、316 字节 helper、16 字节 MD5 |

文件名保留最初交付时的 `CANARY_v2`，便于核对身份。它是实验修改版，不是官方发布，也不代表可恢复性认证。源码公开不改变它的字节：本次下载与既有 v2 完全一致。[所有下载与校验](../docs/DOWNLOADS.md)。

## 实现与演进

最初的原型分别处理数值变化和 GUI delta，切页或焦点改变时，同一输入可能在第二条路径里被重放；模式检查与参数写入之间也可能插入普通通信中断。v2 修了这两类问题：

1. 在原 GPIO decoder 入口确认 direct 条件；仍执行原 decoder，保留方向计数和加速信息，只恢复这次事件进入前的 GUI delta。
2. 在参数入口保存 PRIMASK，用受限临界区保护状态判断、原厂 selector 临时选择和原参数写入；退出时恢复原 selector 与 PRIMASK。
3. 复用原 FEC/Power 函数，重放入口被覆盖的指令；条件不满足时回到原入口。
4. helper 放在已确认的原有填充区；向量、scatter 初始化、辅助镜像、原 GUI 回调和文件长度都不变。
5. 按 V480 特有格式重算 payload MD5；不把 V100 的封装处理套用到这里。

本版观察到的最大屏蔽指令数为 194、函数调用附加栈峰值为 32 字节，都是有界模型的结果，不代表硬件微秒级延迟或整机栈余量。无线协议、TTL 算法没有改写，但中断延迟仍需要真实时序测量。

## 本地复现

把匹配的官方原件放到 `firmware/V480F_V1.03.bin`，在仓库根目录执行：

```sh
python3 v480/patcher.py firmware/V480F_V1.03.bin
python3 v480/patcher.py firmware/V480F_V1.03.bin --output-dir v480/out/v2
```

工具只依赖 Python 标准库。默认只在内存里校验；指定输出目录后才生成新 BIN、`SHA256SUMS.txt`、`PATCH_MANIFEST.json`。完整 SHA、机型、版本尾部、MD5、原字节、唯一上下文、补丁范围和最终 SHA 都要符合；已有目录会拒绝写入，避免覆盖。

直接核验下载来的候选文件：

```sh
python3 v480/patcher.py /path/to/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin --verify-candidate
```

文件级还原：

```sh
python3 v480/patcher.py v480/out/v2/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin --restore --output-dir v480/out/restored
```

还原只证明这个文件能精确变回官方原件，不保证升级失败后设备还能恢复。工具不连接、不刷写、也不控制设备。

## 源码构建与验证

```sh
python3 v480/build.py --llvm-bin /path/to/llvm/bin
python3 -m venv .venv
.venv/bin/python -m pip install -r v480/requirements.txt
.venv/bin/python -m unittest discover -s v480/tests -v
.venv/bin/python v480/lab/run.py
```

已用 LLVM 20.1.8 重建 [316 字节汇编 helper](src/rotary_direct.S)，与 v2 记录完全一致。工具在 PATH 里时可省略 `--llvm-bin`，也可以用 `GODOX_LLVM_BIN`。Lab 默认读取上述原件，也可用 `GODOX_V480_FIRMWARE` 指定路径。不要用 Python `-O` 禁用断言。

| 2026-10-09 公开版检查 | 数量 / 结果 |
|---|---|
| V480 参数、作用域、decoder、消费与回落 | 12,489 项通过 |
| V480 条件通信 ISR 插入 | 746 次；过期模式存储为 0 |
| 重建的完整候选执行 | 1,386 项通过 |
| 新公开补丁工具 | 10 项测试通过 |
| 源码重编译 | helper SHA `673267de9ee3397daf1bc0e6f822d8ae23e2c2d54619ddbc0fd57e4fdc0ac7a4` |

[本次 Lab 结果](evidence/PUBLIC_LAB_RESULTS.json) · [构建验证](evidence/BUILD_VERIFICATION.json) · [发布验证](evidence/PUBLICATION_VERIFICATION.json)

`evidence/historical_*` 是旧工程记录：其中 24,978 项功能与 1,491 次中断测试同时覆盖 V480 和早期 V100 两个 helper。新的公开 runner 只跑 V480，不把双型号的旧总数当作 V480 单独的成绩。实验使用真实固件指令和模拟的 RAM/外设，没有模拟整台设备，也没有测量实际闪光。

## English

**Turn the dial directly on the Wi-Off main screen to adjust TTL FEC or manual power, without selecting the widget and pressing SET first.** Factory FEC limits and one-third-stop behavior remain. Manual power retains the selected 0.1 / 0.3 step and the original rotation-count/acceleration path.

The same direct-adjustment event is not replayed as GUI navigation. Menus, MODE, ZOOM, Sender, Receiver, locks, drawers, modals and other excluded states follow their original paths. **This V480 revision does not add RX direct adjustment or V100's SU-1 features.**

On 2026-10-09 the maintainer reported flashing modified project firmware onto both their V480F and V100F. That report did not identify the installed SHA or supply a complete acceptance matrix; see [hardware status](../docs/HARDWARE_STATUS.md).

Use the download link and exact identities above. The historical `CANARY_v2` filename is preserved for traceability. This publication reproduces the existing bytes, not a new firmware variant. The experimental label does not establish guaranteed recovery.

The first prototype risked replaying one input in both parameter and GUI channels, and allowed a mode-changing interrupt between checking the mode and writing the parameter. v2 qualifies direct events at the decoder, retains the stock direction counters, preserves the incoming GUI delta, and guards parameter updates with saved/restored PRIMASK. It reuses the stock FEC/Power routines and falls back outside the permitted scope.

The helper occupies existing padding. Vectors, initialization, auxiliary content, GUI callback and total length are preserved; the V480 payload MD5 is recomputed. The maximum observed masked instruction count is 194 and additional function-call stack use is 32 bytes in the model. Neither is a physical timing or whole-device stack guarantee.

The standard-library patcher verifies the exact input, model, footer/version, MD5, expected bytes, unique contexts, ranges and final SHA. Default operation is memory-only; `--output-dir` writes a new directory and refuses overwrite. `--verify-candidate` checks a downloaded image, and `--restore` reconstructs the exact original file. File reversal is not device unbricking.

LLVM 20.1.8 rebuilds the helper exactly. Public V480-only reruns passed **12,489 functional checks, 746 interrupt injections, 1,386 whole-image checks and 10 patcher tests**. The older dual-model totals in `historical_*` are kept separately. The lab executes original instructions with modeled RAM/peripherals; it does not perform hardware I/O or optical measurements.
