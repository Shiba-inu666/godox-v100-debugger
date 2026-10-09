# Project history: from direct rotary control to R7

[简体中文](PROJECT_HISTORY.md) · [Home](../README.en.md)

This account covers the engineering state through 2026-10-09. Stages follow dependency and revision order; dates are not invented for early steps without independent timestamps. Requirements, implemented code, offline evidence, device feedback and unresolved work are kept distinct.

## 1. The original request: eliminate one SET operation

On the ordinary on-camera main screen, the dial should directly adjust TTL flash exposure compensation or manual power, instead of selecting a widget, pressing SET and then turning again. TTL meant FEC, with the original ±3 EV range and one-third-stop steps, not a replacement metering algorithm.

Menus, MODE, ZOOM, radio groups, locks, touch and SET had to retain their behavior. The engineering objective was therefore to find the factory adjustment routines used after entering edit mode and change when they were called, rather than globally remap the encoder or recreate power arithmetic.

Both V100F and V480F were initially examined. Originals and identities were preserved before format, architecture and state-machine work. Later development concentrated on V100F; this history does not turn that into a claim of full support for both models.

## 2. Establish what the files contain

Both samples expose little-endian ARM M-profile / Thumb-2 applications and vector tables mapped at `0x08008000`. Cortex-M4 / GD32F4xx is strongly suggested; the exact silicon remains an inference rather than a board identification.

V100F is 1,002,732 bytes and V480F is 753,705 bytes. An identical 19,692-byte auxiliary payload and similar startup/UI structures support a shared framework. However, V480 has an MD5 payload digest, filename, length and fixed trailer marker that are not present in the same form in V100. Shared code does not make packaging, offsets or integrity handling interchangeable.

Localized compressed initialization data was identified, not whole-image compression or encryption. The auxiliary payload has its own vectors and peripheral-transfer evidence; it is not established as a recovery bootloader for a damaged main application. V100 device-side integrity and signature coverage remain unresolved.

These findings prevented assumptions based on other Godox models or on the mere presence of a second executable. See [native architecture](native/ARCHITECTURE.md).

## 3. Build an observable desktop workbench

A browser workbench shortened the feedback loop. Unicorn executes selected original parameter routines while desktop adapters supply screens, inputs, memory inspection, call logs and session replay.

Coverage grew to Wi-Off, Sender, Receiver, TTL/M/Multi, menus, group filtering and settings records. Twenty-six automated tests cover limits, session compatibility and HTTP persistence. The workbench makes parameters and calls observable; it does not model real capacitors, flash tubes, RF hardware or the complete RTOS.

Native firmware still required separate work on actual widget callbacks, memory and interrupt constraints. The repository originally published only the desktop layer. This release adds the native work without conflating the two.

## 4. Native direct adjustment with a restricted scope

The native patch calls existing adjustment routines under page, mode and UI-state guards. A later requirement extended direct main-parameter control to Receiver so the dial would not wander onto other controls on either on-camera or receiver main screens.

The final `fixed_main` helper occupies approximately 508 bytes. Non-target screens retain their original routes, as does Sender group navigation. Subsequent valid radio commands may still update RX main-flash parameters; local direct adjustment is not a radio lockout.

RX event ordering and interrupt interactions received separate attention. Bounded ISR observations can test ordering in covered cases, but cannot prove unchanged physical latency. The reports explicitly retain this limitation instead of treating offline counts as oscilloscope or camera measurements.

## 5. SU-1 controls: displaying a widget is not firing a flash

The next requirement extended the factory on-camera SU-1 controls into Sender and Receiver. A local SUB row was added to Sender, with an entry and native modal on Receiver.

Device feedback exposed independent failures: controls overlapped ZOOM, and a visible, editable SUB did not necessarily fire. Subsequent feedback confirmed the original on-camera SUB and TEST could work; wireless-role restrictions were the remaining focus. R2 reorganized the RX layout; R3 extended the relevant TEST path.

The lesson was concrete: **working UI, successful TEST firing and successful camera exposure are three separate acceptance conditions.** Removing a UI role gate does not automatically change shutter or receive-interrupt behavior.

## 6. R4: normal shutter/RX firing and readiness behavior

A later report confirmed that SUB fired on TEST but not during photography, while wireless RX triggers fired only the main head. Work moved to the actual exposure entry points.

For the established normal-exposure branches, R4 reused the original dual-light mechanism. Main power comes from the stock calculation or received radio command; SUB power comes from its local UI. SUB neither copies main power nor becomes an extra radio group.

Stock on-camera TEST, normal exposure and related radio paths were also traced for readiness. Covered requests that failed their gates were skipped; no ready-wait loop that deferred the shot until charging completed was found. The patch does not introduce waiting or queued replay: a flash after the exposure window does not replace the missed exposure.

Sending a radio command and allowing local emission are separate stages. A network-wide barrier waiting for every receiver was not established. This is a path-bounded finding, not a universal protocol guarantee.

R4 also restored the SUB modal's original on-camera geometry. HSS, Multi and metering preflash were not expanded into new SUB features as a side effect.

## 7. R5: independent SUB with Sender main OFF

The next device issue was that setting Sender M=OFF also stopped SUB. An earlier “OFF still fires” report had been clarified as physical TEST behavior. The new issue concerned the exposure path suppressing both local lights, so the two reports required different treatment.

R5 added a SUB-only branch to the established normal Sender exposure route. The original radio transmission remains, main stays OFF, and enabled SUB uses local power when the relevant readiness conditions permit it. It does not globally disable OFF or fire the main head secretly.

The SUB row was also brought closer to native gray group-row styling. Offline testing exposed object/heap pressure when old and new screens coexist during transitions. Unneeded slider/bar objects were removed, and ownership checks reclaim old SUB objects at established lifecycle transitions. A single screenshot would not reveal these problems.

## 8. R6: from visual overlap to stacking and touch ownership

With the Receiver shortcut drawer open, SUB still appeared above the brightness slider. This was not simply a coordinate error: the stock drawer was created first, then the extra SUB was appended under the same root, putting it above the drawer.

R6 uses native object ordering to place SUB before the current drawer. Focus guards prevent the attachment from taking input back when it reappears. Verification exercises actual hit testing, including the formerly conflicting `(380, 320)` point, which must belong to brightness rather than SUB.

This revision adds 296 stacking/hit-test checks. It changes layering and input ownership while preserving the R5 firing module.

## 9. R7: replacing three missing glyphs with one S

A device photograph showed three empty boxes for the Sender SUB label. Earlier string and rectangle checks passed, but they did not establish that the selected font contained S, U and B.

Inspection found no such glyphs in the numeric subset; another group-label font also lacked a usable S. R7 selects actual native fonts containing S: a 19×24 glyph for Sender and a 9×11 glyph for Receiver, with the label consistently reduced to **S**.

Thirty-seven additional checks verify glyph presence, nonempty bitmaps and layout. R7 keeps the R6/R5 firing code unchanged. A filename or label containing “TTL” cannot create that capability; the candidate's identity is its SHA-256.

## 10. SU-1 TTL: research progress, no feature enablement

The next research question was whether the main TTL logic could simply be reused. Bounded observations show separate main preflash/metering-result and manual SUB-duration paths. Changing the metering input changes main output while a fixed SUB UI setting still produces a fixed duration.

Copying main TTL output would at most provide linked open-loop output. Genuine SUB TTL would require SUB preflash participation, energy calibration, correct handling of the metering result and main exposure, and validation of readiness and dual-light allocation. Independent metering channels for both lights have not been established.

The release preserves 90 research observations without injecting an unvalidated TTL path. See [SU-1 TTL research](native/SU1_TTL_RESEARCH.md).

## 11. Preparing a reproducible public release

On 2026-10-09, the experiments were organized into a portable package:

1. Preserve the desktop workbench and move its original guides to a dedicated folder.
2. Extract R7 C, assembly and linker inputs; rebuild all three helpers and match the recorded R7 bytes exactly.
3. Provide an exact-image patcher, complete-output verification and file-level inverse transformation, without overwriting originals.
4. Remove runtime dependencies on personal absolute paths; reconstruct R4/R5 comparison images in memory from the user's original.
5. Rerun the portable subset: 9,399 functional checks and 90 TTL observations, plus 10 patcher and 26 desktop tests.
6. Archive the 39,851-check engineering record, clearly separating unported runners and offline evidence from physical testing.
7. Publish bilingual history, feature tables, source, reports and recovery limits. That first source-only publication omitted complete BINs; the later two-model download release is recorded in section 13. Official originals, sessions and private photographs remain excluded.

## 12. Present result and next work

The result is an **auditable, reproducible experimental R7 for one exact input image**: main-screen direct rotary control, native wireless-role SUB controls, covered normal firing paths, Sender SUB-only operation with main OFF, and successive UI repairs.

Physical validation remains necessary for light energy, camera exposure, RF timing, recycling, thermal behavior and sustained stability. A reliable recovery route is not established. Authorization to generate an experimental file does not resolve these engineering gaps; the [gate and recovery record](native/RECOVERY.md) preserves that distinction. New TTL or model support requires its own evidence and tests.


## 13. Two-model publication: Godox Firmware Mods and ready-made BINs

On 2026-10-09 the maintainer requested the V480 project and both ready-made BIN downloads, and confirmed modified firmware flashed onto both devices. The repository was renamed **Godox Firmware Mods**, currently covering only V100F and V480F.

The V480 publication is the previously delivered **rotary-direct v2**: Wi-Off direct FEC/manual-power control with stock 0.1/0.3 steps and acceleration. Other screens, including Sender/Receiver, retain stock paths. It does not inherit V100's later RX direct adjustment or SU-1 extensions. Source, an independent patcher, V480 MD5 handling and evidence are included.

The 316-byte V480 helper was rebuilt byte-for-byte. V480-only public reruns passed 12,489 functional checks, 746 ordinary communication interrupt injections, 1,386 whole-image executions and 10 patcher tests. Earlier dual-model totals of 24,978 / 1,491 remain historical evidence, not V480-only counts.

V100 retains its R7 SHA and V480 its existing v2 SHA. This publication packages established firmware rather than adding new firing behavior. The maintainer's two-device flashing report is recorded independently; without installed hashes, it is not expanded into complete physical acceptance of every download revision.

[Both BINs and feature matrix](DOWNLOADS.md) · [V480 project](../v480/README.md) · [Hardware status](HARDWARE_STATUS.md)

## 14. Project naming and documentation structure

Following the maintainer's naming correction, the final name is **Godox Firmware Mods**. Public organization in Hasselblad, Ricoh and FujiHack projects informed a shorter feature/download landing page, model index, documentation map, shared reproduction guide, changelog and issue templates. [References](REFERENCES.md) record the specific inspiration.

V100's `native/` and V480's `v480/` build paths remain stable. Documentation work does not replace source-to-byte evidence. Repository/release names, links and the release manifest were aligned; both BINs and their SHA-256 values remain identical.
