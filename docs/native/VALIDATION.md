# 验证报告 / Validation report

Publication date: **2026-10-09**. Candidate: **V100F V1.03 R7 experimental**.

SHA-256: `8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761`.

## 如何理解“通过” / What a pass means

本项目分四层：文件可复现、原厂指令的有界执行、电脑端操作、实机物理效果。前三层通过不能自动推出第四层通过。脚本里的一次 check 可以是一项参数组合、一条不变量或一个观测，不等于一次独立硬件实验。

There are four layers: file reproducibility, bounded execution of original instructions, desktop interactions, and physical device behavior. Passing the first three does not establish the fourth. A “check” can be a parameter case, invariant or observation, not an independent hardware experiment.

## 本次公开包重新运行 / Publication reruns

| 检查 / Check | 数量 / Count | 覆盖 / Coverage |
|---|---:|---|
| Patcher unit tests | 10 | 精确输入/输出、逆变换、拒绝损坏/截断/扩展/已打补丁输入、原字节、重叠、边界、上下文、禁止覆盖 / Exact identity, inverse and fail-closed behavior |
| Desktop unit tests | 26 | 参数、模式、组隔离、菜单、回放、会话和 HTTP / Parameters, modes, groups, menus, replay and HTTP |
| Native glyph | 37 | 实际 S 字形存在、非空、布局 / Actual S glyphs and layout |
| Drawer | 296 | 对象顺序、层级、焦点、触摸命中 / Order, layering, focus and hit testing |
| Sender row | 171 | 原生行结构、显示和控件行为 / Row geometry and controls |
| Firing | 4,399 | 覆盖的 TEST、普通曝光/RX、就绪与回落 / Covered firing, readiness and fallbacks |
| Sender main OFF | 1,389 | 副灯独立、主灯不触发、原无线路径 / SUB-only, no main trigger, radio path |
| Stock readiness | 398 | 原路径跳过未就绪请求；未发现就绪等待循环 / Stock skip behavior, no ready-wait loop in covered paths |
| Wrapper | 2,317 | 钩子上下文、ABI、寄存器及原路径 / Contexts, ABI, registers and original paths |
| Modal | 392 | 原厂机顶弹窗几何及状态 / Factory-style modal geometry/state |
| TTL research | 90 | 观察主副灯预闪、测光与手动时长差异 / Preflash, metering and manual-duration observations |

八项原生功能 suite 合计 **9,399**；TTL 的 **90** 项单独记录。公开 runner 在运行前后锁定源码摘要，所有结果必须指向同一个候选 SHA。

The eight native functional suites total **9,399**. The **90 TTL observations are separate**. Source digests are checked before/after the run and each result must identify the same candidate.

- [公开 runner 汇总 / Public lab summary](../../native/evidence/PUBLIC_LAB_RESULTS.json)
- [源码重编译 / Source build verification](../../native/evidence/BUILD_VERIFICATION.json)
- [公开包检查 / Publication verification](../../native/evidence/PUBLICATION_VERIFICATION.json)
- [原生测试代码 / Native lab source](../../native/lab/)
- [补丁测试 / Patcher tests](../../native/tests/test_patcher.py)
- [工作台测试 / Desktop tests](../../tests/)

## 源码与机器码 / Source-to-byte match

使用 Homebrew LLVM / Clang 20.1.8，三段辅助代码与 R7 记录逐字节相同：

| Module | Bytes | SHA-256 |
|---|---:|---|
| fixed_main | 508 | `f627240aa800c69047901342057ac03b0f11febcee6f027c53c27b645a797246` |
| fire_su1 | 476 | `26efe0d775327938743ba2c65b071b25f6b39fd38c32ed4be2ce0f50e202110a` |
| native_sub | 3,003 | `bf7b5d51ba7743c0144ee592b67d614ceb5bf562b226b2fe4cb908177f405f09` |

总文件长度保持 1,002,732 字节，原件→R7→原件逆变换精确成立；向量和辅助负载保护区不变。其他编译器没有宣称能产生相同字节，工具遇到差异会停止。

All three rebuilt helpers match exactly. Complete image length is unchanged; original→R7→original is byte-exact, with vector and auxiliary regions preserved. Other compiler versions are not qualified and differing output is rejected.

## 历史完整工程记录 / Archived engineering run

[R7_VALIDATION_SUMMARY.json](../../native/evidence/R7_VALIDATION_SUMMARY.json) 汇总 **39,851** 项，原记录时间为 `2026-10-08T16:33:05.222251+00:00`（北京时间 10 月 9 日）。这是历史执行结果，不是本次公开 runner 的完整重跑。

另外还包括：旋钮功能 25,539、事件链 1,284、RX 布局 205、原生 UI 1,080、RF/ISR 顺序 2,344。对应的 JSON 报告已经公开，但这些更广的 runner 还没有全部移植过来。它们和上面的可移植子集有重叠，不能相加得到新的测试总数。

The archived record has **39,851 checks**, including broader rotary, event-chain, layout, native UI and RF/ISR coverage. Result JSON files are published, but not every historical runner is ported. The portable suite overlaps this record; the counts must not be summed as new coverage.

## 模型能验证什么 / Model scope

- 执行原厂和补丁的 Thumb 指令，观测模拟 RAM、调用、寄存器和选定外设请求。Original and patched Thumb instructions execute against simulated RAM and selected peripheral interfaces.
- 原生 UI 检查控件结构、字形、层级、生命周期和命中；不是 LCD 光学截图。Native UI checks model objects, glyphs, stacking, lifetime and hit testing, not an optical LCD capture.
- 就绪/发光验证使用虚拟 SysTick 与外设替身；发光请求不等于实际放电。Readiness/firing checks use virtual timing and stand-ins; a trigger request is not physical discharge.
- RF/ISR 顺序报告标题保留 `LATENCY_NOT_RESOLVED`，没有把顺序观测写成真实延迟预算已经闭合。RF/ISR ordering does not resolve physical latency.

## 实机反馈与未完成项 / Device feedback and open work

后续更新：作者已确认 V100F 与 V480F 均已刷入项目修改固件。原离线报告不追溯改写；最新设备状态见 [HARDWARE_STATUS](../HARDWARE_STATUS.md)。

Update: the maintainer reports both V100F and V480F flashed. Historical offline reports remain unchanged; see [current device status](../HARDWARE_STATUS.md).

开发期间收到过一些用户反馈：原机顶副灯/TEST 正常、无线角色 UI 已出现、TEST 与快门不一致，以及重叠/缺字。这些反馈推动了 R2–R7 的修改，但不能视为 R7 所有模式的最终验收。归档 R7 报告没有取得 R7 实机显示照片；本次发布也没有增加设备测试。

User reports established useful observations during development, including working on-camera SUB/TEST, visible wireless-role controls, mismatches between TEST and shutter behavior, overlaps and missing glyphs. They motivated revisions, not complete R7 acceptance. The archived R7 report had no R7 device-display confirmation, and publication adds no hardware test.

仍未闭合 / Still open:

- 相机主曝光、预闪与无线同步的实际时序和容差 / Actual exposure, preflash and RF timing margins.
- 主副灯光量、功率曲线、未充满行为与持续拍摄 / Optical energy, power curves, incomplete recharge and sustained shooting.
- 热保护、真实堆栈水位和长期切屏稳定性 / Thermal behavior, real stack high-water mark and long-running UI stability.
- 设备端完整性验证、升级失败恢复、可靠降级 / Device integrity validation, failed-update recovery and reliable downgrade.
- SU-1 TTL，以及其他机型/版本 / SU-1 TTL and other model/version support.

复现命令见 [native/README.md](../../native/README.md)。
