> This guide describes only the desktop debugger, not the native firmware patch.

# V100F 固件调试工作台 · v3

**简体中文** | [English](README.en.md)

这是一个在电脑浏览器里运行的离线观察工具。它在本地通过 Unicorn 执行 V100F V1.03 原厂固件的部分参数函数，让你在没有真机的情况下操作 Wi-Off（机顶模式）、Sender（主控模式）、Receiver（从属模式），以及 TTL、M、Multi 和常用菜单设置，同时观察参数变化、内存状态和原厂函数的调用记录。页面布局与旋钮、按键输入由电脑端适配。

**Offline multi-mode firmware debugger for Godox V100F.** Explore Wi-Off, Sender, Receiver, TTL, manual flash and Multi modes in a browser, with original firmware parameter routines, memory inspection and session replay. The interface runs locally; users supply the matching firmware file.

它不是完整的设备模拟器，也不是可以刷进闪光灯的成品固件。工具不连接真机、不发光、不进行无线通信，也不执行刷机。原厂固件文件需要你自己按 [固件准备说明](../../firmware/README.md) 放到本地；仓库不附带原厂固件，也不保存你的调试会话。

This is an independent debugging tool. It does not operate flash hardware, communicate over radio or flash firmware to a device.

## 首次安装

需要 Python 3.11 或更高版本；本项目已在 macOS / Python 3.14 验证。

1. 克隆仓库：

   ```sh
   git clone https://github.com/Shiba-inu666/godox-firmware-mods.git
   cd godox-firmware-mods
   ```

2. 按 [固件准备说明](../../firmware/README.md) 在本地放入指定的 `V100F_V1.03.bin`。仓库不包含原厂固件，也不包含用户调试会话。

3. 创建环境并启动（macOS / Linux）：

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python debug/server.py --open
   ```

   Windows 可以把命令里的 `.venv/bin/python` 换成 `.venv\Scripts\python.exe` 来执行安装与启动；Windows 运行尚未单独验证。

## 打开与操作

双击 [启动调试.command](../../启动调试.command)，或运行上面的启动命令，浏览器打开 <http://127.0.0.1:8765/>。

- 顶部先选角色 Wi-Off / Sender / Receiver，再选闪光模式。
- 点屏幕上的行进入编辑，或用旋钮选中后按 SET；编辑时旋转旋钮加减，SET / BACK 返回。
- Wi-Off 的 SUB 只保留主区域一个入口。Receiver 左上角选接收组，左下角切换 TTL / M / Multi，右下角调 ZOOM。
- MENU 打开屏幕内设置菜单，可以用旋钮选择，也可以直接点选。
- 键盘方向键旋转，Enter=SET，Escape=BACK；鼠标在圆形旋钮上滚动也能调节。
- 页面下方实时显示状态、内存变化、原厂函数调用，并支持会话导出与回放。

服务只监听本机地址；关闭启动窗口或按 Ctrl+C 停止。多个标签页共用同一会话，其他页面需要刷新才能看到变更。刷新会保留状态；重启后点“恢复会话”读取已保存的内容。

## 能调试什么

| 页面 / 功能 | 已接入内容 |
|---|---|
| Wi-Off · TTL | 本机曝光补偿，原厂显示与 ±3 EV 边界 |
| Wi-Off · M | 本机手动功率、ZOOM、SUB 开关与功率 |
| Sender · Group | M → SUB → A → B → C → D，五个原厂目标的 TTL / M / OFF、ZOOM、整体调整 |
| Receiver · TTL / M | A–E 组选择，独立功率槽与 ZOOM；TTL 显示由远端控制，不新增本地补偿 |
| Multi · 三种角色 | 功率 1/256–1/4 整档、次数 1–100、频率 1–100 Hz、ZOOM；Receiver 保留 A–E 组 |
| Receiver 接收调试 | 选择接收组与目标组，模拟下发模式、M / Multi 功率、次数或频率；原厂参数解析器处理地址匹配 |
| MENU | 功率显示、步进、S1/S2 光控、TCM、距离单位、待机、自动关机及时间、造型灯行为、屏幕亮度/待机、ZOOM 格式、设备语言设置、设备信息 |
| 模拟条件 | SU-1 连接、输入锁、信道 1–32、步进与显示格式 |
| 固件输出 | Sender 无线差异编码、79 字节设置记录；输出仅捕获到模拟内存 |
| 调试工具 | 撤销 / 重做、保存 / 恢复、导出 / 导入、单步 / 全部回放、内存筛选、调用轨迹 |

Receiver 的“模拟远端下发”调用的是原厂**参数解析函数**，没有运行完整的射频中断和传输链路。菜单里一部分设置执行原厂回调，其余直接修改已确认的模拟 RAM 字段；亮度、休眠、自动关机和设备语言只记录设置值，不改变电脑或真实设备的行为。

## 建议验收路线

1. Wi-Off → TTL → 主灯 → 提高一次，检查 +0.3 EV；切到 M 检查手动功率调节。
2. 切到 Multi，依次调整功率、闪光次数和频率，观察调用记录与字段变化。
3. Receiver → M → 接收组 C。模拟向 A 组下发功率，确认被忽略；向 C 组下发相同参数，确认已更新。
4. MENU → 光控引闪 → S2 → BACK，检查菜单显示和内存状态。
5. 切回 Sender，编辑 SUB / A–D，检查独立参数和整体调整。
6. 导出记录，再导入后单步或全部回放，核对角色、模式、组参数和菜单值。

## 会话与兼容性

- “保存会话”写入 `sessions/saved-session.json`；“恢复会话”按动作列表重新执行。
- v3 导出的 schema 为 3；v2 的 schema 2 会话和 v3 会话都能导入，导入时必须匹配固件 SHA-256。导入失败会保持当前状态。v1 的纯状态文件不支持回放。
- 本地 `sessions/` 目录下的记录不会提交到 Git。
- 会话最多 1000 步；调用面板显示最近 80 步；导出文件包含完整动作和最近 300 条日志。
- 重置只清空当前活动会话，不删除已保存的文件。撤销后再执行新操作，才会清空重做分支。

## 实现范围

这是一套由原厂参数函数驱动的离线调试工具。角色和模式切换、页面布局、MENU 导航、GUI 对象与生命周期都由电脑端适配；它不是完整的 MCU / LCD / RTOS 仿真，输出也不能刷进设备。

真实无线收发、闪光、充电、过热保护、扫描配对、实际休眠关机，以及 MCU GUI 补丁注入，都没有实现。界面里的初始值是测试场景，不代表出厂默认值。原厂固件副本本身没有被修改，工具也没有连接设备或刷写固件的接口。调试器的部分交互与后来的原生补丁不同，固件操作请以[对应版本说明](../DOWNLOADS.md)为准。

## 验证

运行检查：

```sh
.venv/bin/python -m unittest discover -s tests -v
```

当前 **26 项测试通过**，覆盖三种角色、Wi-Off FEC / M、Receiver A–E 隔离与地址过滤、TTL 只读、Multi 边界、菜单、旧会话兼容、跨模式回放，以及原 Sender 操作和 HTTP 保存恢复。浏览器里已验证 Wi-Off TTL、Multi 次数、Receiver 匹配 / 不匹配下发、S2 设置、多模式布局，以及 19 步跨模式导入回放；本轮浏览器控制台没有 error / warn。

- [自动测试源码](../../tests/)
- [实现结构与固件映射](../ARCHITECTURE.md)
- [Multi 界面预览](../../debug-preview-v3.jpg)

Receiver 布局：左上角接收组，左下角模式，右下角 ZOOM。

![Receiver 调试界面](../../receiver-layout-fixed.jpg)

Wi-Off 只保留一个 SUB 入口：

![Wi-Off 调试界面](../../wioff-layout-fixed.jpg)

原始固件 SHA-256：`fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787`。
