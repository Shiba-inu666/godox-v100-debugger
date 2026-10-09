.syntax unified
.cpu cortex-m4
.thumb
.text
.balign 4
.global stock_sender
.thumb_func
stock_sender:
 push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x804c761
.ltorg
.balign 4
.global stock_rx
.thumb_func
stock_rx:
 push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x804cc8d
.ltorg
.balign 4
.global stock_focus
.thumb_func
stock_focus:
 push {r4, r5, r6, lr}
 ldr r5,=0x200009e8
 ldr pc,=0x802cc25
.ltorg
.balign 4
.global stock_close
.thumb_func
stock_close:
 push {r4, r5, lr}
 ldr r4,=0x200014a8
 ldr pc,=0x801dd25
.ltorg
.balign 4
.global stock_activity
.thumb_func
stock_activity:
 mov r3, r1
 cmp r0, #1
 ldr pc,=0x8051aa5
.ltorg
.balign 4
.global stock_tick
.thumb_func
stock_tick:
 push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x80426c1
.ltorg
.balign 4
.global stock_page
.thumb_func
stock_page:
 cmp r0, #0xc
 it hs
 bxhs lr
 ldr pc,=0x801d00f
.ltorg
.balign 4
.global stock_sender_event
.thumb_func
stock_sender_event:
 push.w {r4, r5, r6, r7, r8, lr}
 ldr pc,=0x801c0f9
.ltorg
.balign 4
.global stock_rx_event
.thumb_func
stock_rx_event:
 push.w {r4, r5, r6, r7, r8, lr}
 ldr pc,=0x801c5f5
.ltorg
.balign 4
.global stock_rx_mode
.thumb_func
stock_rx_mode:
 push {r4, r5, lr}
 ldr r5,=0x200004c3
 ldr pc,=0x80175ed
.ltorg
.balign 4
.global stock_format
.thumb_func
stock_format:
 push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}
 ldr pc,=0x80124a1
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
 ldr pc,=0x08015d4b
.ltorg
