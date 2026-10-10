# Godox Firmware Mods

[简体中文](README.md) | **English**

Firmware research and practical improvements for Godox flashes. **The project currently covers two models: V100 and V480, specifically V100F / V480F V1.03.** It started with direct rotary adjustment and grew to include V100 SU-1 extensions, native UI repairs, offline debugging and reproducible patch tools.

**The maintainer reports having flashed project-modified firmware onto both their V100F and V480F** (2026-10-09). Their feature sets differ. Deployment feedback and complete acceptance coverage are recorded separately in [hardware status](docs/HARDWARE_STATUS.md). This project is independent of Godox.

## BIN downloads

| Device | Download version | File | Main changes |
|---|---|---|---|
| **V100F V1.03** | R10 experimental | [Download V100F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-r10-2026-10-10/v1.03r10.bin) | R9 controls and native gestures, plus native colored group badges and Sender S-row power dragging |
| **V480F V1.03** | Rotary-direct v2 | [Download V480F BIN](https://github.com/Shiba-inu666/godox-firmware-mods/releases/download/v100-v480-2026-10-09/Godox_V480F_V1.03_rotary-direct_CANARY_v2.bin) | Wi-Off main-screen TTL FEC / manual-power adjustment, retaining factory step and acceleration paths |

[Release and checksum files](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-v480-2026-10-09) · [Download matrix and SHA-256](docs/DOWNLOADS.md)

Match the exact model suffix. Both are experimental modified images, not official firmware; other camera suffixes are not supported. **SU-1 TTL remains unimplemented on V100; V480 v2 does not include V100's SU-1 extensions or RX direct adjustment.**

**V100F R10 (2026-10-10):** [Release](https://github.com/Shiba-inu666/godox-firmware-mods/releases/tag/v100-r10-2026-10-10) · [Controls, source and native previews](native/r10/README.md). The simplified filename is `v1.03r10.bin`, for V100F V1.03 only. 13,966 native functional checks and 37 image checks passed; hardware acceptance remains pending. The earlier deployment report does not validate R10. The table below records the R7/V480 baseline.

## Implemented features by model

| Feature | V100F R7 | V480F v2 |
|---|---|---|
| Wi-Off direct TTL FEC adjustment | Implemented with factory ±3 EV / one-third-stop rules | Implemented with factory ±3 EV / one-third-stop rules |
| Wi-Off direct manual-power adjustment | Implemented with factory rules | Implemented; retains 0.1 / 0.3 step selection and acceleration |
| Receiver main direct adjustment | Implemented; later radio commands still apply | Not added; stock operation |
| Native Sender/RX SUB controls and normal firing | Implemented; local manual SUB setting | Not added |
| Sender main OFF with SUB-only normal exposure | Implemented for the covered path | Not added |
| SUB overlap, drawer and missing-glyph repairs | Implemented; single S label | Not part of this patch |
| Menus, MODE, ZOOM, locks and other excluded screens | Original fallback | Original fallback |
| Maintainer reports firmware flashed | Yes | Yes |

## Emulator preview

The project also includes a **browser-based V100F offline emulator (debugging workbench)** for exploring Wi-Off, Sender and Receiver modes, parameter changes, memory and call records. Its desktop-adapted interface is not a complete emulation of the device screen. [Setup and usage](docs/debugger/README.en.md).

![V100F offline emulator: Wi-Off Multi screen](debug-preview-v3.jpg)

![V100F offline emulator: Receiver mode and receive debugging](receiver-layout-fixed.jpg)

## Documentation and source

| Goal | Entry point |
|---|---|
| Model scope, version and known limits | [V100F R7](docs/devices/V100F.md) · [V480F v2](docs/devices/V480F.md) |
| Development story and individual fixes | [Full English history](docs/PROJECT_HISTORY.en.md) · [Changelog](CHANGELOG.md) |
| Deployment reports and acceptance coverage | [Hardware status](docs/HARDWARE_STATUS.md) |
| Reproduce, reverse or verify the files | [Reproduction guide](docs/REPRODUCE.md) |
| Read the implementation | [V100 C / assembly](native/src/) · [V480 assembly](v480/src/) · [Directory layout](DIRECTORY_LAYOUT.md) |
| Firmware formats, tests and SU-1 TTL research | [Documentation index](docs/README.md) |
| Explore parameters and calls on a computer | [Desktop workbench](docs/debugger/README.en.md) |
| Report an issue or contribute | [Contributing](CONTRIBUTING.md) · [New issue](https://github.com/Shiba-inu666/godox-firmware-mods/issues/new/choose) |

## Progress

Work began with both firmware formats and ARM input chains, followed by direct rotary adjustment. V100 then gained wireless-role SUB controls, separate TEST and exposure-path work, main-OFF SUB support, stacking repairs and a verified native glyph. V480 retains its independent on-camera rotary scope. The bilingual history preserves the failures, revisions and supporting evidence.

The public source reproduces the recorded bytes. Portable V100 results contain 9,399 functional checks and 90 separate TTL observations; V480-only results contain 12,489 functional checks, 746 interrupt injections and 1,386 whole-image checks. **These are computer-side checks; full hardware acceptance and failed-update recovery remain incomplete.** [Validation](docs/native/VALIDATION.md) · [Recovery and gates](docs/native/RECOVERY.md)

The name **Godox Firmware Mods** directly describes the project. Documentation organization draws on Hasselblad, Ricoh and FujiHack firmware projects; [references](docs/REFERENCES.md) explain what was borrowed as an organizational idea.
