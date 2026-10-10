# R7 experimental · 原生补丁公开版 / Native patch publication

> 历史首次源码发布记录。后续版本与各型号 BIN 请见：[最新下载](https://github.com/Shiba-inu666/godox-firmware-mods/blob/main/docs/DOWNLOADS.md)。
> Historical first source-only publication. V480 and both BIN downloads are now available: [current downloads](https://github.com/Shiba-inu666/godox-firmware-mods/blob/main/docs/DOWNLOADS.md).

## 中文

这是 V100F V1.03 原生补丁的公开复现包，同时保留原有的电脑端调试工作台。

本版包含的功能：

- 机顶 Wi-Off 与从属 Receiver 主界面，旋钮直接调整主灯 TTL 曝光补偿或 M 功率。
- 主控 Sender 中原生的本机副灯行，以及从属 Receiver 原生的副灯入口和弹窗。
- 在已覆盖的 TEST、普通相机曝光和 RX 无线触发路径上，支持手动功率的 SU-1 副灯。
- 主控普通曝光下，主灯 OFF 时副灯可以独立走发光路径。
- 原生行样式、弹窗布局、对象生命周期、下拉面板层级和点击命中的修复。
- R7 专项修复：用原厂字体里实际存在的单字母 **S**，替换原来显示为空框的 SUB 标签。

这个公开包新增了精确版本补丁工具、三段 C/汇编辅助代码、可移植离线验证，以及中英文完整历程和风险记录。R7 的发光代码与 R6/R5 相同；**SU-1 副灯的 TTL 未实现**。

验证记录：9,399 项可移植功能检查、90 项 TTL 研究观测、10 项补丁工具测试和 26 项工作台测试；辅助代码重新编译后与既有 R7 字节完全一致。更早的 39,851 项离线工程记录单独归档，与上述数量有重叠，不相加。

实机整体验收、真实的同步与光量、设备完整性机制以及失败恢复流程仍未完成。本次为 **prerelease**，不代表正式 Canary 放行。

完整的原厂/修改版 BIN 没有随发布附上。请自行准备指定的官方原件，用补丁工具在本地生成候选文件；工具不连接设备、不刷机、也不覆盖原件。

- [中文完整历程](https://github.com/Shiba-inu666/godox-firmware-mods/blob/r7-experimental/docs/PROJECT_HISTORY.md)
- [生成与验证说明](https://github.com/Shiba-inu666/godox-firmware-mods/blob/r7-experimental/native/README.md)
- [验证与限制](https://github.com/Shiba-inu666/godox-firmware-mods/blob/r7-experimental/docs/native/VALIDATION.md)

## English

This release publishes the reproducible native patch kit for **V100F V1.03**, alongside the existing desktop workbench.

Cumulative features:

- Direct main-screen rotary adjustment of TTL FEC or manual power in Wi-Off / Receiver.
- A native local-SUB row in Sender and native Receiver entry/modal.
- Manual SU-1 support in covered TEST, normal shutter and RX radio-trigger paths.
- A SUB-only branch with Sender main OFF in the covered normal-exposure path.
- Native styling, modal geometry, object-lifetime, drawer-layer and hit-test fixes.
- R7-specific repair: a single **S** from a verified native font replaces missing SUB glyphs.

The package adds an exact-image patcher, three C/assembly helpers, a portable execution lab, detailed bilingual history and risk records. R7 retains the R6/R5 firing code. **SU-1 TTL is not implemented.**

Validation includes 9,399 portable functional checks, 90 separate TTL observations, 10 patcher tests and 26 desktop tests. Rebuilt helpers exactly match the established R7 bytes. The broader 39,851-check historical engineering run is archived separately and overlaps these results.

Complete hardware acceptance, real synchronization/energy, device integrity and failed-update recovery remain unresolved. This is a **prerelease**, not formal Canary approval.

Complete vendor/candidate BINs are not attached. Supply the exact official input locally and use the patcher to generate the candidate. No device connection, flashing or input overwrite is performed.

- [Detailed English history](https://github.com/Shiba-inu666/godox-firmware-mods/blob/r7-experimental/docs/PROJECT_HISTORY.en.md)
- [Reproduction and verification guide](https://github.com/Shiba-inu666/godox-firmware-mods/blob/r7-experimental/native/README.md)
- [Recovery and gates](https://github.com/Shiba-inu666/godox-firmware-mods/blob/r7-experimental/docs/native/RECOVERY.md)

## Exact identities / 精确身份

- Original / 原件: `fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787`
- R7: `8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761`
- Size / 大小: 1,002,732 bytes; 24 patch regions; 4,018 differing bytes.
- Supported model / 支持机型: V100F only. Earlier V480 research is documented, not promoted as R7 support.
