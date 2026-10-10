# Godox Firmware Mods · 神牛闪光灯固件修改项目

**简体中文** | [English](README.en.md)

这是一个神牛闪光灯固件逆向与功能修改项目，**目前覆盖 V100F/C/N/S/O 与 V480F；各型号使用自己的原厂版本**。项目最初实现了旋钮直接调整 TTL 曝光补偿与 M 手动功率，之后为 V100 加入 SU-1 副灯控制和界面修复，并提供离线调试工具与可复现补丁。

作者在自用的 V100F 与 V480F 两台设备上已刷入本项目修改固件（2026-10-09 报告）；这份反馈没有绑定在机文件 SHA，不能替代当前 R10 的真机验收。各型号支持的功能见下表，实机反馈与验收范围记录在[设备状态](docs/HARDWARE_STATUS.md)。本项目为个人开源研究项目，与 Godox 官方无隶属关系。

## BIN 下载

### V100

| 设备 | 当前下载版本 | 文件 | 主要功能 |
|---|---|---|---|
| **V100F V1.03** | R10 experimental | [下载 V100F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-r10-2026-10-10/v1.03r10.bin) | 保留 R9 单灯控制与原厂手势，新增原厂彩色组名和主控 S 行拖动调功率 |
| **V100C V1.11** | R10 experimental | [下载 V100C BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100c-r10-2026-10-10/v1.11r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100N V1.05** | R10 experimental | [下载 V100N BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100n-r10-2026-10-10/v1.05r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100S V1.06** | R10 experimental | [下载 V100S BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100s-r10-2026-10-10/v1.06r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |
| **V100O V1.04** | R10 experimental | [下载 V100O BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100o-r10-2026-10-10/v1.04r10.bin) | R10 独立移植；单灯页、彩色组名、副灯拖动；未实机验收 |

### V480

| 设备 | 当前下载版本 | 文件 | 主要功能 |
|---|---|---|---|
| **V480F V1.03** | R10b experimental | [下载 V480F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v480-r10b-2026-10-10/v480f-v1.03r10b.bin) | 主控单灯页、TTL/M 与暂停；机顶/从属旋钮直调；从属 A–E 组别断电记忆 |

[R7 / V480 基线发布与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-v480-2026-10-09) · [全部型号下载、功能对照与 SHA-256 校验](docs/DOWNLOADS.md)

请下载与设备型号后缀和原厂版本完全匹配的固件，不同后缀不可混用。以上均为实验修改版，非官方固件；所有 V100 R10 与 V480 R10b 版本尚待真机验收。**V100 副灯 TTL 暂未实现；V480 R10b 已加入从属直调，不含 V100 的 SU-1 扩展。**

**V100F R10（2026-10-10）：** [发布与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-r10-2026-10-10) · [操作、源码与原生预览](native/r10/README.md)。下载文件简化为 `v1.03r10.bin`，仅用于 V100F V1.03。已通过 13,966 项原生功能检查及 37 项镜像检查，尚待真机验收；此前的刷入反馈不代表 R10 已验收。下表保留 R7/V480 基线功能记录。

**V100 C/N/S/O R10：** [各型号说明、源码与验证记录](native/ports/README.md)。Canon 版保留 A–E，其余保留 M/A–D；均从对应原厂版本单独构建。

**V480F R10b（2026-10-10）：** [发布与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v480-r10b-2026-10-10) · [操作、源码与原生预览](v480/r10/README.md)。保留原厂主控长按和滑动，单击 M/A–D 进入单灯页，提供 TTL/M、暂停/恢复；旋钮只调当前灯数值。从属 TTL/M 直调，组选项 A–E 确认后保存，切换机顶/主控再关机也保留。23,652 项功能检查、1,562 次中断检查与 53 项镜像检查通过，尚待真机验收。

## 基线功能对比

| 功能 | V100F R7 | V480F v2 |
|---|---|---|
| 机顶 Wi-Off 主界面旋钮直调 TTL 曝光补偿 | 已实现，沿用原厂 ±3 EV / 1/3 EV 规则 | 已实现，沿用原厂 ±3 EV / 1/3 EV 规则 |
| 机顶 Wi-Off 主界面旋钮直调 M 功率 | 已实现，复用原厂功率调节逻辑 | 已实现，保留 0.1 / 0.3 步进及原厂加速机制 |
| 从属 Receiver 主界面主灯直调 | 已实现；后续无线命令仍可覆盖更新主灯参数 | 未加入；保持原厂操作逻辑 |
| 主控/从属模式原生副灯 UI 与普通闪光支持 | 已实现；副灯按本地手动功率输出 | 未加入 |
| 主控模式主灯 OFF 时，副灯可独立发光 | 已覆盖对应普通曝光路径 | 未加入 |
| 副灯与 ZOOM/下拉栏重叠、缺字修复 | 已修复；标识简化为单字母 S | 不涉及本补丁 |
| 菜单、MODE、ZOOM、锁屏等非目标页面 | 原厂逻辑 | 原厂逻辑 |
| 作者实机刷入反馈 | 已报告（R7 时期） | 已报告（v2 时期） |

## 模拟器预览

项目还提供 **V100F 浏览器离线模拟器（调试工作台）**，可切换机顶、主控和从属模式，观察参数调整、内存变化与调用记录。界面由电脑端适配，不是实机屏幕的完整仿真。[启动与使用说明](docs/debugger/README.zh-CN.md)。

![V100F 离线模拟器：机顶 Multi 界面](debug-preview-v3.jpg)

![V100F 离线模拟器：从属模式与接收调试](receiver-layout-fixed.jpg)

## 文档与源码

| 想做什么 | 入口 |
|---|---|
| 查看单款机型的功能范围、版本细节与已知限制 | [V100F 说明](docs/devices/V100F.md) · [V100 C/N/S/O 说明](native/ports/README.md) · [V480F 说明](docs/devices/V480F.md) |
| 了解开发历程与历次问题修复 | [中文完整历程](docs/PROJECT_HISTORY.md) · [更新记录](CHANGELOG.md) |
| 核对实机反馈与硬件验收范围 | [两台设备的状态](docs/HARDWARE_STATUS.md) |
| 从原厂固件复现、还原或校验补丁 | [统一复现指南](docs/REPRODUCE.md) |
| 阅读实现源码 | [V100 C / 汇编](native/src/) · [V480 汇编](v480/src/) · [目录结构说明](DIRECTORY_LAYOUT.md) |
| 查看固件格式、测试方案与副灯 TTL 研究 | [技术文档索引](docs/README.md) |
| 在电脑端观察参数与调用流程 | [调试工作台](docs/debugger/README.zh-CN.md) |
| 反馈问题或参与贡献 | [贡献说明](CONTRIBUTING.md) · [提交 Issue](https://github.com/Shiba-inu666/godox-firmware-mods/issues/new/choose) |

## 项目进度

项目从两款机型的固件格式与 ARM 输入链路逆向分析起步，先实现了旋钮直接调整闪光灯 TTL 曝光补偿与 M 手动功率的功能，之后逐步修复 V100 无线模式下副灯 UI 异常、TEST 与实际曝光分支冲突、主灯关闭后副灯独立工作、界面重叠缺字等问题。V480 在机顶旋钮直调基础上加入主控单灯页、从属直调与组别记忆。所有问题现象、修改理由与验证依据记录在中英文项目历程中。

目前已公开可复现源码与离线测试记录：V100F R7 基线的可移植子集包含 9,399 项功能检查与 90 项独立 TTL 研究观测；V480 单机型通过 12,489 项功能检查、746 次条件中断注入、1,386 次整镜像执行与 10 项补丁工具测试。R10 的新增验证分别记录在 F 版与 C/N/S/O 版说明中。

**以上均为电脑端自动化校验结果。完整的实机全场景验收、光量长稳与升级失败恢复机制尚未完成。**
[验证说明](docs/native/VALIDATION.md) · [恢复与安全机制](docs/native/RECOVERY.md)

项目定名为 **Godox Firmware Mods**。文档架构参考了哈苏、理光与 FujiHack 等成熟固件研究项目，具体参考来源与借鉴范围见[参考项目](docs/REFERENCES.md)。
