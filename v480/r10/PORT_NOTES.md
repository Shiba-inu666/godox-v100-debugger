# V480F port evidence and address map

The implementation is derived from the behavior of `native/r10/src/native_sub.c`, not its V100 flash/RAM addresses. Original-image SHA verification is mandatory before compiling or patching. Intermediate disassembly matching only suggested candidates; final checks execute the V480 code and LVGL against the complete candidate.

| V480 address | Verified role |
| --- | --- |
| `0x0804d1b0` | Native Sender screen constructor |
| `0x0802d788` | Native focus-list reconstruction |
| `0x08043240` | Native main UI update; custom editor refresh runs after it |
| `0x0801d3ec` | Native screen transition |
| `0x0801c368` | Native Sender key/back handler |
| `0x08010850`, `0x0800b9f0` | Native positive/negative parameter entries |
| `0x0800b4f0` | GPIO rotary decoder; GPIO B bits 0/1 |
| `0x0802a79c` | Encoder GUI read callback; SET GPIO C bit 5 |
| `0x0808d000` | Preserved published v2 rotary helper |
| `0x0808d200` | New group UI module in erased flash |
| `0x2000051c` | Five group mode bytes |
| `0x20000528`, `0x20000547` | Five M power / TTL FEC bytes |
| `0x2000055c`, `0x20000436` | Group enables / bit mask |
| `0x2000050c`, `0x2000053d` | Current group / native parameter selector |
| `0x20000664` | Sender screen root |
| `0x20000668` | Receiver screen root (page 2, role 4) |
| `0x20000543`, `0x2000055b` | Receiver TTL FEC / current Receiver group (1–5) |
| `0x200018e0`, `0x20001bb4` | Native Receiver group / ZOOM chooser roots |
| `0x20001860`–`0x2000186c` | Receiver value, numerator, sign and fraction labels |
| `0x0801f47e` | R10a: page-2 conditional branch routes to native numeric TTL formatting at `0x0801f496` |
| `0x080121a0` | R10b: native main-loop settings save service, wrapped to request a changed confirmed RX group commit |
| `0x0800b748`, `0x08019f48` | Native 80-byte serializer / rotating flash record writer |
| `0x08015570`, `0x0802fb7c` | Native boot record scan / deserializer |
| `0x08015874` | R10b: remove role-dependent group reset; retain native 1–5 validation |
| `0x20000ff5` | RX group byte in the last committed native record RAM mirror (record offset 9) |
| `0x2000033b` | Native pending-save flag; consumed in the main loop |
| `0x20001630`, `0x20001644`, `0x200016a4` | Row, title and slider arrays; slider stride 28 bytes |
| `0x20000770` | Initialized native RGB565 palette; group entries 10–13 |
| `0x2004d034` | V480 native 64 KiB LVGL/TLSF pool |

LCD configuration at `0x0803f808` sets 320×240. The 43-pixel numeric font is `0x08061cec`; native fractional labels are at `0x0805c8fc`, `0x0805cf4c`, and `0x0808c044`. Native TTL sign symbols use `0x080652d8`; the return glyph U+E692 exists in `0x0806c04c`.

Receiver badges are constructed at `0x08044de4`: 44×44, radius 5, centered font `0x080625f0`. R10a places that same appearance at `(12, 2)` in each A–D Sender editor. The tests compare all 5,808 RGB bytes of each badge crop with the original Receiver badge, in TTL, M and OFF editor states.

R10a Receiver direct adjustment uses the original parameter selectors 6 (TTL) and 2 (M). M dispatches to `power[receiver_group]`, not `power[0]`. The selector is restored to zero inside the same PRIMASK critical section. Nonzero explicit selections, native choosers, locks, busy flags and mismatched current/pending pages fall back to the original path. Decoder suppression preserves GUI delta already pending before the current sample.

The original Receiver TTL formatter renders a fixed word and the main tick does not track FEC changes. R10a redirects only its page-2 branch through the existing number/sign formatter, then caches FEC in the value label's user_data for refresh after the native tick. Page and role bytes are never spoofed. The real-UART interrupt test injects a valid camera packet at every adjustment instruction boundary: that packet changes mode and requests the hotshoe page, so adjustment must finish before IRQ delivery or skip after that page request.

The prototype initially refreshed only when the native list refresh function ran. Disassembly of the actual main update showed per-group power labels are also updated directly. The final implementation wraps the main update instead, and the encoder regression checks visible value strings after that actual update entry.

R10b reuses the existing 80-byte configuration record: offset 9 is the RX group and offset 70 is the group palette/radio index. The original touch group callback updates RAM without requesting a save, and the original boot validator resets the group to A whenever the saved role is not Receiver. The save-service wrapper compares the valid current group with the committed mirror and sets the original pending-save flag once the native chooser / group selector has closed. The original comparer, 25-record rotation, erase, word programming, debounce for other settings and shutdown flush remain. No private RAM variable, new flash region or record-format migration is introduced. Factory reset still selects A. The boot patch removes only the role-dependent reset and keeps all group range checks and radio/palette synchronization.

Persistence tests run native ARM serialization, comparison, flash word stores, record rotation, boot scanning and deserialization. They transfer only the nonvolatile flash window into a fresh VM at each cold boot. MCU flash-size registers, flash write-one-to-clear status and erase effects are modeled. Valid A–E are exercised through physical touch samples and native SET/encoder selection; all 256 saved group-byte values retain the native bounds check. Repeated unchanged selections do not add writes. A selection becomes durable after the next native save-service pass completes; loss of power during native erase/programming is not proven atomic. Physical retention, brownout behavior and flash timing require device testing.

Other test substitutions are limited to physical touch samples, GPIO values, LCD transfer, and selected wake/beep services. Actual LVGL layout, hit-testing, long-press timers, scrolling, allocation, formatting and input consumption execute as ARM instructions. Preview VMs alone use a single framebuffer. These are offline execution results, not physical-device acceptance.
