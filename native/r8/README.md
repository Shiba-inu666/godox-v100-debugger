# V100F V1.03 · R8 独立灯组控制

R8 是本地实验版，基于 GitHub 发布 `v100-v480-2026-10-09` 中的 V100F R7。发布资产已下载核对，R7 的 SHA-256 为 `8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761`。当时 GitHub 主分支基线为 `d445b7f342ef12c9ac7878c06beb9dbbed5e6b56`。

## 本轮四项修改

1. 在从属页按实体返回或电源键进入原厂选择页时，副灯入口随旧屏幕一起退出，而不是提前单独消失。共享控件句柄先解绑，旧对象等原厂屏幕动画结束后再释放。
2. 从属页副灯入口的命名与机顶一致：中文“副灯”，英文“SUB”，字库、位置和颜色都沿用原厂。
3. 主控 S 的字形高度与 M/A–D 统一为 **29 像素**，文字框、基线和纵向位置对齐。原厂组名字库不含 S，所以用 R7 内嵌的 S 点阵生成同高度的 4 位抗锯齿字形，没有直接拿缺字字库来显示 S。
4. 在主控列表单击 **M、A、B、C、D** 任一行的灯名或数字，就打开该灯的独立页；列表上的加减按钮仍可直接调整。独立页左下是 TTL/M，右下是 ON/OFF；加减、旋钮照旧调功率或 TTL 曝光补偿，按右上返回后焦点回到该灯。灯在 OFF 时可以先选模式而不启用灯组，下次开启时恢复所选模式。

S 仍然是本机 SU-1 的手动副灯。新的 TTL/M 按钮只作用于 M/A–D；SU-1 TTL 没有实现。

## 实现范围

- 原厂的组模式、启用数组、无线掩码和 M 功率/TTL 补偿仍按原来的索引存储；S 不放进无线组数组。
- 独立页通过原厂组加减回调改参数，显示格式和步进沿用原厂。新弹层对象存在原厂 LVGL 对象的用户数据里，随父屏幕一起释放，不新增固定的全局 RAM 地址。
- 发光、保护、无线协议和旋钮辅助代码与 R7 相同，只改了 UI 辅助段和 UI 钩子。
- 从机顶或从属直接切到主控页面时，仍要先回收旧的副灯子树：五组原生主控控件和完整旧页同时存在会耗尽固定 GUI 堆。这保留了 R7 的直接切换内存处理；正常走返回或选择页退出时，副灯显示完整保留。
- 独立页的数值刷新带状态缓存，数值没变的周期不重复分配文字、不重绘标签。

## 构建、验证、生成

在仓库根目录执行。输入原件必须与公开 R7 工具要求的官方 V100F V1.03 SHA 一致。需要 LLVM/Clang 20 和 `native/requirements.txt` 里的 Python 依赖。

```sh
.venv/bin/python native/r8/build.py
.venv/bin/python native/r8/validate.py
.venv/bin/python native/r8/package.py native/r8/out/r8
```

可以用 `GODOX_LLVM_BIN`、`GODOX_LD_LLD` 指定本机 LLVM 工具。构建时加 `--github-base /path/to/R7.bin`，会要求下载文件与本地重建的 R7 逐字节一致。

生成器只接受通过本轮完整验证、且源码、候选镜像和各测试结果摘要都没有变化的版本。输出目录必须不存在，以免覆盖旧文件；写入后会重新读取核对。验证内容包括新界面专项，以及原有的下拉层级、原生副灯行、发光、就绪、调用约定和副灯弹窗回归。R7 的公开源码、补丁记录和既有验证摘要保持原样。

生成的 `V100F_V1.03_GROUP_CONTROL_R8_EXPERIMENTAL.bin` 是完整长度的实验镜像，附带 `SHA256SUMS.txt`、`PATCH_MANIFEST.json`、`VALIDATION.json`。它只适用于 **V100F**，不能用于其他卡口后缀或 V480。

## 本轮验证结果（2026-10-10）

- **14,649 项原生离线检查通过**：新增 UI 5,287；下拉层级 296；副灯行 171；发光 4,399；主灯 OFF／副灯独立 1,389；就绪 398；调用约定和版本准入 2,317；原生副灯弹窗 392。
- 另有 21 项镜像完整性检查、原补丁工具 10 项单元测试和桌面调试器 26 项测试通过。
- 文件大小 **1,002,732 字节**。SHA-256：`4e986a26ecf38b362b3b3e4b78adb551572cd5e6f4e091a7b4deb34f1ab5bdc8`。
- 本轮源码、测试结果和候选摘要都绑定在验证记录里；发光与旋钮辅助代码逐字节保留 R7，完整文件逆变换后与官方原件一致。
- [验证记录](evidence/VALIDATION.json) · [新 UI 检查](evidence/R8_UI_RESULTS.json) · [镜像校验](evidence/IMAGE_INTEGRITY.json)

## 真机复测

1. 在从属主界面短按电源或返回键，看副灯是否与其余界面同步退出；回到从属页后检查“副灯”、开关和功率。
2. 在主控页面比较 M/S/A/B/C/D 的字号、基线和滚动显示。
3. 依次单击 M、A、B、C、D，确认页标题对应；左侧 TTL/M、右侧开关、加减、旋钮和返回键都只作用于该灯。
4. 关掉某盏灯，在 OFF 状态切换模式后重新开启；核对列表、独立页和实际受控的灯一致。确认操作其他组不会改变 S 或剩余灯组。
5. 检查原有机顶／从属直调、主控副灯、普通快门和无线触发。

离线测试执行的是完整镜像里的原生指令和 LVGL 对象。LCD 的实际观感、实体触摸和旋钮手感、设备实拍仍需上机复测；本轮没有连接或写入设备。

## English

R8 is a local experimental UI revision based on the exact public V100F R7. It preserves the Receiver SUB footer through the normal exit animation, restores the native localized SUB label, matches S to the 29-pixel M/A–D group metrics, and adds dedicated M/A–D editors with TTL/M on the left and ON/OFF on the right. Native power/FEC buttons, encoder control, group indices, firing and RF code remain in use. SU-1 remains manual.

The build, validation and packaging commands above create a complete image only after candidate/source-bound offline regression passes. Device validation remains outstanding. R7's published reconstruction and evidence are unchanged.
