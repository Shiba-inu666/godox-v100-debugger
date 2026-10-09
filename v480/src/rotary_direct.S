.syntax unified
.cpu cortex-m4
.thumb
.text

.balign 4
.global positive_wrapper
.thumb_func
positive_wrapper:
 push {r0,r1,r2,r3,r4,r5,r6,lr}
 mrs r4,primask
 cpsid i
 bl .Lscope_guard
 cbz r0,positive_fallback
 ldr r5,=0x2000053d
 strb r0,[r5]
 pop {r0,r1,r2,r3}
 bl .Loriginal_positive
 movs r6,#0
 strb r6,[r5]
 msr primask,r4
 pop {r4,r5,r6,pc}
positive_fallback:
 msr primask,r4
 pop {r0,r1,r2,r3,r4,r5,r6,lr}
 b .Loriginal_positive

.balign 4
.global negative_wrapper
.thumb_func
negative_wrapper:
 push {r0,r1,r2,r3,r4,r5,r6,lr}
 mrs r4,primask
 cpsid i
 bl .Lscope_guard
 cbz r0,negative_fallback
 ldr r5,=0x2000053d
 strb r0,[r5]
 pop {r0,r1,r2,r3}
 bl .Loriginal_negative
 movs r6,#0
 strb r6,[r5]
 msr primask,r4
 pop {r4,r5,r6,pc}
negative_fallback:
 msr primask,r4
 pop {r0,r1,r2,r3,r4,r5,r6,lr}
 b .Loriginal_negative

.balign 4
.global decoder_wrapper
.thumb_func
decoder_wrapper:
 push {r0,r1,r2,r3,r4,r5,r6,lr}
 mrs r4,primask
 cpsid i
 bl .Lscope_guard
 cbz r0,decoder_fallback
 ldr r6,=0x20000028
 ldr r5,[r6]
 pop {r0,r1,r2,r3}
 bl .Loriginal_decoder
 str r5,[r6]
 msr primask,r4
 pop {r4,r5,r6,pc}
decoder_fallback:
 msr primask,r4
 pop {r0,r1,r2,r3,r4,r5,r6,lr}
 b .Loriginal_decoder
.balign 4
.global scope_guard
.thumb_func
scope_guard:
.Lscope_guard:
 ldr r1,=0x20000000

 ldrb.w r0,[r1,#1341]
 cmp r0,#0
 bne denied
 adr r3,byte_guards
guard_loop:
 ldrh r2,[r3],#2
 cbz r2,guard_flags
 ldrb r2,[r1,r2]
 cmp r2,#0
 bne denied
 b guard_loop
guard_flags:
 ldrb r2,[r1,#0x31]
 tst r2,#8
 bne denied
 ldrb r2,[r1,#58]
 tst r2,#2
 bne denied
 ldr.w r2,[r1,#1596]
 cbz r2,denied
 adr r3,word_guards
guard_word_loop:
 ldrh r2,[r3],#2
 cbz r2,.Lguard_mode_load
 ldr r2,[r1,r2]
 cmp r2,#0
 bne denied
 b guard_word_loop
.global guard_mode_load
guard_mode_load:
.Lguard_mode_load:
 ldrb.w r2,[r1,#1307]
 ands r2,r2,#3
 cbz r2,ttl
 cmp r2,#1
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
.global original_decoder
.thumb_func
original_decoder:
.Loriginal_decoder:
 push {r4,r5,r6,r7}
 ldr r0, =0x40020410

 ldr pc, =0x800b4f5

.balign 4
.global original_positive
.thumb_func
original_positive:
.Loriginal_positive:

 ldr r0, =0x20000046
 movs r2,#0
 ldr pc, =0x8010855

.balign 4
.global original_negative
.thumb_func
original_negative:
.Loriginal_negative:

 ldr r0, =0x20000046
 movs r2,#0
 ldr pc, =0x800b9f5

.balign 4
.global code_end
code_end:
byte_guards:
 .hword 0x5fb,0x350,0x3af,0x5a3,0x576,0x358,0x589,0x5f5,0x5f6,0x7ae,0x7b0,0x7b1,0x18,0
word_guards:
 .hword 0x1bb4,0x15e4,0
.balign 4
.ltorg
