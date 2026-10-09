# 本地固件 / Local firmware

本仓库不分发 Godox 完整原厂或修改版固件。请自行准备有权使用的指定原件，放入：

```text
firmware/V100F_V1.03.bin
```

| 项目 / Item | 值 / Value |
|---|---|
| Model / version | V100F V1.03 |
| Size | 1,002,732 bytes |
| SHA-256 | `fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787` |
| Main application mapping | `0x08008000` |

相同版本名不保证内容相同。工具按精确摘要拒绝未知输入，不要通过改名或取消校验适配其他文件。

电脑工作台读取原件用于离线执行；原生补丁工具读取原件并在新目录生成实验文件。两者均不覆盖输入，也不连接或刷写设备。固件、输出 BIN 和会话均不提交到 Git。

[原生工具说明](../native/README.md) · [恢复限制](../docs/native/RECOVERY.md)

## English

Supply your own authorized copy of the exact original at the path above. A version label is not a binary identity; mismatched input is rejected. Do not bypass checks or rename another model/version to make it appear compatible.

The desktop debugger reads the original for offline execution. The native patcher reads it and creates an experimental candidate in a new output directory. Neither overwrites the input or connects to/writes a device. Complete original/candidate firmware files and user sessions are excluded from Git.
