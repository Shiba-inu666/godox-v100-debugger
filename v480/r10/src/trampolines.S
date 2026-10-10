.syntax unified
.cpu cortex-m4
.thumb
.text
.balign 4
.global stock_save
.thumb_func
stock_save:
 push {r4,r5,r6,lr}
 ldr r5,=0x20000338
 ldr pc,=0x80121a5
.ltorg
.balign 4
.global stock_sender
.thumb_func
stock_sender:
 push.w {r4,r5,r6,r7,r8,r9,r10,r11,lr}
 ldr pc,=0x804d1b5
.ltorg
.balign 4
.global stock_focus
.thumb_func
stock_focus:
 push {r4,r5,r6,lr}
 ldr r5,=0x20000a60
 ldr pc,=0x802d78d
.ltorg
.balign 4
.global stock_tick
.thumb_func
stock_tick:
 push.w {r4,r5,r6,r7,r8,r9,r10,r11,lr}
 ldr pc,=0x8043245
.ltorg
.balign 4
.global stock_page
.thumb_func
stock_page:
 cmp r0,#12
 it hs
 bxhs lr
 ldr pc,=0x801d3f3
.ltorg
.balign 4
.global stock_sender_event
.thumb_func
stock_sender_event:
 push.w {r4,r5,r6,r7,r8,lr}
 ldr pc,=0x801c36d
.ltorg
.balign 4
.global stock_gui
.thumb_func
stock_gui:
 push.w {r4,r5,r6,r7,r8,r9,r10,lr}
 ldr pc,=0x802a7a1
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
 bl receiver_target
 cbz r0,.Lnative_\name
 ldr r6,=0x2000053d
 strb r0,[r6]
 pop {r0-r3}
 ldr r5,=\original
 blx r5
 movs r0,#0
 strb r0,[r6]
 msr primask,r4
 pop {r4-r6,pc}
.Lnative_\name:
 msr primask,r4
 pop {r0-r6,lr}
 ldr pc,=\original
.ltorg
.endm
editor_adjust positive, 0x0808d001
editor_adjust negative, 0x0808d02d
.balign 4
.global sub_decoder
.thumb_func
sub_decoder:
 push {r0-r6,lr}
 mrs r4,primask
 cpsid i
 bl editor_target
 cbnz r0,.Ldecoder_direct
 bl receiver_target
 cbz r0,.Ldecoder_fallback
.Ldecoder_direct:
 ldr r6,=0x20000028
 ldr r5,[r6]
 pop {r0-r3}
 ldr r0,=0x0808d059
 blx r0
 str r5,[r6]
 msr primask,r4
 pop {r4-r6,pc}
.Ldecoder_fallback:
 msr primask,r4
 pop {r0-r6,lr}
 ldr pc,=0x0808d059
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
 ldr r1,=0x20000a5c
 str r0,[r1]
.Lgui_resume:
 msr primask,r4
 pop {r0-r4,lr}
 b stock_gui
.ltorg
