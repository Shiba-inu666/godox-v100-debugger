# V100F 固件调试工作台 · v3

**简体中文** | [English](README.en.md)

在电脑上调试 **Wi-Off（机顶）、Sender（发射）、Receiver（接收）**，以及 TTL、M、Multi 和常用菜单设置。参数调节执行 V100F V1.03 的原始 Thumb 机器码；页面与输入由电脑适配。

**Offline multi-mode firmware debugger for Godox V100F.** Explore Wi-Off, Sender, Receiver, TTL, manual flash and Multi modes in a browser, with original firmware parameter routines, memory inspection and session replay. The interface runs locally; users supply the matching firmware file.

原厂固件由用户自行在本地提供。本项目是独立调试工具，不提供真实闪光、无线通信或刷机功能。

This is an independent debugging tool. It does not operate flash hardware, communicate over radio or flash firmware to a device.

## 首次安装

需要 Python 3.11 或更高版本；本项目已在 macOS / Python 3.14 验证。

1. 克隆仓库：

   ```sh
   git clone https://github.com/Shiba-inu666/godox-v100-debugger.git
   cd godox-v100-debugger
   ```

2. 按 [固件准备说明](firmware/README.md) 在本地放入指定的 `V100F_V1.03.bin`。**仓库不包含原厂固件**，也不包含用户调试会话。

3. 创建环境并启动（macOS / Linux）：

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python debug/server.py --open
   ```

   Windows 可使用 `.venv\Scripts\python.exe` 执行上述安装与启动命令；Windows 运行尚未单独验证。

## 打开与操作

双击 [启动调试.command](启动调试.command)，打开 <http://127.0.0.1:8765/>。

- 顶部选择 Wi-Off / Sender / Receiver，再选择闪光模式。
- 触摸屏幕行进入编辑，或者旋钮选择后按 SET。编辑时旋转加减；SET / BACK 返回。
- Wi-Off 的 SUB 只保留主区域一个入口。Receiver 左上角选接收组，左下角切换 TTL / M / Multi，右下角调 ZOOM。
- MENU 打开屏幕内设置菜单，可旋钮选择或直接点选。
- 键盘方向键旋转，Enter=SET，Escape=BACK；鼠标在圆形旋钮上滚动也能调节。
- 页面下方有实时状态、内存变化、原厂函数调用、会话导出与回放。

服务只监听本机；关闭启动窗口或 Ctrl+C 停止。多个页面共用同一会话，其他页面需刷新查看变更。刷新保留状态；重启后点“恢复会话”读取已保存内容。

## 可调试内容

| 页面 / 功能 | 已接入内容 |
|---|---|
| Wi-Off · TTL | 本机曝光补偿，原厂显示与 ±3 EV 边界 |
| Wi-Off · M | 本机手动功率、ZOOM、SUB 开关与功率 |
| Sender · Group | M → SUB → A → B → C → D，五个原厂目标 TTL / M / OFF、ZOOM、整体调整 |
| Receiver · TTL / M | A–E 组选择，独立功率槽与 ZOOM；TTL 显示由远端控制，不新增本地补偿 |
| Multi · 三种角色 | 功率 1/256–1/4 整档、次数 1–100、频率 1–100 Hz、ZOOM；Receiver 保留 A–E 组 |
| Receiver 接收调试 | 选择接收组与目标组，模拟下发模式、M / Multi 功率、次数或频率；原厂参数解析器处理地址匹配 |
| MENU | 功率显示、步进、S1/S2 光控、TCM、距离单位、待机、自动关机及时间、造型灯行为、屏幕亮度/待机、ZOOM 格式、设备语言设置、设备信息 |
| 模拟条件 | SU-1 连接、输入锁、信道 1–32、步进与显示格式 |
| 固件输出 | Sender 无线差异编码、79 字节设置记录；输出仅捕获到模拟内存 |
| 调试工具 | 撤销 / 重做、保存 / 恢复、导出 / 导入、单步 / 全部回放、内存筛选、调用轨迹 |

Receiver 的“模拟远端下发”调用原厂**参数解析函数**，没有运行完整射频中断和传输链路。菜单的一部分设置执行原厂回调，其余直接修改已确认的模拟 RAM 字段；亮度、休眠、关机和设备语言仅记录设置，不改变电脑或真实设备行为。

## 建议验收路线

1. Wi-Off → TTL → 主灯 → 提高一次，检查 +0.3 EV；切 M 检查手动功率调节。
2. 切 Multi，依次调整功率、闪光次数和频率，观察调用与字段变化。
3. Receiver → M → 接收组 C。模拟向 A 组下发功率，确认被忽略；向 C 组下发相同参数，确认更新。
4. MENU → 光控引闪 → S2 → BACK，检查菜单显示和内存状态。
5. 切回 Sender，编辑 SUB / A–D，检查独立参数和整体调整。
6. 导出记录，导入后单步或全部回放，核对角色、模式、组参数和菜单值。

## 会话与兼容性

- “保存会话”写入 `sessions/saved-session.json`；“恢复会话”按动作列表重新执行。
- v3 导出 schema 3；支持原 v2 schema 2 会话与 v3 会话，必须匹配固件 SHA-256。错误导入保持当前状态。v1 纯状态文件不支持回放。
- 本地 `sessions/` 中的记录不会提交到 Git。
- 会话最多 1000 步，调用面板显示最近 80 步；导出含完整动作与最近 300 条日志。
- 重置只清空活动会话，不删除已保存文件。改变撤销后的历史会清空重做分支。

## 实现范围

这是一套**原厂参数函数驱动的离线调试工具**。角色和模式切换、页面布局、MENU 导航、GUI 对象与生命周期由电脑适配，并非完整 MCU / LCD / RTOS 仿真，也不是可刷入设备的成品固件。

真实无线收发、闪光、充电、热保护、扫描配对、实际休眠关机以及 MCU GUI 补丁注入尚未实现。初始值是测试场景，不代表出厂默认值。原固件副本未修改，没有设备连接或刷机端点。

## 验证

运行检查：

```sh
.venv/bin/python -m unittest discover -s tests -v
```

当前 **26 项测试通过**，覆盖三种角色、Wi-Off FEC / M、Receiver A–E 隔离与地址过滤、TTL 只读、Multi 边界、菜单、旧会话兼容、跨模式回放，以及原 Sender 操作和 HTTP 保存恢复。浏览器已验证 Wi-Off TTL、Multi 次数、Receiver 匹配/不匹配下发、S2 设置、多模式布局及 19 步跨模式导入回放；本轮浏览器控制台无 error / warn。

- [自动测试源码](tests/)
- [实现结构与固件映射](docs/ARCHITECTURE.md)
- [Multi 界面预览](debug-preview-v3.jpg)

Receiver 布局：左上角接收组，左下角模式，右下角 ZOOM。

![Receiver 调试界面](receiver-layout-fixed.jpg)

Wi-Off 只保留一个 SUB 入口：

![Wi-Off 调试界面](wioff-layout-fixed.jpg)

原始固件 SHA-256：`fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787`。
