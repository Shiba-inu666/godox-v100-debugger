# 设备刷入与验证状态 / Device deployment status

Updated: **2026-10-10**.

**R10 发布说明：** V100F R10 已完成离线验证，尚无绑定该版本 SHA 的真机验收记录。下列 2026-10-09 作者反馈与 R7/V480 下载记录保留为历史证据。

**R10 release note:** V100F R10 is offline-validated; no hardware acceptance report is bound to its SHA. The 2026-10-09 maintainer report and R7/V480 download records below remain historical evidence.

## V480F R10b · 2026-10-10

R10b 的主控单灯页、从属 TTL/M 直调和组选项断电记忆已完成离线验证：23,652 项功能检查、1,562 次通信中断检查、53 项镜像检查。尚未刷写或进行本版本真机验收；2026-10-09 的 V480 反馈不用于证明 R10b。实际断电保持、写入/擦除中掉电及无线时序仍待设备验证。

R10b is offline-validated only. No R10b device write or hardware acceptance is claimed; physical flash retention, interrupted programming/erase and RF timing remain unverified. [发布与验证 / Release evidence](../v480/r10/README.md)。

## C/N/S/O · 2026-10-10

作者确认暂时没有 V100C、V100N、V100S、V100O 实机。因此新增四款 R10 仅记录离线验证，`hardware_verified: false`；未刷入设备，也没有借用 F 版的实机反馈作为证明。

No C/N/S/O hardware was available. Their R10 ports are offline-validated prereleases only; no device writes or hardware acceptance are claimed.

## 作者反馈 / Maintainer report

项目作者确认，目前用于本项目的设备为 **V100F 与 V480F**，两台均已刷入项目修改固件。因此本项目应描述为"已在作者两台设备上刷入的实验固件项目"，不是从未刷机的纯离线项目。

The maintainer confirms that the project currently uses **V100F and V480F**, and that modified project firmware has been flashed onto both. The project is therefore described as experimental firmware deployed on the maintainer's two devices, rather than an entirely never-flashed offline experiment.

| 设备 / Device | 作者报告 / Report | 本次提供的下载 / Published download |
|---|---|---|
| V100F | 已刷入修改固件 / Modified firmware flashed | V1.03 R7 |
| V480F | 已刷入修改固件 / Modified firmware flashed | V1.03 rotary-direct v2 |

该反馈未提供两台设备各自在机文件的 SHA，也没有逐项确认下载版本的全部功能。"已刷入"是设备层面的作者报告；下载文件的精确身份由本地重建、摘要与发布回读单独核验，两者不合并为每个下载字节都已完成实机验收。

The report does not bind each installed image to a SHA or confirm every feature of these downloadable revisions. “Flashed” is a device-level maintainer report. Exact download identity is established separately by reproduction, hashes and release readback; it is not represented as complete hardware acceptance of every published byte.

## 功能范围 / Feature scope

- **V100F R7**：机顶 Wi-Off 与从属 Receiver 主界面主灯旋钮直调；主控/从属原生 SU-1 界面与已覆盖的普通闪光路径；主控主灯 OFF 时副灯可独立发光；UI 层级与字形修复。副灯仍按本地手动功率输出，未实现 TTL。
- **V480F v2**：机顶 Wi-Off 主界面 TTL 曝光补偿 / M 功率直调，保留原厂步进与加速。无线角色继续使用原厂操作，本版不加入 SU-1 扩展。

V100F R7 implements main-screen rotary changes, native SU-1 controls and covered normal firing routes, main-OFF SUB-only operation, layering and glyph repairs. SUB remains manual. V480F v2 implements Wi-Off direct FEC/manual-power control with original step/acceleration; wireless roles retain stock operation and no SU-1 extension is added.

## 本反馈尚未证明的事项 / Not established by this report

成功刷入不等于所有相机组合、HSS、无线环境、长时间连拍、热行为或升级失败恢复均已验收。旧 JSON 中的 `hardware_verified: false`、`device_written: false` 是当时脚本运行的事实，保留为历史记录；最新作者设备反馈单独存于 [HARDWARE_STATUS.json](HARDWARE_STATUS.json)。

Successful flashing does not establish complete camera, HSS, radio, sustained-shooting, thermal or failed-update recovery coverage. Older JSON `hardware_verified: false` / `device_written: false` fields describe those historical tool runs and remain intact. The new maintainer report is recorded separately in [HARDWARE_STATUS.json](HARDWARE_STATUS.json).
