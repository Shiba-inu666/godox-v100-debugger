# 本地固件

此仓库不分发 Godox 原厂固件。运行前，请自行准备与你有权使用的 V100F V1.03 对应的原始二进制，放在：

```
firmware/V100F_V1.03.bin
```

只接受下列精确样本：

- 文件大小：1,002,732 字节
- SHA-256：`fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787`
- 模拟加载地址：`0x08008000`

版本名称相同不代表二进制内容相同。地址和布局只针对上述样本；校验不匹配时程序会停止。不要绕过校验或把其他版本文件改名后使用。

此目录中的二进制被 Git 忽略，固件只在本机模拟器中读取。仓库不提供固件下载、设备刷写或真实闪光接口。

## English

Vendor firmware is not distributed with this repository. Supply a copy you are entitled to use at `firmware/V100F_V1.03.bin`.

The supported sample is exactly **1,002,732 bytes**, with SHA-256 `fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787`. It is loaded at simulated address `0x08008000`.

The same version label does not guarantee identical binary contents. All mapped addresses target this exact sample, and the program stops on a hash mismatch. Do not bypass the check or rename another version to match the expected filename.

Binary files in this directory are ignored by Git and read only by the local emulator. The repository provides no firmware download, device flashing or hardware flash-firing interface.
