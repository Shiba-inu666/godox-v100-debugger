# 固件下载与功能对照 / Firmware downloads

[项目首页 / Home](../README.md) · [Release](https://github.com/Shiba-inu666/godox-flash-lab/releases/tag/v100-v480-2026-10-09)

目前仅提供 **V100F 与 V480F，均基于 V1.03**。作者报告两台均已刷入修改固件；[具体证据范围](HARDWARE_STATUS.md)。

Currently **V100F and V480F only, both based on V1.03**. The maintainer reports both devices flashed; see [evidence scope](HARDWARE_STATUS.md).

| 设备 / Device | BIN 下载 / Download | 大小 / Size | 实现功能 / Changes |
|---|---|---:|---|
| V100F | [V100F V1.03 R7](https://github.com/Shiba-inu666/godox-flash-lab/releases/download/v100-v480-2026-10-09/V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin) | 1,002,732 bytes | 机顶/从属主灯直调、SU-1 主控/从属 UI 和普通闪光路径、主灯 OFF 时副灯独立、界面修复 / Wi-Off/RX direct main adjustment, Sender/RX manual SU-1 controls/firing, SUB-only with main OFF, UI fixes |
| V480F | [V480F V1.03 rotary-direct v2](https://github.com/Shiba-inu666/godox-flash-lab/releases/download/v100-v480-2026-10-09/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin) | 753,705 bytes | 仅 Wi-Off 主界面 TTL FEC / M 功率直调，保留 0.1/0.3 步进、原厂加速与其他页面 / Wi-Off direct FEC/manual power, original steps, acceleration and excluded pages |

- [SHA256SUMS.txt](https://github.com/Shiba-inu666/godox-flash-lab/releases/download/v100-v480-2026-10-09/SHA256SUMS.txt)
- [RELEASE_MANIFEST.json](https://github.com/Shiba-inu666/godox-flash-lab/releases/download/v100-v480-2026-10-09/RELEASE_MANIFEST.json)
- [V100 补丁清单 / V100 patch manifest](https://github.com/Shiba-inu666/godox-flash-lab/releases/download/v100-v480-2026-10-09/V100F_R7_PATCH_MANIFEST.json)
- [V480 补丁清单 / V480 patch manifest](https://github.com/Shiba-inu666/godox-flash-lab/releases/download/v100-v480-2026-10-09/V480F_V2_PATCH_MANIFEST.json)

## SHA-256

```text
8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761  V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin
58dedf69cb23805a8cb72b9b44a4d6dafb2b7997081a7404e2a53f471ba20fb4  Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin
```

两款文件不能混用，其他 C/N/S/O 后缀未在此发布中适配。下载文件保留既有实验版本名称和原字节，不因仓库更名而重新修改 firmware。**V100 副灯 TTL 未实现；V480 本版没有 RX 直调、SU-1 或新增 UI。**

Do not interchange the files. Other C/N/S/O suffixes are not adapted in this release. Existing experimental filenames and bytes are retained; renaming the repository does not create new firmware behavior. **V100 SUB TTL is not implemented; V480 v2 has no RX direct adjustment, SU-1 extension or new UI.**

## 文件来源 / Provenance

每个 BIN 都由对应严格版本补丁工具从固定官方原件重建，再与此前交付文件的完整 SHA 比较。发布的是修改版 BIN，不附原厂固件备份；源码、补丁清单和本地复现方式同时保留。

Each BIN is reproduced from its pinned official input with its own exact-version patcher, then compared against the previously delivered full-image SHA. Modified BINs are published; official backup images are not bundled. Source, patch manifests and local reproduction remain available.

[V100 工具 / tool](../native/README.md) · [V480 工具 / tool](../v480/README.md) · [恢复与 Gate / recovery and gates](native/RECOVERY.md)
