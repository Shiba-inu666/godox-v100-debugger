# Godox V100F Firmware Research, Native Patches and Debugger

[简体中文](README.md) | **English**

This project started with direct rotary adjustment and grew into native SU-1 controls for V100F V1.03, experimental Sender/Receiver firing support, and successive fixes informed by device feedback. It also includes the original desktop debugging workbench.

**Latest native revision: R7 experimental.** End-to-end hardware acceptance is incomplete. The repository contains source, patch records, reproduction tools and evidence. Users supply the exact official firmware and generate complete candidate BIN files locally; neither full vendor images nor full patched images are distributed here. This is an independent project, unaffiliated with Godox.

## Start here

- [Detailed project history](docs/PROJECT_HISTORY.en.md) / [中文历程](docs/PROJECT_HISTORY.md): what changed and why.
- [Desktop debugger guide](docs/debugger/README.en.md): inspect parameters and calls on a computer.
- [Native reproduction guide](native/README.md), [validation](docs/native/VALIDATION.md), [recovery and gates](docs/native/RECOVERY.md).
- [SU-1 TTL research](docs/native/SU1_TTL_RESEARCH.md): **SU-1 TTL is not implemented.**

## What the native patch implements

“Implemented” means present in code with static or bounded execution evidence. It does not mean every camera/radio combination has passed physical testing.

| Feature | R7 behavior | Evidence / boundary |
|---|---|---|
| Direct main-screen rotary adjustment | Wi-Off and RX: adjust main-flash FEC in TTL or power in M without moving focus to unrelated widgets | Reuses factory adjustment routines; menus, MODE, ZOOM, locks, modals and drawers retain their original paths |
| Factory parameter rules | Preserve existing limits, steps and associated adjustment paths | Main TTL adjustment is FEC; the metering algorithm is not rewritten |
| Native Sender SU-1 row | M → **S** → A–D, with native-style enable and manual-power controls | S is the local SU-1, not an extra radio group; Sender rotary navigation retains stock behavior |
| Native Receiver SU-1 entry | MODE / ZOOM / S bottom row and factory-style SUB modal | Separates SUB from ZOOM and fixes drawer overlap |
| Wireless-role TEST support | Enabled SU-1 can participate in the covered Sender/RX TEST paths | TEST and exposure commands have different semantics |
| Normal shutter / radio firing | Covered Sender shutter and RX normal-fire paths retain factory main-power calculation or received power; SUB uses its local UI setting | Bounded execution evidence; no added SU-1 HSS, Multi or TTL |
| Sender main OFF, SUB ON | A SUB-only branch for the covered normal-exposure path | Preserves the original radio-command flow; does not redefine the physical TEST button |
| Not-ready behavior | Reuse relevant stock readiness decisions, without adding charge waits, queued shots or delayed replay | Observed stock paths skip requests that fail their gates; no claim of a network-wide ready barrier |
| UI repairs | Native row styling, modal geometry, object lifetime, drawer stacking and hit testing | R7 uses a single S found in the actual native fonts instead of missing SUB glyphs |
| Exact-version patching | Check full input SHA, model, vectors, expected bytes and unique contexts; verify complete output SHA | Only the exact V100F V1.03 sample below is supported |

Later valid radio commands can still update RX main-flash settings. Direct adjustment does not lock out radio control, and zero additional interrupt latency has not been established.

## Supported image

| Item | Value |
|---|---|
| Model / version | **Godox V100F V1.03** |
| Original size | **1,002,732 bytes** |
| Original SHA-256 | `fe92fbacce29e2ec22784371900f73bbe3e5052c49cc7e66845c276ab5fc7787` |
| R7 SHA-256 | `8c07a4f6672ffa575081d2aa11df29c50487f978aa6155321c95a19cb032c761` |
| R7 difference | 24 patch regions; 4,018 changed bytes; unchanged total length |

Early work also examined V480F and found strong shared-framework evidence as well as packaging differences. **This public R7 tool supports V100F only.** It does not offer equivalent V480F features or compatibility with V100C/N/S/O.

## Reproduce R7 locally

Follow the [firmware preparation notes](firmware/README.md). The patcher requires Python 3.11+ and the standard library; no compiler or device connection is needed.

```sh
git clone https://github.com/Shiba-inu666/godox-v100-debugger.git
cd godox-v100-debugger
# Place your matching original at firmware/V100F_V1.03.bin
python3 native/patcher.py firmware/V100F_V1.03.bin
python3 native/patcher.py firmware/V100F_V1.03.bin --output-dir native/out/r7
```

The first patcher invocation verifies in memory only. The second creates a **new directory** containing:

- `V100F_V1.03_SINGLE_S_LABEL_R7_EXPERIMENTAL.bin`
- `SHA256SUMS.txt`
- `PATCH_MANIFEST.json`

Existing output directories are rejected. The input is not overwritten. Successful generation confirms exact file reproduction; it does **not** establish device flashing, recovery or photographic performance. Read the [outstanding hardware validation](docs/native/RECOVERY.md).

## Desktop workbench

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python debug/server.py --open
```

Open `http://127.0.0.1:8765/` to explore Wi-Off, Sender, Receiver, TTL, M, Multi, menus, memory changes, call traces and session replay. Selected original parameter routines execute under emulation; desktop adapters provide the interface. **The browser is not a complete simulation of the R7 device screen**, charging, real radio or light emission.

[English operating guide](docs/debugger/README.en.md) / [中文操作指南](docs/debugger/README.zh-CN.md).

## Validation status

Publication checks on 2026-10-09:

| Layer | Result | Meaning |
|---|---|---|
| Patcher unit tests | 10 / 10 passed | Input rejection, patch ranges, complete hashes, inverse transformation and no overwrite |
| Desktop tests | 26 / 26 passed | Parameters, roles, sessions and HTTP behavior |
| Portable native subset | 9,399 checks passed | Glyphs, stacking, firing branches, readiness, ABI and modal checks |
| SU-1 TTL investigation | 90 observations completed | Existing-path differences, **not a TTL feature pass** |
| Three native source modules | Exact match to recorded R7 bytes | LLVM / Clang 20.1.8 |
| Archived engineering run | 39,851 offline checks | Includes rotary/event/ISR checks not ported into the public runner |
| Complete hardware acceptance | **Incomplete** | Optical energy, shutter/RF timing, thermal behavior and failed-update recovery remain open |

These sets overlap and must not be added together as a hardware-test total. See [methods, evidence and limitations](docs/native/VALIDATION.md).

## Repository layout

```text
debug/               Desktop workbench
tests/               Desktop tests
native/src/          R7 C / Thumb assembly and linker script
native/patches/      R4 / R5 comparison records and exact R7 patch
native/lab/          Portable execution lab for original instructions
native/evidence/     Validation records without personal paths
native/patcher.py    Local generation / file-level inverse transformation
native/build.py      Recompile source and compare with recorded R7 bytes
docs/                Bilingual history, architecture, validation, recovery, TTL
firmware/            Locally supplied firmware; excluded from Git
```

For an issue, include model, input/candidate SHA, radio role, mode, HSS state, main/SUB enable states, and whether you used TEST or the camera shutter. “Latest version” alone cannot identify the executing firing path.
