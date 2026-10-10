# 更新记录 / Changelog

[首页 / Home](README.md) · [完整中文历程](docs/PROJECT_HISTORY.md) · [Full English history](docs/PROJECT_HISTORY.en.md)

下面按公开整理时间和固件修订顺序记录；早期步骤没有独立日期的，不补造日期。仓库名称变化不代表固件版本变化。

Entries follow publication dates and firmware revision order. Dates are not invented for early revisions. Repository naming changes do not imply new firmware behavior.

## 2026-10-10 · V100F R10

- 发布 `v1.03r10.bin`、源码和校验文件；简化文件名，BIN 字节与本地 R10 候选一致。
- 单灯页 A/B/C/D 使用原厂字体、颜色和圆角色块；主控 S 行增加相对左右拖动功率，短按和纵向滚动保留。
- 保留 R9 单灯控制、TTL/M 与暂停/恢复、原厂长按和滑动；单灯页旋钮只调当前灯功率或 TTL 补偿。
- 13,966 项原生功能检查和 37 项镜像检查通过；尚待真机验收。只适用于 V100F V1.03。

- Published `v1.03r10.bin` with source and checksums; shortened filename, identical bytes to the local R10 candidate.
- Adds exact native A/B/C/D badges and relative Sender S-row power dragging, retaining R9 controls and gestures.
- 13,966 native functional checks and 37 image checks passed; V100F V1.03 only, hardware acceptance pending.

## 2026-10-10 · V100F R9

- 发布 R9 实验 BIN、源码、完整补丁和摘要绑定的验证记录；保留 R7 与中间 R8 源码。
- 主控 M/A–D 保留原厂长按 TTL/M/OFF 与滑动调节，新增单击进入独立页；左侧 TTL/M、右侧暂停/恢复，旋钮固定调当前灯功率或 TTL 补偿。
- 修复从属页“副灯”命名和退出时提前消失、主控 S 字号；副灯仍为手动。
- 12,159 项原生功能检查和 37 项镜像检查通过；R9 尚待真机验收。

- Published R9 experimental BIN, source, full patch and hash-bound validation, retaining R7 and intermediate R8 source.
- Preserves Sender long press and swipe; adds short-tap M/A–D editors with TTL/M, pause/resume and a power-only encoder.
- Retains SUB naming/lifecycle and S typography repairs. SUB remains manual. 12,159 native functional checks and 37 image checks passed; R9 hardware acceptance is pending.

## 2026-10-09 · Godox Firmware Mods

- 项目正式采用 **Godox Firmware Mods｜神牛闪光灯固件修改项目**；重新组织中英文首页、型号入口、文档索引、复现说明与反馈模板。
- 发布 V100F R7 与 V480F v2 的源码、独立工具、BIN 和校验文件；作者报告两台灯均已刷入项目修改固件。
- 两款既有 BIN 字节及 SHA-256 保持不变。改名与文档整理没有新增副灯 TTL、V480 RX 直调或其他固件功能。

- Adopted **Godox Firmware Mods**, with bilingual landing pages, model guides, documentation index, reproduction guide and issue templates.
- Published V100F R7 and V480F v2 source, separate tools, BINs and checksums. The maintainer reports flashing both devices.
- Existing BIN bytes and SHA-256 values are unchanged. Naming/documentation work does not add SU-1 TTL or V480 RX direct adjustment.

## V100F · R7 → R2

| 修订 / Revision | 改变 / Change |
|---|---|
| R7 | 使用真实原厂字形的单字母 S，修复 SUB 方框 / Use an available native S glyph instead of missing SUB glyphs |
| R6 | 修复 RX 下拉层级、触摸命中和焦点问题 / Repair RX drawer stacking, hit testing and focus |
| R5 | 主控主灯 OFF 时副灯独立普通曝光；原生行样式与对象生命周期 / SUB-only normal exposure with Sender main OFF; native row styling and object lifetime |
| R4 | 覆盖普通相机快门和 RX 副灯路径；沿用原厂就绪判断；弹窗布局修复 / Normal shutter/RX SUB paths, stock readiness decisions and modal geometry |
| R3 | 主控/从属 TEST 路径副灯支持 / SUB support in Sender/RX TEST paths |
| R2 | RX 副灯布局，分开 ZOOM 区域 / RX SUB layout separated from ZOOM |

以上修订之前，已完成机顶主灯直调原型，随后扩展到 V100 RX 主屏。各阶段的实机反馈、离线证据与限制见完整历程；该历史发布按 R7 身份核对，不提供旧修订降级建议。

The earlier main-screen rotary work preceded these revisions and later extended to V100 RX. See the full history for feedback, evidence and limits. That historical download identifies R7; historical revisions are not downgrade recommendations.

## V480F · Rotary-direct v2

Wi-Off 主屏直接调整 TTL FEC / M 功率；保留原厂步进与加速，修复输入重复消费和模式切换中断窗口；重算 V480 特有 MD5。其他页面及无线角色保留原行为。

Direct Wi-Off main-screen FEC/manual-power adjustment, preserving stock steps and acceleration. Addresses duplicate event consumption and the mode-change interrupt window; recomputes the V480-specific MD5. Other screens and wireless roles retain stock behavior.

## 副灯 TTL / SU-1 TTL

只有可行性研究与 90 项有界观测，尚未实现。/ Feasibility research and 90 bounded observations only; not implemented.
