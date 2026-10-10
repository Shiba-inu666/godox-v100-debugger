.syntax unified
.cpu cortex-m4
.thumb
.text
.balign 4
.global stock_sender
.thumb_func
stock_sender:
 push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x804c539
.ltorg
.balign 4
.global stock_rx
.thumb_func
stock_rx:
 push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x804ca65
.ltorg
.balign 4
.global stock_focus
.thumb_func
stock_focus:
 push {r4, r5, r6, lr}
 ldr r5,=0x20000a34
 ldr pc,=0x802cac1
.ltorg
.balign 4
.global stock_close
.thumb_func
stock_close:
 push {r4, r5, lr}
 ldr r4,=0x200014f4
 ldr pc,=0x801dc61
.ltorg
.balign 4
.global stock_activity
.thumb_func
stock_activity:
 mov r3, r1
 cmp r0, #1
 ldr pc,=0x8051891
.ltorg
.balign 4
.global stock_tick
.thumb_func
stock_tick:
 push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x80425e5
.ltorg
.balign 4
.global stock_page
.thumb_func
stock_page:
 cmp r0, #0xc
 it hs
 bxhs lr
 ldr pc,=0x801cea3
.ltorg
.balign 4
.global stock_sender_event
.thumb_func
stock_sender_event:
 push.w {r4, r5, r6, r7, r8, lr}
 ldr pc,=0x801bf8d
.ltorg
.balign 4
.global stock_rx_event
.thumb_func
stock_rx_event:
 push.w {r4, r5, r6, r7, r8, lr}
 ldr pc,=0x801c489
.ltorg
.balign 4
.global stock_rx_mode
.thumb_func
stock_rx_mode:
 push {r4, r5, lr}
 ldr r5,=0x20000511
 ldr pc,=0x80166c9
.ltorg
.balign 4
.global stock_format
.thumb_func
stock_format:
 push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x8011691
.ltorg
.balign 4
.global stock_sender_fields
.thumb_func
stock_sender_fields:
 push.w {r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,lr}
 sub sp,#12
 mov r4,r1
 mov r5,r3
 mov r6,r2
 // Factory tail removes field[4] from the temporary default focus group.
 // Use the live row there; sub_focus rebuilds the final native focus list.
 str r0,[r4,#16]
 ldr pc,=0x8014e43
.ltorg

.macro editor_adjust name, original
.balign 4
.global sub_\name
.thumb_func
sub_\name:
 push {r0-r6,lr}
 mrs r4,primask
 cpsid i
 bl editor_target
 cbz r0,.Lfallback_\name
 bl editor_allowed
 cbz r0,.Lblocked_\name
 bl editor_select
 pop {r0-r3}
 ldr r5,=\original
 blx r5
 msr primask,r4
 pop {r4-r6,pc}
.Lblocked_\name:
 msr primask,r4
 pop {r0-r6,pc}
.Lfallback_\name:
 msr primask,r4
 pop {r0-r6,lr}
 ldr pc,=\original
.ltorg
.endm
editor_adjust positive, 0x80bdd01
editor_adjust negative, 0x80bdd3d
.balign 4
.global sub_decoder
.thumb_func
sub_decoder:
 push {r0-r6,lr}
 mrs r4,primask
 cpsid i
 bl editor_target
 cbz r0,.Ldecoder_fallback
 ldr r6,=0x20000028
 ldr r5,[r6]
 pop {r0-r3}
 ldr r0,=0x80bdd79
 blx r0
 str r5,[r6]
 msr primask,r4
 pop {r4-r6,pc}
.Ldecoder_fallback:
 msr primask,r4
 pop {r0-r6,lr}
 ldr pc,=0x80bdd79
.ltorg
.balign 4
.global sub_gui
.thumb_func
sub_gui:
 push {r0-r4,lr}
 mrs r4,primask
 cpsid i
 bl editor_target
 cbz r0,.Lgui_resume
 ldr r1,=0x20000028
 movs r0,#0
 str r0,[r1]
 ldr r1,=0x20000a30
 str r0,[r1]
.Lgui_resume:
 msr primask,r4
 pop {r0-r4,lr}
 ldr pc,=0x80bdda5
.ltorg
