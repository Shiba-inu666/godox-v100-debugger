# Godox Firmware Mods · 神牛闪光灯固件修改项目

**简体中文** | [English](README.en.md)

这是一个神牛闪光灯固件逆向与功能增强项目，**目前覆盖 V100F/C/N/S/O 与 V480F；各型号使用自己的原厂版本**。项目最初落地了旋钮直接调整闪光灯TTL/M功率的功能，后续逐步为 V100 加入 SU-1 副闪功能扩展、原生界面修复、离线调试工具以及可复现补丁套件。

**作者已在自用的 V100F 与 V480F 上刷入并验证了修改后的固件**（2026-10-09 更新）。两款机型当前支持的功能各有侧重，具体见下表；实机刷入反馈与完整场景验收分开记录在[设备状态](docs/HARDWARE_STATUS.md)中。本项目为个人开源研究项目，与 Godox 官方无任何隶属关系。

## BIN 下载

| 设备 | 当前下载版本 | 文件 | 主要功能 |
|---|---|---|---|
| **V100F V1.03** | R10 experimental | [下载 V100F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-r10-2026-10-10/v1.03r10.bin) | 保留 R9 单灯控制与原厂手势，新增原厂彩色组名和主控 S 行拖动调功率 |
| **V100C V1.11** | R10 experimental | [下载 V100C BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100c-r10-2026-10-10/v1.11r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100N V1.05** | R10 experimental | [下载 V100N BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100n-r10-2026-10-10/v1.05r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100S V1.06** | R10 experimental | [下载 V100S BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100s-r10-2026-10-10/v1.06r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100O V1.04** | R10 experimental | [下载 V100O BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100o-r10-2026-10-10/v1.04r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V480F V1.03** | Rotary-direct v2 | [下载 V480F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin) | 机顶 Wi-Off 主界面 TTL / M 功率直调，保留原厂步进与加速逻辑 |

[完整发布页与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-v480-2026-10-09) · [下载说明、功能对照与 SHA-256 校验](docs/DOWNLOADS.md)

请务必下载与设备型号后缀完全匹配的固件，不同后缀不可混用。以上均为实验修改版，非官方固件；新增 C/N/S/O 版尚无实机验收。**V100 副灯 TTL 暂未实现；V480 版不含 V100 的 SU-1 扩展与 RX 直调功能。**

**V100F R10（2026-10-10）：** [发布与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-r10-2026-10-10) · [操作、源码与原生预览](native/r10/README.md)。下载文件简化为 `v1.03r10.bin`，仅用于 V100F V1.03。已通过 13,966 项原生功能检查及 37 项镜像检查，尚待真机验收；此前的刷入反馈不代表 R10 已验收。下表保留 R7/V480 基线功能记录。

**V100 C/N/S/O R10：** [各型号说明、源码与验证记录](native/ports/README.md)。Canon 版保留 A–E，其余保留 M/A–D；均从对应原厂版本单独构建。

## 功能对比

| 功能 | V100F R7 | V480F v2 |
|---|---|---|
| 机顶模式 主界面旋钮直调 TTL 曝光补偿 | 已实现，沿用原厂 ±3 EV / 1/3 EV 规则 | 已实现，沿用原厂 ±3 EV / 1/3 EV 规则 |
| 机顶模式 主界面旋钮直调 M 功率 | 已实现，复用原厂功率调节逻辑 | 已实现，保留 0.1 / 0.3 步进及原厂加速机制 |
| 接收模式 主界面主灯直调 | 已实现；后续无线命令仍可覆盖更新主灯参数 | 未加入；保持原厂操作逻辑 |
| 主控/从属模式原生副闪 UI 与普通闪光支持 | 已实现；副灯按本地手动功率输出 | 未加入 |
| 主控模式 主灯 OFF、副闪单独功率调节 | 已打通对应工作路径 | 未加入 |
| 副闪与 ZOOM/下拉栏重叠、缺字修复 | 已修复；标识简化为单字母 S | 不涉及本补丁 |
| 菜单、MODE、ZOOM、锁屏等非目标页面 | 原厂逻辑 | 原厂逻辑 |
| 作者实机刷入验证 | 已反馈 | 已反馈 |

## 模拟器预览

项目还提供 **V100F 浏览器离线模拟器（调试工作台）**，可切换机顶、主控和从属模式，观察参数调整、内存变化与调用记录。界面由电脑端适配，不是实机屏幕的完整仿真。[启动与使用说明](docs/debugger/README.zh-CN.md)。

![V100F 离线模拟器：机顶 Multi 界面](debug-preview-v3.jpg)

![V100F 离线模拟器：从属模式与接收调试](receiver-layout-fixed.jpg)

## 文档与源码

| 想做什么 | 入口 |
|---|---|
| 查看单款机型的功能范围、版本细节与已知限制 | [V100F R7 说明](docs/devices/V100F.md) · [V480F v2 说明](docs/devices/V480F.md) |
| 了解开发历程与历次问题修复 | [中文完整历程](docs/PROJECT_HISTORY.md) · [更新记录](CHANGELOG.md) |
| 核对实机反馈与硬件验收范围 | [两台设备的状态](docs/HARDWARE_STATUS.md) |
| 从原厂固件复现、还原或校验补丁 | [统一复现指南](docs/REPRODUCE.md) |
| 阅读实现源码 | [V100 C / 汇编](native/src/) · [V480 汇编](v480/src/) · [目录结构说明](DIRECTORY_LAYOUT.md) |
| 查看固件格式、测试方案与副灯 TTL 研究 | [技术文档索引](docs/README.md) |
| 在电脑端观察参数与调用流程 | [调试工作台](docs/debugger/README.zh-CN.md) |
| 反馈问题或参与贡献 | [贡献说明](CONTRIBUTING.md) · [提交 Issue](https://github.com/Shiba-inu666/godox-firmware-mods/issues/new/choose) |

## 项目进度

项目从两款机型的固件格式与 ARM 输入链路逆向分析起步，先落地了旋钮直接调整闪光灯TTL/M功率的功能，之后逐步解决了 V100 无线模式下副灯 UI 异常、TEST 与实际曝光分支冲突、主灯关闭后副灯独立工作、界面重叠缺字等原生问题。V480 则保持独立的机顶旋钮直调优化方向。所有问题现象、修改理由与验证依据都详细记录在中英文项目历程中。

目前已公开可复现源码与离线测试记录：V100 可移植子集包含 9,399 项功能检查与 90 项独立 TTL 研究观测；V480 单机型通过了 12,489 项功能校验、746 次条件中断注入、1,386 次整镜像执行与 10 项补丁工具测试。

**以上均为电脑端自动化校验结果，完整的实机全场景验收、光量长稳与变砖恢复机制尚未完全完成。**
[验证说明](docs/native/VALIDATION.md) · [恢复与安全机制](docs/native/RECOVERY.md)

项目定名为 **Godox Firmware Mods**，直白清晰。文档架构参考了哈苏、理光与 FujiHack 等成熟固件研究项目，具体参考来源与借鉴范围见[参考项目](docs/REFERENCES.md)。
