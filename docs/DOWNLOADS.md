# 固件下载与功能对照 / Firmware downloads

[项目首页 / Home](../README.md) · [R7 / V480 基线 Release](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-v480-2026-10-09)

## V100 系列 / V100 downloads

F 版与 C/N/S/O 独立移植版均提供 R10 单灯控制、原厂彩色组名和副灯拖动。全部为实验版，当前修订均尚待真机验收。详见 [F 版说明](../native/r10/README.md)与 [C/N/S/O 操作及验证](../native/ports/README.md)。

| 设备 | 下载版本 | 文件 | 状态 |
|---|---|---|---|
| **V100F V1.03** | R10 experimental | [下载 V100F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-r10-2026-10-10/v1.03r10.bin) | 保留 R9 单灯控制与原厂手势，新增原厂彩色组名和主控 S 行拖动调功率 |
| **V100C V1.11** | R10 experimental | [下载 V100C BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100c-r10-2026-10-10/v1.11r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100N V1.05** | R10 experimental | [下载 V100N BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100n-r10-2026-10-10/v1.05r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100S V1.06** | R10 experimental | [下载 V100S BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100s-r10-2026-10-10/v1.06r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100O V1.04** | R10 experimental | [下载 V100O BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100o-r10-2026-10-10/v1.04r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |

Separate exact-model R10 ports; all four are offline-tested prereleases without hardware acceptance. See each release for its SHA-256 and report.

## V100F R10 · 2026-10-10

当前 V100F 实验版：[下载 v1.03r10.bin](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-r10-2026-10-10/v1.03r10.bin) · [发布页与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-r10-2026-10-10) · [操作与原生预览](../native/r10/README.md)。单灯页使用原厂 A/B/C/D 彩色字母块，主控列表 S 行支持左右拖动功率，保留 R9 单灯页、长按、滑动和旋钮操作。副灯仍为手动。简化文件名不改变 BIN 内容；只适用于 V100F V1.03。

Current V100F experimental revision: native colored group badges and relative Sender S-row power dragging, retaining R9 controls. The shorter filename does not change firmware bytes. **V100F V1.03 only; 13,966 native functional checks + 37 image checks passed; hardware acceptance is pending.**

Size: **1,002,732 bytes**. SHA-256:

```text
250523b8634d75e2ccb3124cd80695def5e8b056c79e71cee4fd4c0e4924353d  v1.03r10.bin
```

## V100F R9 · 2026-10-10

历史 V100F R9：[下载 R9 BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-r9-2026-10-10/V100F_V1.03_GROUP_CONTROL_R9_EXPERIMENTAL.bin) · [发布页与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-r9-2026-10-10) · [操作、源码与原生预览](../native/r9/README.md)。R9 新增 M/A–D 独立控制页，保留原厂长按切换 TTL/M/OFF 与滑动调节，单灯页旋钮只调当前灯功率或 TTL 补偿；修复副灯命名、退出时的显示生命周期与 S 字号。副灯仍为手动功率。

Previous V100F R9 revision: dedicated M/A–D editors, native long press/swipe, power-only editor encoder and SUB UI repairs. SUB remains manual. **12,159 native functional checks + 37 image checks; R9 hardware acceptance remains pending.**

Size: **1,002,732 bytes**. SHA-256:

```text
6373f518f30e0582c9fde4c18efc6da81978207bbd8def1781219c2ddd3e24e5  V100F_V1.03_GROUP_CONTROL_R9_EXPERIMENTAL.bin
```

## V480 系列 / V480 downloads

| 设备 / Device | 下载版本 / Revision | BIN 下载 / Download | 主要功能 / Changes |
|---|---|---|---|
| **V480F V1.03** | **R10b experimental** | [v480f-v1.03r10b.bin](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v480-r10b-2026-10-10/v480f-v1.03r10b.bin) | 主控单灯页、TTL/M、暂停/恢复；机顶/从属旋钮直调；从属 A–E 组别断电记忆 / Sender group editors, Wi-Off/RX direct rotary, persistent RX group |

[发布与校验文件 / Release](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v480-r10b-2026-10-10) · [操作、源码与原生预览 / Controls and source](../v480/r10/README.md)。保留原厂主控长按 TTL/OFF/M 和滑动调节，单击 M/A–D 进入独立页；A–D 字块与原厂从属页一致。组选项确认后由原厂保存循环持久化，跨机顶/主控关机后仍保留；恢复出厂设置回到 A。不包含 SU-1 扩展。

**23,652 项功能检查、1,562 次中断检查与 53 项镜像检查通过，尚待真机验收。** 新增 1,522 项组别保存 / 冷启动恢复检查；写入或擦除中突然断电的行为仍需设备验证。

Preserves native long press/swipe, adds per-group editors with native badges, TTL/M and pause/resume. The editor dial controls only power/FEC. Confirmed Receiver A–E selection persists through the original save service across role changes and restarts. Factory reset restores A. No SU-1 extension; hardware acceptance, including physical power-loss behavior, remains pending.

Size: **753,705 bytes**. SHA-256:

```text
a97628e92d62b2918ff3091da264c155c4525abf7fc850734b1cbe8445d55bc2  v480f-v1.03r10b.bin
```

## 2026-10-09 基线发布 / Baseline release

这次基线发布仅提供 **V100F 与 V480F，均基于 V1.03**。作者报告两台设备均已刷入修改固件；[证据范围见设备状态](HARDWARE_STATUS.md)。

This historical baseline contains **V100F and V480F only, both based on V1.03**. The maintainer reports both devices flashed; see [evidence scope](HARDWARE_STATUS.md).

- **V100F 历史基线**：[V100F V1.03 R7](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin)，1,002,732 bytes。机顶 Wi-Off 与从属 Receiver 主灯直调、SU-1 主控/从属原生 UI 与普通闪光路径、主控主灯 OFF 时副灯独立、界面修复 / Wi-Off/RX direct main adjustment, Sender/RX manual SU-1 controls/firing, SUB-only with main OFF, UI fixes
- **V480F 历史基线**：[V480F V1.03 rotary-direct v2](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin)，753,705 bytes。仅机顶 Wi-Off 主界面 TTL 曝光补偿 / M 功率直调，保留 0.1/0.3 步进、原厂加速，其余页面沿用原厂 / Wi-Off direct FEC/manual power, original steps, acceleration and excluded pages

- [SHA256SUMS.txt](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/SHA256SUMS.txt)
- [RELEASE_MANIFEST.json](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/RELEASE_MANIFEST.json)
- [V100 补丁清单 / V100 patch manifest](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/V100F_R7_PATCH_MANIFEST.json)
- [V480 补丁清单 / V480 patch manifest](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/V480F_V2_PATCH_MANIFEST.json)

## SHA-256

```text
8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761  V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin
58dedf69cb23805a8cb72b9b44a4d6dafb2b7997081a7404e2a53f471ba20fb4  Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin
```

两款文件不能混用，其他 C/N/S/O 后缀未在此发布中适配。下载文件保留既有实验版本名称与原字节，仓库更名不改变固件行为。**V100 副灯 TTL 未实现；V480 v2 没有 RX 直调、SU-1 或新增 UI。**

Do not interchange the files. Other C/N/S/O suffixes are not adapted in this release. Existing experimental filenames and bytes are retained; renaming the repository does not create new firmware behavior. **V100 SUB TTL is not implemented; V480 v2 has no RX direct adjustment, SU-1 extension or new UI.**

## 文件来源 / Provenance

每个 BIN 由对应严格版本补丁工具从固定原厂原件重建，再与此前交付文件的完整 SHA 比较。发布的是修改版 BIN，不附原厂固件备份；源码、补丁清单与本地复现方式同时保留。

Each BIN is reproduced from its pinned official input with its own exact-version patcher, then compared against the previously delivered full-image SHA. Modified BINs are published; official backup images are not bundled. Source, patch manifests and local reproduction remain available.

[V100 工具 / tool](../native/README.md) · [V480 工具 / tool](../v480/README.md) · [恢复与 Gate / recovery and gates](native/RECOVERY.md)
