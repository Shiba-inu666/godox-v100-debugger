# Godox V100F 固件研究、原生补丁与调试工作台

**简体中文** | [English](README.en.md)

从“旋钮直接调节闪光参数”开始，逐步实现 V100F V1.03 的原生 SU-1 副灯界面、主控/从属普通闪光支持，并根据实机反馈修复布局、下拉面板层级和字体问题。本仓库同时保留电脑端离线调试工作台。

**最新原生版本：R7 experimental。** 这是指定固件的实验性补丁，尚未完成整机验收。仓库提供源码、补丁记录、复现工具及验证资料；原厂固件和完整修改版 BIN 由使用者在本地准备、生成，不随仓库分发。项目与 Godox 官方无隶属关系。

## 从哪里开始

- 想了解做了什么、为什么反复修改：[完整中文历程](docs/PROJECT_HISTORY.md) / [English history](docs/PROJECT_HISTORY.en.md)。
- 想在电脑上观察参数与调用：[调试工作台指南](docs/debugger/README.zh-CN.md)。
- 想复现 R7 文件：[原生补丁指南](native/README.md)、[验证报告](docs/native/VALIDATION.md)、[恢复与 Gate 状态](docs/native/RECOVERY.md)。
- 想了解副灯 TTL：[专项研究](docs/native/SU1_TTL_RESEARCH.md)。**目前未实现副灯 TTL。**

## 原生固件已经实现什么

这里的“实现”指代码已实现且有对应静态或离线执行证据；不等于每种相机、无线组合均完成实测。

| 功能 | R7 行为与范围 | 证据 / 限制 |
|---|---|---|
| 机顶、从属主界面旋钮直调 | TTL 调节主灯 FEC；M 调节主灯功率，避免旋钮焦点跑到其他控件 | 复用原厂调整函数；菜单、MODE、ZOOM、锁屏、弹窗和下拉面板保留原路径 |
| 原厂参数规则 | 保留原厂边界、步进及相关调整路径 | 主灯 TTL 调整的是曝光补偿，没有重写 TTL 测光算法 |
| Sender 原生副灯行 | 主控页面按 M → **S** → A–D 排列，原厂风格控件调整副灯开关和手动功率 | S 表示本机 SU-1，不是新增无线组；Sender 旋钮导航保持原逻辑 |
| Receiver 原生副灯入口 | 底部 MODE / ZOOM / S 三列，进入原生副灯设置弹窗 | 修复原先与 ZOOM、下拉面板重叠的问题 |
| 无线角色下 TEST 副灯 | 主控、从属 TEST 路径支持已开启的 SU-1 | TEST 与相机曝光命令语义不同，不能用 TEST 单独证明拍照链路正常 |
| 普通拍照 / 无线触发副灯 | 已覆盖的 Sender 快门和 RX 普通触发路径，主灯沿用原厂计算/无线功率，副灯使用本地 UI 功率 | 有界指令执行验证；未新增副灯 HSS、Multi 或 TTL |
| 主控主灯 OFF 时副灯独立 | 已覆盖的普通曝光路径中，M=OFF、S=ON 可进入副灯单独发光路径 | 保留原无线命令流程；不把实体 TEST 重新定义为“只测试参与曝光的灯” |
| 未就绪处理 | 复用原厂相关就绪检查，不添加等待充电、排队或延迟补闪 | 原厂已追踪路径表现为跳过不满足条件的请求；不代表所有无线灯存在统一就绪屏障 |
| UI 修复 | 原生灰色行、功率控件；弹窗布局、对象生命周期、下拉层级与命中修复 | R7 将无法显示的 SUB 标签改为原字体确实包含的单字母 S |
| 严格版本匹配 | 校验完整原件 SHA、机型、向量、原字节和唯一上下文，生成后核对完整 SHA | 只接受本文指定 V100F V1.03，不将偏移套用到其他型号 |

从属模式的本地主灯设置仍可被后续合法无线命令更新。直调不等于屏蔽无线控制，也不承诺零额外中断延迟。

## 支持的固件

| 项目 | 内容 |
|---|---|
| 机型 / 版本 | **Godox V100F V1.03** |
| 原件大小 | **1,002,732 字节** |
| 原件 SHA-256 | `fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787` |
| R7 SHA-256 | `8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761` |
| R7 变化量 | 24 个补丁区域，共 4,018 字节与原件不同；文件长度不变 |

项目早期同时研究了 V480F，发现共同框架的强证据，也发现封装差异。**本次公开 R7 工具只支持 V100F**；不提供 V480F、V100C/N/S/O 的同等功能或兼容承诺。

## 本地复现 R7

先按[固件准备说明](firmware/README.md)放入原件。补丁工具只需 Python 3.11+ 标准库，不需要编译器，也不会连接设备。

```sh
git clone https://github.com/Shiba-inu666/godox-v100-debugger.git
cd godox-v100-debugger
# 将自己的指定原件放入 firmware/V100F_V1.03.bin
python3 native/patcher.py firmware/V100F_V1.03.bin
python3 native/patcher.py firmware/V100F_V1.03.bin --output-dir native/out/r7
```

第一条补丁命令只在内存中校验。第二条在**新目录**生成：

- `V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin`
- `SHA256SUMS.txt`
- `PATCH_MANIFEST.json`

已有目录会被拒绝，输入文件不会覆盖。生成成功只说明文件精确复现，**不表示已经验证设备刷写、恢复或拍摄效果**。使用前阅读[当前未完成的硬件验证](docs/native/RECOVERY.md)。

## 电脑端调试工作台

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python debug/server.py --open
```

浏览器打开 `http://127.0.0.1:8765/`，可探索 Wi-Off、Sender、Receiver、TTL、M、Multi、菜单、内存变化、调用记录和会话回放。它执行选定原厂参数函数，UI 由电脑适配；**浏览器界面不是 R7 固件屏幕的完整仿真**，不具备真实闪光、充电或无线接口。

详细操作：[中文](docs/debugger/README.zh-CN.md) / [English](docs/debugger/README.en.md)。

## 验证状态

2026-10-09 公开包验证：

| 验证层级 | 结果 | 解释 |
|---|---|---|
| 补丁工具单元测试 | 10 / 10 通过 | 输入拒绝、补丁范围、完整 SHA、逆变换与不覆盖 |
| 电脑端工作台测试 | 26 / 26 通过 | 参数、模式、会话及 HTTP 行为 |
| 可移植原生验证子集 | 9,399 项通过 | 字形、层级、发光分支、就绪、ABI、弹窗等有界检查 |
| 副灯 TTL 研究 | 90 项观测完成 | 证明当前路径差异，**不是 TTL 功能通过** |
| 三段补丁源码重编译 | 与 R7 字节完全相同 | LLVM / Clang 20.1.8 |
| 既有完整工程记录 | 39,851 项离线检查 | 历史存档，包含未移植到公开 runner 的旋钮/事件/ISR 测试 |
| 完整实机验收 | **未完成** | 真实光能、快门/RF 时序、热行为、失败恢复仍待验证 |

这些数字是不同验证集合，彼此有重叠，不应相加为硬件测试总量。[详细方法、记录与限制](docs/native/VALIDATION.md)。

## 目录

```text
debug/               电脑端工作台
tests/               工作台测试
native/src/          R7 的 C / Thumb 汇编与链接脚本
native/patches/      R4 / R5 对照与 R7 精确补丁记录
native/lab/          可移植的原厂指令执行验证
native/evidence/     已脱离个人路径的验证结果
native/patcher.py    本地生成 / 文件级逆变换
native/build.py      源码重编译并核对 R7 字节
docs/                中英文历程、架构、验证、恢复与 TTL 研究
firmware/            用户自行提供的固件；不提交到 Git
```

反馈时请附机型、原件/候选 SHA、无线角色、模式、是否 HSS、主灯/副灯开关，以及使用 TEST 还是相机快门。不要仅写“最新版本”：相同 UI 不代表相同发光路径。
