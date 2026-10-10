// V100N_V1.05 R10 fire gates. Original pulse routines remain in vendor flash.
.syntax unified
.thumb
.cpu cortex-m4
.text
.balign 4
// Each wrapper replaces a role load; the stock CMP/branch remains intact.
.global ttl_wrapper
.thumb_func
ttl_wrapper:
 push {r1,r2,r3,lr}
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x34c]
 cmp r0,#0
 beq restore_ttl
 ldr r2,[sp,#20]
 ldr r3,=0x800e3a9
 cmp r2,r3
 bne restore_ttl
 ldr r2,[sp,#36]
 bl qualify_physical_test
restore_ttl:
 pop {r1,r2,r3,lr}
 ldr pc,=0x800d1af

.balign 4
.global manual_wrapper
.thumb_func
manual_wrapper:
 push {r1,r2,r3,lr}
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x34c]
 cmp r0,#0
 beq restore_manual
 ldr r1,=0x20000000
 ldr r2,[sp,#52]
 ldr r3,=0x800e373
 cmp r2,r3
 bne restore_manual
 ldr r2,[sp,#68]
 bl qualify_physical_test
restore_manual:
 pop {r1,r2,r3,lr}
 cmp r0,#0
 bne 1f
 ldr pc,=0x80114c1
1:
 ldr pc,=0x80113e3

.balign 4
.global exposure_ttl_wrapper
.thumb_func
exposure_ttl_wrapper:
 push {r1,r2,r3,lr}
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x34c]
 cmp r0,#0
 beq exposure_ttl_restore
 ldr r1,=0x20000000
 bl qualify_exposure
exposure_ttl_restore:
 pop {r1,r2,r3,lr}
 cmp r0,#0
 cmp r0,#0
 bne 1f
 ldr pc,=0x800a3ad
1:
 ldr pc,=0x8009e3f

.balign 4
.global exposure_m_wrapper
.thumb_func
exposure_m_wrapper:
 push {r1,r2,r3,lr}
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x34c]
 cmp r0,#0
 beq exposure_m_restore
 ldr r1,=0x20000000
 bl qualify_exposure
exposure_m_restore:
 pop {r1,r2,r3,lr}
 // Displaced CMP is part of this hook; preserve its result into stock BEQ.W.
 cmp r0,#0
 cmp r0,#0
 bne 1f
 ldr pc,=0x800a9a1
1:
 ldr pc,=0x800a433

.balign 4
.global radio_wrapper
.thumb_func
radio_wrapper:
 push {r0,r1,r2,r3,r12,lr}
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x34c]
 cmp r0,#4
 bne radio_original
 ldrb.w r2,[r1,#0x50d]
 cmp r2,#10
 bne radio_original
 bl qualify_wireless
 cmp r0,#0
 bne radio_original
 // Original RX preparation has already set main duration 0x522.
 // Stock joint routine reads that unchanged and independent SUB power 0x4C0.
 ldr r3,=0x802a09d
 blx r3
 pop {r0,r1,r2,r3,r12,lr}
 ldr pc,=0x801f98d
radio_original:
 pop {r0,r1,r2,r3,r12,lr}
 ldr r0,=0x20000430
 ldrb r0,[r0]
 ldr pc,=0x801f8d3

.balign 4
.global sender_off_wrapper
.thumb_func
sender_off_wrapper:
 // This site is exclusively the reviewed normal-sync radio-only branch.
 // Original Sender packet is already sent; CPSID remains active throughout.
 push {r0,r1,r2,r3,r12,lr}
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x34c]
 cmp r0,#3
 bne sender_off_restore
 bl qualify_wireless
 cmp r0,#0
 bne sender_off_restore
 bl sub_only_full_width
sender_off_restore:
 pop {r0,r1,r2,r3,r12,lr}
 mov.w r0,#4000
 ldr pc,=0x800ad95

.balign 4
.thumb_func
sub_only_full_width:
 // Reproduce E3E8's frame and table preparation, using the same U16 table
 // width as the stock photographic joint routine 2A9D0 (TEST uses U8).
 // Continue into untouched native SUB readiness/head/ON checks and pulse.
 // Never enter any main tube firing routine or write main duration 0x522.
 push {r4,r5,r6,r7,r8,lr}
 ldr r0,=0x200004d0
 ldr r1,=0x8051dec
 ldr r5,=0x200004d2
 ldrb r0,[r0]
 movs r6,#0
 rsb.w r0,r0,#80
 ldrh.w r4,[r1,r0,lsl #1]
 ldr pc,=0x800dd7b

.balign 4
.thumb_func
qualify_exposure:
 ldrb.w r2,[r1,#0x522]
 cmp r2,#10
 beq qualify_wireless
 cmp r2,#0x8a
 beq qualify_wireless
 bx lr

.balign 4
.thumb_func
qualify_physical_test:
 ldr r3,=0x8010435
 cmp r2,r3
 bne reject
 ldrb.w r2,[r1,#0x559]
 cmp r2,#0
 bne reject
 cmp r0,#3
 beq sender
 cmp r0,#4
 bne reject
 movs r3,#2
 b page
sender:
 movs r3,#1
page:
 ldrb.w r2,[r1,#0x5af]
 cmp r2,r3
 bne reject
 ldrb.w r2,[r1,#0x3a8]
 cmp r2,r3
 bne reject
 b common
.thumb_func
qualify_wireless:
 // UI locks/pages do not inhibit photography. Actual flash mode/role does.
 cmp r0,#3
 beq common
 cmp r0,#4
 bne reject
common:
 ldrb.w r2,[r1,#0x4d3]
 tst r2,#0x10
 bne reject
 ands r2,r2,#3
 cmp r2,#1
 bhi reject
 // Do NOT prefilter SUB-ready/ON/head here. Original E3E8/2A9D0 own them.
 // In particular 2A9D0 returns without either pulse if attached SUB not ready.
 .irp off,0x4a6,0x51c
 ldrb.w r2,[r1,#\off]
 cmp r2,#1
 bne reject
 .endr
 .irp off,0x53f,0x544,0x54a
 ldrb.w r2,[r1,#\off]
 cmp r2,#0
 bne reject
 .endr
 // Stock SU-1 index = 80 - power. Only native 1/3-stop codes 0..70.
 ldrb.w r2,[r1,#0x4d0]
 cmp r2,#70
 bhi reject
mod10:
 cmp r2,#10
 blo residue
 subs r2,#10
 b mod10
residue:
 cmp r2,#0
 beq allow
 cmp r2,#3
 beq allow
 cmp r2,#7
 bne reject
allow:
 movs r0,#0
reject:
 bx lr
.balign 4
.global code_end
code_end:
.ltorg
