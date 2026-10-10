# 反馈与贡献 / Contributing

[首页 / Home](README.md) · [复现 / Reproduce](docs/REPRODUCE.md) · [型号目录 / Devices](docs/devices/README.md)

## 报告问题 / Report an issue

使用 [Bug 表单](https://github.com/Shiba-inu666/godox-firmware-mods/issues/new?template=bug_report.yml)，尽量提供以下信息：

- 完整型号后缀、BIN 文件名和 SHA-256；只说"最新版本"无法定位问题。
- 当前角色（Wi-Off / Sender / Receiver）、闪光模式（TTL / M）、HSS 状态，以及主灯与副灯的开关和功率。
- 触发方式：实体 TEST、相机快门还是无线触发；附上相机/引闪器型号和可重复的操作步骤。
- 预期结果和实际结果，是否影响照片曝光；UI 问题可附去除私人信息后的照片。

Use the [bug form](https://github.com/Shiba-inu666/godox-firmware-mods/issues/new?template=bug_report.yml). Include the exact model suffix, BIN filename/hash, role, flash mode, HSS and main/SUB settings. Distinguish physical TEST, camera shutter and radio triggering. Describe the camera/transmitter, reproduction steps, expected/actual behavior and effect on the photograph. A redacted photo helps with UI issues. “Latest version” alone is insufficient.

## 修改代码 / Change code

1. 每个型号使用自己的原件身份、补丁清单和原字节断言。不要把 V100 偏移套给 V480，也不要扩大未知版本匹配。
2. 说明影响的页面和触发路径，复用已有参数规则。未改动的模式要有对应回落证据。
3. 按[复现指南](docs/REPRODUCE.md)运行与改动相关的验证；提供具体命令、结果和生成文件 SHA。新固件行为需要新修订身份。
4. 静态分析、离线执行、用户反馈和实机测量分开记录。保留历史结果，不把旧结果改成新功能的通过证明。
5. 修改文档时运行 `python3 scripts/check_repository.py`。源码或补丁改变后，重新产生对应证据，不只改摘要让检查通过。

Each model owns its input identity, patch record and expected-byte checks. Describe affected pages and firing/input routes, preserve factory rules and demonstrate fallback outside scope. Run relevant checks from the reproduction guide and record commands, results and output SHA. New firmware behavior needs a new revision identity. Separate static findings, offline execution, user reports and physical measurements; retain historical evidence. For docs, run the repository checker. Source changes require regenerated evidence, not merely edited hashes.

## 提交内容 / Submission contents

Git 中提交源码、文档和脱离个人路径的证据。官方原件、设备序列号、私人会话与编译缓存留在本地。修改版 BIN 通过带摘要和清单的 Release 发布，源代码 PR 无需塞入二进制文件。

Commit source, documentation and portable evidence. Keep official inputs, device serial numbers, private sessions and build caches local. Modified BINs belong in Releases with hashes and manifests, rather than source PRs.
