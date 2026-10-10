# 两台设备的刷入与验证状态 / Device deployment status

Updated: **2026-10-10**.

**R10 发布补充：** V100F R10 已完成离线验证，尚无绑定该版本 SHA 的真机验收记录。下列 2026-10-09 作者反馈与 R7/V480 下载记录保留为历史证据。

**R10 release note:** V100F R10 is offline-validated; no hardware acceptance report is bound to its SHA. The 2026-10-09 maintainer report and R7/V480 download records below remain historical evidence.

## 作者反馈 / Maintainer report

项目作者确认，目前拥有并开展本项目的设备为 **V100F 与 V480F**，两台均已刷入项目修改固件。因此项目应被描述为“已在作者两台设备上刷入的实验固件项目”，不再笼统写成“从未刷机的纯离线项目”。

The maintainer confirms that the project currently uses **V100F and V480F**, and that modified project firmware has been flashed onto both. The project is therefore described as experimental firmware deployed on the maintainer's two devices, rather than an entirely never-flashed offline experiment.

| 设备 / Device | 作者报告 / Report | 本次提供的下载 / Published download |
|---|---|---|
| V100F | 已刷入修改固件 / Modified firmware flashed | V1.03 R7 |
| V480F | 已刷入修改固件 / Modified firmware flashed | V1.03 rotary-direct v2 |

反馈未提供两台设备各自在机文件的 SHA，也没有逐项确认此次下载版本的全部功能。因而“已经刷入”是设备层面的作者报告；下载文件的精确身份由本地重建、摘要和发布回读核验，不把二者合并为每个下载字节都已完成实机验收。

The report does not bind each installed image to a SHA or confirm every feature of these downloadable revisions. “Flashed” is a device-level maintainer report. Exact download identity is established separately by reproduction, hashes and release readback; it is not represented as complete hardware acceptance of every published byte.

## 功能范围 / Feature scope

- **V100F R7**：机顶/从属主灯直调，主控/从属原生 SU-1 UI、对应普通闪光路径、主控主灯 OFF 时副灯独立、UI 层级和字形修复。副灯仍按本地手动功率，未开启 TTL。
- **V480F v2**：Wi-Off 机顶主界面 TTL FEC / M 功率直调，尊重原厂步进和加速。无线角色继续使用原厂操作，本版不加入 SU-1 扩展。

V100F R7 implements main-screen rotary changes, native SU-1 controls and covered normal firing routes, main-OFF SUB-only operation, layering and glyph repairs. SUB remains manual. V480F v2 implements Wi-Off direct FEC/manual-power control with original step/acceleration; wireless roles retain stock operation and no SU-1 extension is added.

## 尚未由本次反馈证明的事项 / Not established by this report

成功刷入不等于所有相机、HSS、无线组合、长时间连拍、热行为或升级失败恢复均已验收。旧 JSON 中的 `hardware_verified: false`、`device_written: false` 是当时脚本运行的事实，保留历史记录；最新作者设备反馈单独存于 [HARDWARE_STATUS.json](HARDWARE_STATUS.json)。

Successful flashing does not establish complete camera, HSS, radio, sustained-shooting, thermal or failed-update recovery coverage. Older JSON `hardware_verified: false` / `device_written: false` fields describe those historical tool runs and remain intact. The new maintainer report is recorded separately in [HARDWARE_STATUS.json](HARDWARE_STATUS.json).
