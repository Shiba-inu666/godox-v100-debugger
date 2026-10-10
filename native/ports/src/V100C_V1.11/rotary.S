.syntax unified
.cpu cortex-m4
.thumb
.text
// Called with interrupts masked. No new persistent RAM state.
.macro adjust name
.balign 4
.global \name\()_wrapper
.thumb_func
\name\()_wrapper:
 push {r0-r6,lr}
 mrs r4,primask
 cpsid i
 bl .Lscreen_guard
 cbz r0,\name\()_fallback
 // A blocked adjustment must NOT fall through to the selected ZOOM/SUB field.
 mov r6,r0
 bl .Ladjust_allowed
 cbz r0,\name\()_blocked
 ldr r5,=0x20000533
 ldrb r0,[r5]
 strb r6,[r5]
 mov r6,r0
 pop {r0-r3}
 bl .Loriginal_\name
 strb r6,[r5]
 msr primask,r4
 pop {r4-r6,pc}
\name\()_blocked:
 msr primask,r4
 pop {r0-r6,pc}
\name\()_fallback:
 msr primask,r4
 pop {r0-r6,lr}
 b .Loriginal_\name
.endm
adjust positive
adjust negative
.balign 4
.global decoder_wrapper
.thumb_func
decoder_wrapper:
 push {r0-r6,lr}
 mrs r4,primask
 cpsid i
 bl .Lscreen_guard
 cbz r0,decoder_fallback
 ldr r6,=0x20000028
 ldr r5,[r6]
 pop {r0-r3}
 bl .Loriginal_decoder
 str r5,[r6]
 msr primask,r4
 pop {r4-r6,pc}
decoder_fallback:
 msr primask,r4
 pop {r0-r6,lr}
 b .Loriginal_decoder
.balign 4
.global gui_wrapper
.thumb_func
gui_wrapper:
 push {r0-r4,lr}
 mrs r4,primask
 cpsid i
 bl .Lscreen_guard
 cbz r0,gui_resume
 // Discard both old hardware navigation delta and the GUI residual delta.
 // The original callback still samples and reports SET, untouched.
 ldr r1,=0x20000028
 movs r0,#0
 str r0,[r1]
 ldr r1,=0x20000a30
 strh r0,[r1]
gui_resume:
 msr primask,r4
 pop {r0-r4,lr}
 b .Loriginal_gui
.balign 4
.global screen_guard
.thumb_func
screen_guard:
.Lscreen_guard:
 ldr r1,=0x20000000
 ldrb.w r0,[r1,#0x5eb]
 ldrb.w r2,[r1,#0x3eb]
 cmp r0,r2
 bne denied
 cmp r0,#0
 beq hotshoe
 cmp r0,#2
 bne denied
 ldrb.w r2,[r1,#0x38c]
 cmp r2,#4
 bne denied
 ldr.w r2,[r1,#0x650]
 cmp r2,#0
 beq denied
 ldr r3,=0x200018b4
 ldr r2,[r3]
 cmp r2,#0
 bne denied
 ldrb.w r2,[r1,#0x553]
 cmp r2,#4
 bhi denied
 b common
hotshoe:
 ldrb.w r2,[r1,#0x38c]
 cmp r2,#0
 bne denied
 ldr.w r2,[r1,#0x624]
 cmp r2,#0
 beq denied
common:
 ldr r3,=0x20001bf8
 ldr r2,[r3]
 cmp r2,#0
 bne denied
 ldr r3,=0x200015b8
 ldr r2,[r3]
 cmp r2,#0
 bne denied
 ldrb.w r2,[r1,#0x794]
 cmp r2,#0
 bne denied
 ldrb.w r2,[r1,#0x796]
 cmp r2,#0
 bne denied
 ldrb.w r2,[r1,#0x797]
 cmp r2,#0
 bne denied
 // Only selectors proven in main callbacks 0801A29C / 0801C18C.
 ldrb.w r2,[r1,#0x533]
 cmp r2,#24
 bhi denied
 ldr r3,=0x01014047 // bits 0,1,2,6,14,16,24
 movs r0,#1
 lsls r0,r0,r2
 tst r0,r3
 beq denied
 ldrb.w r0,[r1,#0x511]
 ands r0,r0,#3
 cbz r0,ttl
 cmp r0,#1
 bne denied
 movs r0,#2
 bx lr
ttl:
 movs r0,#6
 bx lr
denied:
 movs r0,#0
 bx lr
.balign 4
.global adjust_allowed
.thumb_func
adjust_allowed:
.Ladjust_allowed:
 ldr r1,=0x20000000
 adr r3,adjust_guards
adjust_loop:
 ldrh r2,[r3],#2
 cbz r2,adjust_flags
 ldrb r2,[r1,r2]
 cmp r2,#0
 bne blocked
 b adjust_loop
adjust_flags:
 ldrb r2,[r1,#0x31]
 tst r2,#8
 bne blocked
 ldrb r2,[r1,#0x36]
 tst r2,#2
 bne blocked
 movs r0,#1
 bx lr
blocked:
 movs r0,#0
 bx lr
// Version-checked displaced instructions and their literals are appended by builder.

.balign 4
.global original_positive
.thumb_func
original_positive:
.Loriginal_positive:
 ldr r0,=0x20000042
 movs r2,#0
 ldr pc,=0x800fd81

.balign 4
.global original_negative
.thumb_func
original_negative:
.Loriginal_negative:
 ldr r0,=0x20000042
 movs r2,#0
 ldr pc,=0x800b5b5

.balign 4
.global original_decoder
.thumb_func
original_decoder:
.Loriginal_decoder:
 ldr r1,=0x40020c10
 movs r0,#0
 ldr pc,=0x800b07d

.balign 4
.global original_gui
.thumb_func
original_gui:
.Loriginal_gui:
 push.w {r4, r5, r6, r7, r8, sb, sl, lr}
 ldr pc,=0x8029aad

.balign 4
.global code_end
code_end:
adjust_guards:
 .hword 0x599,0x56d,0x392,0x57f,0x5e5,0x5e6,0x18,0x0
.balign 4
.ltorg
