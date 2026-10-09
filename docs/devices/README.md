# 支持型号 / Supported devices

[首页 / Home](../../README.md) · [文档 / Docs](../README.md) · [BIN 下载 / Downloads](../DOWNLOADS.md)

当前只有 **V100 与 V480**；精确适配的是 **V100F V1.03 与 V480F V1.03**。作者确认自己的两台设备均已刷入项目修改固件。其他后缀和版本不自动兼容。

Only **V100 and V480** are currently included, specifically **V100F V1.03 and V480F V1.03**. The maintainer reports flashing both owned devices. Other suffixes and versions are not automatically compatible.

| 型号 / Model | 当前版本 / Revision | 功能重点 / Focus | 源码与工具 / Source and tools |
|---|---|---|---|
| [V100F](V100F.md) | R7 | 机顶/RX 直调；主控/RX 手动 SU-1、原生 UI 与修复 / Wi-Off/RX direct control; Sender/RX manual SU-1 and native UI repairs | [native/](../../native/README.md) |
| [V480F](V480F.md) | Rotary-direct v2 | Wi-Off 主屏 TTL FEC / M 直调，保留步进 / Wi-Off direct FEC/manual power with factory steps | [v480/](../../v480/README.md) |

每款页面包含输入/输出身份和验证边界。机器可读的 [catalog.json](catalog.json) 将型号对应到独立补丁清单，不用于猜测或自动适配未知版本。

Each model page records image identities and evidence limits. [catalog.json](catalog.json) maps models to their own patch records; it is not a heuristic for adapting unknown versions.
