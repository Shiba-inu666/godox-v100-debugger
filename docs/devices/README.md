# 支持型号 / Supported devices

[首页 / Home](../../README.md) · [文档 / Docs](../README.md) · [BIN 下载 / Downloads](../DOWNLOADS.md)

当前提供 **V100F 1.03、V100C 1.11、V100N 1.05、V100S 1.06、V100O 1.04 与 V480F 1.03** 的独立版本。作者的刷入反馈仅涉及 F 版设备；新增 C/N/S/O R10 均未实机验收。其他版本不自动兼容。

Separate exact-version packages cover V100F/C/N/S/O and V480F. Hardware deployment reports concern the owned F devices only; the new C/N/S/O R10 ports have no hardware acceptance. Unknown versions are not automatically compatible.

| 型号 / Model | 当前版本 / Revision | 功能重点 / Focus | 源码与工具 / Source and tools |
|---|---|---|---|
| [V100F R10](../../native/r10/README.md) | R10 | 机顶/RX 直调；主控/RX 手动 SU-1、原生 UI 与修复 / Wi-Off/RX direct control; Sender/RX manual SU-1 and native UI repairs | [native/](../../native/README.md) |
| [V100C/N/S/O R10](../../native/ports/README.md) | R10 experimental | 单灯控制、原厂彩色组名、副灯拖动；未实机验收 / Group editors, native badges, SUB dragging; no hardware acceptance | [native/ports](../../native/ports/README.md) |
| [V480F](V480F.md) | Rotary-direct v2 | Wi-Off 主屏 TTL FEC / M 直调，保留步进 / Wi-Off direct FEC/manual power with factory steps | [v480/](../../v480/README.md) |

每款页面包含输入/输出身份和验证边界。机器可读的 [catalog.json](catalog.json) 将型号对应到独立补丁清单，不用于猜测或自动适配未知版本。

Each model page records image identities and evidence limits. [catalog.json](catalog.json) maps models to their own patch records; it is not a heuristic for adapting unknown versions.
