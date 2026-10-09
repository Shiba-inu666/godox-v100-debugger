# Godox Firmware Mods · 神牛闪光灯固件修改项目

**简体中文** | [English](README.en.md)

神牛闪光灯固件研究与功能改进项目，**目前包含 V100 和 V480 两款灯，具体适配 V100F / V480F V1.03**。项目从旋钮直调出发，逐步加入 V100 的 SU-1 副灯扩展、原生界面修复、离线调试和可复现补丁工具。

**作者已在自己的 V100F 和 V480F 上刷入项目修改固件**（2026-10-09 作者反馈）。当前两款灯功能范围不同，见下表；刷入反馈与完整场景验收分别记录于[设备状态](docs/HARDWARE_STATUS.md)。项目与 Godox 官方无隶属关系。

## BIN 下载

| 设备 | 当前下载版本 | 文件 | 主要功能 |
|---|---|---|---|
| **V100F V1.03** | R7 experimental | [下载 V100F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin) | 机顶/从属主灯直调、SU-1 主控/从属支持、主灯 OFF 时副灯独立及 UI 修复 |
| **V480F V1.03** | Rotary-direct v2 | [下载 V480F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin) | Wi-Off 机顶主界面 TTL FEC / M 功率直调，保留原厂步进和加速路径 |

[完整发布页与校验文件](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-v480-2026-10-09) · [下载、功能对照与 SHA-256](docs/DOWNLOADS.md)

只下载与设备型号后缀一致的文件。两款均为实验修改版，不是官方固件；目前不支持其他相机后缀。**V100 的副灯 TTL 尚未实现，V480 版没有加入 V100 的 SU-1 扩展或 RX 直调。**

## 两款灯实现了什么

| 功能 | V100F R7 | V480F v2 |
|---|---|---|
| Wi-Off 主界面旋钮直接调 TTL 曝光补偿 | 已实现，复用原厂 ±3 EV / 1/3 EV 规则 | 已实现，复用原厂 ±3 EV / 1/3 EV 规则 |
| Wi-Off 主界面旋钮直接调 M 功率 | 已实现，复用原厂功率规则 | 已实现，尊重 0.1 / 0.3 步进及原厂加速 |
| Receiver 主界面主灯直调 | 已实现；后续无线命令仍可更新主灯 | 未加入；保持原厂操作 |
| 主控/从属原生副灯 UI 与普通发光支持 | 已实现；副灯按本地手动功率 | 未加入 |
| Sender 主灯 OFF、副灯单独普通曝光 | 已实现对应路径 | 未加入 |
| 副灯与 ZOOM/下拉栏重叠、缺字修复 | 已修复；标识为单字母 S | 不涉及本补丁 |
| 菜单、MODE、ZOOM、锁屏等非目标页面 | 回落原逻辑 | 回落原逻辑 |
| 作者已刷入修改固件 | 已反馈 | 已反馈 |

## 文档与源码

| 想做什么 | 入口 |
|---|---|
| 查看每款灯的范围、版本和已知限制 | [V100F R7](docs/devices/V100F.md) · [V480F v2](docs/devices/V480F.md) |
| 了解开发经过与历次问题修复 | [中文完整历程](docs/PROJECT_HISTORY.md) · [更新记录](CHANGELOG.md) |
| 核对设备反馈和硬件验收范围 | [两台设备的状态](docs/HARDWARE_STATUS.md) |
| 从原厂文件复现、还原或验证 | [统一复现指南](docs/REPRODUCE.md) |
| 阅读实现 | [V100 C / 汇编](native/src/) · [V480 汇编](v480/src/) · [目录说明](DIRECTORY_LAYOUT.md) |
| 查看固件格式、测试与副灯 TTL 研究 | [技术文档索引](docs/README.md) |
| 在电脑上观察参数与调用 | [调试工作台](docs/debugger/README.zh-CN.md) |
| 反馈问题或贡献 | [贡献说明](CONTRIBUTING.md) · [提交问题](https://github.com/Shiba-inu666/godox-firmware-mods/issues/new/choose) |

## 项目走到了哪一步

从两款固件的格式与 ARM 输入链路分析开始，先实现旋钮直调，再逐步解决 V100 无线角色下副灯 UI、TEST 与真实曝光分支、主灯 OFF、副灯遮挡及原生字形问题。V480 保持独立的机顶旋钮直调范围。详细的失败现象、修订理由和证据保留在中英文历程中。

公开包已有可复现源码和离线执行记录：V100 的可移植子集包含 9,399 项功能检查及单列的 90 项 TTL 研究观测；V480 单型号包含 12,489 项功能、746 次中断插入和 1,386 项整镜像检查。**这些是电脑端检查，完整实机验收和失败恢复仍未完成。** [验证说明](docs/native/VALIDATION.md) · [恢复与 Gate](docs/native/RECOVERY.md)

项目名称采用直接描述用途的 **Godox Firmware Mods**。文档组织参考哈苏、理光和 FujiHack 的固件研究项目；具体来源与借鉴范围见[参考项目](docs/REFERENCES.md)。
