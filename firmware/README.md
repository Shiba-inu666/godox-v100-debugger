# 原件准备与修改版下载 / Original inputs and modified downloads

现成的 **V100F R7 / V480F v2 修改版 BIN** 请到[下载页](../docs/DOWNLOADS.md)。若要自己复现或运行离线测试，请自行准备相应官方原件，放入本目录。原厂原件不随仓库分发。

Ready-made **V100F R7 / V480F v2 modified BINs** are on the [download page](../docs/DOWNLOADS.md). To reproduce them or run offline tests, supply the corresponding official originals locally. Official originals are not distributed here.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `firmware/V100F_V1.03.bin` | 1,002,732 | `fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787` |
| `firmware/V480F_V1.03.bin` | 753,705 | `84ca232f50a62ceb2d9b24017a3b447a7154bf63f6461ef546a30a6b29077ebf` |

相同版本名不保证字节相同。工具按精确摘要拒绝未知输入，不要改名或取消校验适配其他固件。两款主应用映射均为 `0x08008000`，但包装结构和偏移不同，分别使用 [V100](../native/README.md) / [V480](../v480/README.md) 工具。

The same version label does not guarantee identical bytes. Unknown inputs are rejected; do not rename or bypass checks to use another image. Both main applications map at `0x08008000`, but packaging and offsets differ. Use the corresponding [V100](../native/README.md) or [V480](../v480/README.md) tool.

二进制不进入 Git 历史，明确核验的修改版通过 GitHub Releases 提供。原件、私人会话与本机环境仍被忽略。生成器不覆盖输入，也不连接或写设备。

Binary files stay out of Git history; verified modified images are attached to GitHub Releases. Originals, private sessions and local environments remain excluded. Generators do not overwrite input or connect to/write devices.
