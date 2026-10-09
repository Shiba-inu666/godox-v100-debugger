# 文档索引 / Documentation

[中文首页](../README.md) · [English home](../README.en.md) · [目录结构 / Layout](../DIRECTORY_LAYOUT.md)

## 使用与下载 / Use and downloads

| 内容 / Topic | 入口 / Document |
|---|---|
| 支持型号、版本、功能 / Supported devices and scope | [型号目录 / Device index](devices/README.md) |
| 现成 BIN、SHA-256、发布清单 / BINs, hashes and manifests | [Downloads](DOWNLOADS.md) |
| 作者已刷入反馈、待验收事项 / Deployment reports and outstanding acceptance | [Hardware status](HARDWARE_STATUS.md) |
| 文件恢复与设备恢复的区别、Gate 6–9 / Recovery and gates | [Recovery](native/RECOVERY.md) |

## 开发与复现 / Development and reproduction

| 内容 / Topic | 入口 / Document |
|---|---|
| 原件准备、两款工具命令、测试 / Inputs, both patchers and tests | [Reproduce](REPRODUCE.md) |
| V100F R7 原生源码与精确补丁 / Native source and exact patch | [V100 source guide](../native/README.md) |
| V480F v2 原生源码与精确补丁 / Native source and exact patch | [V480 source guide](../v480/README.md) |
| 电脑端参数工作台 / Desktop parameter workbench | [中文](debugger/README.zh-CN.md) · [English](debugger/README.en.md) |
| 反馈与贡献 / Reporting and contributing | [Contributing](../CONTRIBUTING.md) |

## 研究与证据 / Research and evidence

| 内容 / Topic | 入口 / Document |
|---|---|
| 固件容器、ARM 架构、原生补丁组成 / Formats, ISA and patch architecture | [Native architecture](native/ARCHITECTURE.md) |
| 工作台架构 / Desktop architecture | [Debugger architecture](ARCHITECTURE.md) |
| V100 验证方法、结果和边界 / V100 validation scope | [Validation](native/VALIDATION.md) · [Evidence](../native/evidence/) |
| V480 单型号验证与旧记录 / V480-only checks and historical records | [V480 guide](../v480/README.md) · [Evidence](../v480/evidence/) |
| 副灯 TTL 可行性，尚未实现 / SU-1 TTL feasibility, not implemented | [TTL research](native/SU1_TTL_RESEARCH.md) |
| 参考项目及借鉴范围 / External projects and their relevance | [References](REFERENCES.md) |

## 历程与版本 / History and revisions

- [完整中文历程](PROJECT_HISTORY.md) / [Full English history](PROJECT_HISTORY.en.md)
- [简明更新记录 / Changelog](../CHANGELOG.md)
- [首次 R7 源码发布 / Initial R7 source release](releases/R7.md)
- [V100F + V480F 双型号发布 / Two-model release](releases/V100_V480.md)

公开源码中的“实现”和离线通过记录，与作者实机反馈分别列出。旧证据文件保留当时状态；当前设备反馈以 `HARDWARE_STATUS.md` 为准。

Implementation and offline checks are recorded separately from device feedback. Historical evidence retains its original status; `HARDWARE_STATUS.md` holds the current deployment report.
