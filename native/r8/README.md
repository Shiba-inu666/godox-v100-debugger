# V100F V1.03 · R8 独立灯组控制

本地后续实验版，基于 GitHub `v100-v480-2026-10-09` 中的 V100F R7。已实际下载并核对发布资产：R7 SHA-256 为 `8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761`。GitHub 主分支基线为 `d445b7f342ef12c9ac7878c06beb9dbbed5e6b56`。

## 本轮四项修改

1. 从属页按实体返回／电源键进入原厂选择页时，副灯入口随旧屏幕一起退出，避免单独提前消失。共享控件句柄会先解绑，旧对象由原厂屏幕动画结束时释放。
2. 从属页副灯入口与机顶一致：中文“副灯”，英文“SUB”，使用相同原厂字库、位置及颜色。
3. 主控 S 的字形高度统一为 M/A–D 的 **29 像素**，文字框、基线和纵向位置对齐。原厂组名字库不包含 S，因此以 R7 内嵌 S 点阵生成同高度的 4 位抗锯齿字形，没有把缺字字库直接用于 S。
4. 单击主控 **M、A、B、C、D** 任一行的灯名或数字打开该灯独立页，列表加减按钮保留直接调整。左下为 TTL/M，右下为 ON/OFF；保留加减和旋钮调功率／TTL 曝光补偿，右上返回后焦点回到该灯。OFF 时可预选模式而不启用灯组，再开启时恢复所选模式。

S 仍是本机 SU-1 的手动副灯。新 TTL/M 按钮适用于 M/A–D；未实现 SU-1 TTL。

## 实现范围

- 原厂组模式、启用数组、无线掩码和 M 功率／TTL 补偿仍按原索引存储；S 不插入无线组数组。
- 独立页通过原厂组加减回调调整参数，沿用原厂显示格式及步进。新弹层的对象保存在原厂 LVGL 对象用户数据中，控件跟随父屏幕释放，不新增固定全局 RAM 地址。
- 发光、保护、无线协议和旋钮辅助代码保持与 R7 相同。只有 UI 辅助段与 UI 钩子改变。
- 直接从机顶／从属创建主控页面时，仍需先回收旧副灯子树：五组原生主控控件与完整旧页同时存在会耗尽固定 GUI 堆。这保留了 R7 的直接切换内存处理；正常经返回／选择页的退出过程保留完整副灯显示。
- 独立页数值刷新带状态缓存；未变化的周期不重复分配文字或重绘标签。

## 构建、验证、生成

从仓库根目录执行，原件仍须匹配公开 R7 工具所要求的官方 V100F V1.03 SHA。需要 LLVM/Clang 20 和原有 `native/requirements.txt` 的 Python 依赖。

```sh
.venv/bin/python native/r8/build.py
.venv/bin/python native/r8/validate.py
.venv/bin/python native/r8/package.py native/r8/out/r8
```

可用 `GODOX_LLVM_BIN`、`GODOX_LD_LLD` 指定本机 LLVM 工具。构建时可加 `--github-base /path/to/R7.bin`，要求下载文件与重建的 R7 逐字节相同。

生成器只接受通过本轮完整验证且源码、候选、各测试结果摘要未变化的版本。输出目录必须不存在，避免覆盖旧文件；写入后重新读取核对。验证包含新界面专项及原有下拉层级、原生副灯行、发光、就绪、调用约定和副灯弹窗回归。R7 的公开源码、补丁记录及既有验证摘要保持原样。

生成的 `V100F_V1.03_GROUP_CONTROL_R8_EXPERIMENTAL.bin` 是完整长度实验镜像，附 `SHA256SUMS.txt`、`PATCH_MANIFEST.json`、`VALIDATION.json`。仅适用 **V100F**，不是其他卡口后缀或 V480 固件。

## 本轮验证结果（2026-10-10）

- **14,649 项原生离线检查通过**：新增 UI 5,287；下拉层级 296；副灯行 171；发光 4,399；主灯 OFF／副灯独立 1,389；就绪 398；调用约定和版本准入 2,317；原生副灯弹窗 392。
- 另有 21 项镜像完整性检查、原有补丁工具 10 项单元测试、桌面调试器 26 项测试通过。
- 文件大小 **1,002,732 字节**。SHA-256：`4e986a26ecf38b362b3b3e4b78adb551572cd5e6f4e091a7b4deb34f1ab5bdc8`。
- 本轮源码、测试结果和候选摘要均绑定在验证记录中；发光与旋钮辅助代码逐字节保留 R7，完整文件逆变换与官方原件一致。
- [验证记录](evidence/VALIDATION.json) · [新 UI 检查](evidence/R8_UI_RESULTS.json) · [镜像校验](evidence/IMAGE_INTEGRITY.json)

## 真机复测

1. 从属主界面短按电源／返回键，观察副灯是否与其余界面同步退出；返回从属页后检查“副灯”、开关与功率。
2. 主控页面比较 M/S/A/B/C/D 的字号、基线和滚动显示。
3. 依次单击 M、A、B、C、D，检查页标题对应；左侧 TTL/M、右侧开关、加减、旋钮和返回键均作用于该灯。
4. 关闭某灯，在 OFF 状态切换模式后重新开启；核对列表、独立页和实际受控灯结果一致。检查操作其他组不会改变 S 或剩余灯组。
5. 检查原有机顶／从属直调、主控副灯、普通快门和无线触发。

离线测试执行完整镜像中的原生指令及 LVGL 对象。LCD 的实际观感、实体触摸／旋钮手感和设备实拍仍需复测；本轮未连接或写入设备。

## English

R8 is a local experimental UI revision based on the exact public V100F R7. It preserves the Receiver SUB footer through the normal exit animation, restores the native localized SUB label, matches S to the 29-pixel M/A–D group metrics, and adds dedicated M/A–D editors with TTL/M on the left and ON/OFF on the right. Native power/FEC buttons, encoder control, group indices, firing and RF code remain in use. SU-1 remains manual.

The build, validation and packaging commands above create a complete image only after candidate/source-bound offline regression passes. Device validation remains outstanding. R7's published reconstruction and evidence are unchanged.
