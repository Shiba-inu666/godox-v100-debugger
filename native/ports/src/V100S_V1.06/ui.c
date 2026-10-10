/* V100S V1.06 R10 port. Exact original identity is pinned in profiles.
 * Offline experimental firmware; hardware acceptance is pending. */
typedef unsigned int U;
typedef unsigned char B;
#define R8(o) (*(volatile B *)(0x20000000u+(o)))
#define USER(o) (*(volatile U *)((o)+0x10))
#define R32(o) (*(volatile U *)(0x20000000u+(o)))
#define F(a) ((U (*)())((a)|1u))
#define V(a) ((void (*)())((a)|1u))
extern void stock_sender(void),stock_rx(void),stock_focus(void),stock_close(void);
extern void stock_tick(void),stock_page(U,U),stock_activity(U,U);
extern void stock_sender_event(U),stock_rx_event(U);
static U group_modal(void);
static void group_focus(void),group_close(void),group_refresh(void),group_tap(U);
static U sub_drag(U);
U editor_target(void);
void editor_select(void);
extern void stock_rx_mode(void);
extern void stock_format(U,U,U,U,U,U,U,U);
extern void stock_sender_fields(U,U*,U*,U*);
static U valid(U obj) {return obj && F(0x803ce2c)(obj);}
static U parent(U obj) {return obj ? F(0x803b7f8)(obj) : 0;}
static U root(void) {
    U r=0;
    if (R8(0x5ef)==1 && R8(0x38c)==3) r=R32(0x650);
    if (R8(0x5ef)==2 && R8(0x38c)==4) r=R32(0x654);
    return valid(r) ? r : 0;
}
static U owns_row(void) {
    U r=root(),row=R32(0x15a0);
    if (!r || !valid(row)) return 0;
    return parent(row)==(R8(0x5ef)==1 ? R32(0x1604) : r);
}
static U owns_modal(void) {
    U r=root(),m=R32(0x15bc);
    return r && valid(m) && parent(m)==r && owns_row();
}
/* Only the added SUB editor uses Wi-Off geometry. Never spoof global page/role. */
void sub_format(U a,U b,U c,U d,U slider,U bar,U extra,U value) {
    stock_format(a,b,c,d,slider,bar,extra,value);
    if(value!=0x20000510 || a!=R32(0x15c8) || !owns_modal()) return;
    V(0x803e8cc)(c,0x80bbcdc,0);
    V(0x803a282)(a,9,-5,-66);
    V(0x803a29e)(c,a,0x12,-2,-2);
    V(0x803a29e)(b,c,0x12,-1,0);
    V(0x803a29e)(d,a,0x15,3,-2);
    V(0x803e756)(bar,F(0x803126c)(0xfd9f0a),0x20000);
}
static U visible(void) {return R8(0x4e6)==1 && (R8(0x513)&3)!=2;}
static void format_row(void) {
    if(R8(0x5ef)==1) {
        /* Native Sender numerical field and original fractional/decimal formatting.
         * Its shared slider refresh uses scratch group indices; preserve those. */
        U a=R8(0x532),b=R8(0x533);
        V(0x8012204)(R32(0x15ac),R32(0x15b0),R32(0x15a8),R32(0x15b4),0,0,0,0x20000510);
        R8(0x532)=a;R8(0x533)=b;
        if(!R8(0x511)) {
            V(0x8039590)(R32(0x15ac),"OFF");
            V(0x8039590)(R32(0x15b0),"");
            V(0x8039590)(R32(0x15a8),"");
            V(0x8039590)(R32(0x15b4),"");
        }
        V(0x803e8ea)(R32(0x15a4),R8(0x511)?255:127,0);
        if(R8(0x594)==1 || !R8(0x511)) V(0x803a14a)(R32(0x15b8),1);
        else V(0x803aa72)(R32(0x15b8),1);
        return;
    }
    V(0x800e57c)(R32(0x15a0),R32(0x15a4),R32(0x15a8),R32(0x15ac),R32(0x15b0),R32(0x15b4),R32(0x15b8));
}
static void add(U off) {V(0x8036a6c)(R32(0xa38),R32(off));}
void sub_focus(void) {
    if(group_modal()) {group_focus();return;}
    stock_focus();
    if (!owns_row() || !visible() || owns_modal()) return;
    U focused=F(0x8036c80)(R32(0xa38));
    V(0x8036cf0)(R32(0xa38));
    if (R8(0x5ef)==1) {
        add(0x1608);add(0x15a0);
        for(U i=1;i<5;i++) add(0x1608 + 4*i);
        add(0x17a8);add(0x17c4);
    } else {
        add(0x18b0);add(0x1834);add(0x1878);add(0x1894);add(0x15a0);
    }
    if (valid(focused)) V(0x8036b60)(focused);
}
void sub_close(void) {
    U own=owns_modal();
    stock_close();
    if(own && owns_row() && visible()) {
        /* Native close applies the compact hotshoe footer formatter first. */
        if(R8(0x5ef)==1) format_row();
        V(0x8036b60)(R32(0x15a0));
    }
}
void sub_activity(U code,U original_root) {
    if(owns_modal() && original_root==R32(0x628)) original_root=root();
    stock_activity(code,original_root);
}
void sub_sender_event(U e) {
    if(group_modal()) {
        U code=F(0x8035fac)(e);
        V(0x802b63e)(code,0x200005f2,0x19,0);
        if(code==0xc && F(0x8037ef4)(F(0x8037ee8)())==2) {
            if(!R8(0x5f2)) group_close();
            R8(0x5f2)=0;
        }
        return;
    }
    if(owns_modal()) V(0x801aa5c)(e); else stock_sender_event(e);
}
void sub_rx_event(U e) {
    if(owns_modal()) V(0x801aa5c)(e); else stock_rx_event(e);
}
static void layout(U show) {
    if(R8(0x5ef)==1) {
        for(U i=1;i<5;i++) V(0x803e3b4)(R32(0x1608 + 4*i),0,(i+show)*86);
    } else {
        /* Multi keeps its stock full-width ZOOM footer. */
        if ((R8(0x513)&3)==2) return;
        V(0x803e464)(R32(0x1878),show?156:237,55);
        V(0x803e464)(R32(0x1894),show?156:237,55);
        V(0x803a282)(R32(0x1894),show?5:6,0,-1);
        V(0x800c954)(R32(0x1894),R32(0x1898),R32(0x189c),R32(0x18a0),R32(0x18a4),R32(0x18a8),R32(0x18ac));
    }
}
static void entry(U event) {
    U code=F(0x8035fac)(event),r=root();
    if(!r || !owns_row()) return;
    stock_activity(code,r);
    if(sub_drag(event)) return;
    if(code!=4 || R8(0x5e9) || R8(0x5ea) || R8(0x59b) || !visible()
       || R8(0x3e8)!=R8(0x5ef) || valid(R32(0x15bc)) || group_modal()) return;
    if(R8(0x5ef)==1) V(0x801c098)(); else V(0x801c4a4)();
    V(0x8048cbc)(r);
    V(0x8036b60)(R32(0x15c4));
    if(F(0x8035fd8)(event)==R32(0xa30))
        V(0x8036038)(R32(0x15c4),4,R32(0xa30));
}
static U label(U p,U align,int x,int y,U font,U color,const char *text) {
    return F(0x8045a6c)(p,align,x,y,font,F(0x8031224)(color),text);
}
static void step(U event,U decrease) {
    U code=F(0x8035fac)(event),r=root();
    if(!r || R8(0x5ef)!=1 || !owns_row()) return;
    stock_activity(code,r);
    if(code!=4 || owns_modal() || group_modal() || R8(0x5e9) || R8(0x5ea) || R8(0x59b)
       || !visible() || R8(0x3e8)!=1 || !R8(0x511)) return;
    /* Exact native SUB button rule (1A814): 1D7FC steps; clamp at 70.
     * No main/group values, selector, radio packet or firing call is involved. */
    U value=R8(0x510);
    if(!decrease || value<70) value=F(0x801d98c)(decrease,value,3);
    R8(0x510)=value>70?70:value;
    format_row();
}
/* Sender SUB uses the same one-third-stop native stepping as its +/- keys.
 * Keep state on its row: a tap must not change power, and vertical scrolling
 * must never adjust SUB. Horizontal movement is relative to the press value. */
static U sub_drag(U e) {
    if(R8(0x5ef)!=1) return 0;
    U row=R32(0x15a0),code=F(0x8035fac)(e);
    if(F(0x8036024)(e)!=row || F(0x8035fd8)(e)!=R32(0xa2c)) return 0;
    U state=USER(row);
    if(code==4) return (state&0x60000000u)!=0;
    if(code==3 || code==9) {USER(row)=state|0x40000000u;return 0;}
    if(code!=1 && code!=2) return 0;
    if(owns_modal() || group_modal() || R8(0x5e9) || R8(0x5ea) || R8(0x59b)
       || (R8(0x36)&2) || R8(0x798) || R8(0x79a) || R8(0x79b)
       || !visible() || R8(0x3e8)!=1) {USER(row)=0x40000000u;return 0;}
    short point[2];V(0x8037f1c)(R32(0xa2c),point);
    if(code==1) {
        USER(row)=0x80000000u|((U)point[0]&511)|(((U)point[1]&511)<<9)
            |((U)(R8(0x510)>70?70:R8(0x510))<<18);
        return 0;
    }
    if(!(state&0x80000000u) || (state&0x40000000u)) return 0;
    int dx=point[0]-(int)(state&511),dy=point[1]-(int)((state>>9)&511);
    int ax=dx<0?-dx:dx,ay=dy<0?-dy:dy;
    if(!(state&0x20000000u)) {
        if(ay>8 && ay>ax) {USER(row)=state|0x40000000u;return 0;}
        if(ax<=8 || ax<ay) return 0;
        USER(row)=state|0x20000000u;
    }
    if(!R8(0x511)) return 0;
    U value=(state>>18)&127,n=(U)(ax*21/416);
    if(n>21)n=21;
    for(U i=0;i<n;i++) {
        if(dx<0 && value>=70)break;
        value=F(0x801d98c)(dx<0,value,3);
        if(value>70)value=70;
    }
    if(value!=R8(0x510)) {R8(0x510)=value;format_row();}
    return 0;
}
static void plus(U event) {step(event,0);}
static void minus(U event) {step(event,1);}
#include "s_bitmap.h"
struct Glyph {U font;unsigned short advance,w,h;short x,y;B bpp,pad;};
static U s_glyph(U font,struct Glyph *d,U ch,U next) {
    (void)font;(void)next;
    if(ch!='S') return 0;
    d->font=0;d->advance=25;d->w=23;d->h=29;d->x=1;d->y=-3;d->bpp=4;d->pad=0;
    return 1;
}
static const B *s_pixels(U font,U ch) {(void)font;return ch=='S'?s_bitmap:0;}
static const struct {U (*glyph)();const B *(*bitmap)();unsigned short height,baseline;
    B subpixel; signed char underline; B thickness,pad;U descriptor,fallback;}
    s_font={s_glyph,s_pixels,29,3,0,-3,2,0,0,0};
static void sender_controls(U row) {
    U field[7],down[2],up[2];
    /* Native group tile and the darker strip behind the minus button. */
    U tile=F(0x8045998)(row,7,0,0,46,78);
    V(0x803e8a0)(tile,0,0);V(0x803e79a)(tile,0,0);
    V(0x803e756)(tile,F(0x8031224)(0x525252),0);
    V(0x803aa72)(tile,2);
    U strip=F(0x8045998)(row,7,44,0,60,78);
    V(0x803e8a0)(strip,0,0);V(0x803e79a)(strip,0,0);
    V(0x803e756)(strip,F(0x8031224)(0x282828),0);
    V(0x803aa72)(strip,2);
    /* Re-enter native factory after its unused slider/bar allocation. */
    stock_sender_fields(row,field,down,up);
    R32(0x15ac)=field[0];R32(0x15b0)=field[1];
    R32(0x15a8)=field[2];R32(0x15b4)=field[3];
    V(0x803a0ac)(down[0],(U)minus,0,0);
    V(0x803a0ac)(up[0],(U)plus,0,0);
    /* Verified native S glyph; the numerical 0x805b294 font lacks letters. */
    R32(0x15a4)=label(row,7,0,0,(U)&s_font,0xcbcbcb,"S");
    V(0x803a29e)(R32(0x15a4),tile,9,0,-3);
    R32(0x15b8)=label(row,3,-73,4,0x80a1c14,0xcbcbcb,"\xee\x9a\x99");
}
static void build(U sender) {
    U r=root(); if(!r) return;
    /* Native SU-1 globals belong to the active page; never borrow remote state. */
    for(U o=0x15a0;o<=0x15b8;o+=4) R32(o)=0;
    U p=sender ? R32(0x1604) : r;
    U row=F(0x8045818)(p,sender?0:6,0,sender?86:-1,sender?480:156,sender?82:55,sender?2:1);
    R32(0x15a0)=row;
    V(0x803e8a0)(row,0,0);
    V(0x803e778)(row,F(0x8031224)(0xfd9f0a),5);
    if(sender) sender_controls(row);
    else {
        R32(0x15a4)=label(row,1,8,2,0x8053014,0x999999,R8(0x134a)?"\x53\x55\x42":"\xe5\x89\xaf\xe7\x81\xaf");
        R32(0x15ac)=label(row,9,0,10,0x8061364,0xcbcbcb,"");
        R32(0x15b0)=label(row,9,0,10,0x80536f0,0xcbcbcb,"");
        R32(0x15b4)=label(row,9,0,10,0x80536f0,0xcbcbcb,"");
        R32(0x15b8)=label(row,3,-6,4,0x80a1c14,0xcbcbcb,"\xee\x9a\x99");
    }
    V(0x803a0ac)(row,(U)entry,0,0);
    if(sender) {
        /* Native row/power arrays remain [M,A,B,C,D]. Only visual positions move. */
        V(0x803d0c4)(row,1);
    } else {
        /* Stock RX constructs the drawer before this added root-level footer.
         * Keep SUB immediately behind that same screen's drawer, matching the
         * native MODE/ZOOM layer for drawing and reverse-order touch search. */
        U drawer=R32(0x1404);
        if(valid(drawer) && parent(drawer)==r)
            V(0x803d0c4)(row,F(0x803b752)(drawer));
    }
    layout(visible());
    if(!visible()) V(0x803a14a)(row,1);
    format_row();
    R8(0x3e4)=R8(0x4e6);R8(0x3dc)=R8(0x510);R8(0x3de)=R8(0x594);R8(0x3e5)=R8(0x511);
    sub_focus();
}
void sub_sender(void) {
    stock_sender();build(1);
    /* Add a short-tap observer AFTER the original callbacks. Native title,
     * slider, long-press, +/- and scrolling flags/callbacks remain intact. */
    for(U g=0;g<5;g++) {
        V(0x803a0ac)(R32(0x1608 + 4*g),(U)group_tap,0,0);
        V(0x803a0ac)(R32(0x161c + 4*g),(U)group_tap,0,0);
        V(0x803a0ac)(R32(0x167c + 28*g),(U)group_tap,0,0);
    }
}
void sub_rx(void) {stock_rx();build(0);}
/* Stock mode refresh resets RX ZOOM width and alignment, including on first tick. */
void sub_rx_mode(void) {
    stock_rx_mode();
    if (R8(0x5ef)==2 && owns_row()) layout(visible());
}
void sub_refresh(void) {
    if(!owns_row()) return;
    U row=R32(0x15a0),show=visible();
    U hidden=F(0x803c686)(row,1);
    if(!show && owns_modal()) sub_close();
    if((show && hidden) || (!show && !hidden)) {
        if(show) V(0x803aa72)(row,1); else V(0x803a14a)(row,1);
        layout(show);
        /* Attachment visibility changes must not replace the drawer's focus
         * list while it is open, scrolling, or finishing its scroll event. */
        if(!owns_modal() && !R8(0x798) && !R8(0x79a) && !R8(0x79b)) sub_focus();
    }
    if(R8(0x3e4)!=R8(0x4e6) || R8(0x3dc)!=R8(0x510) || R8(0x3de)!=R8(0x594) || R8(0x3e5)!=R8(0x511)) {
        R8(0x3e4)=R8(0x4e6);R8(0x3dc)=R8(0x510);R8(0x3de)=R8(0x594);R8(0x3e5)=R8(0x511);
        format_row();
        if(owns_modal()) {
            V(0x8012204)(R32(0x15c8),R32(0x15cc),R32(0x15d0),R32(0x15d4),R32(0x15d8),R32(0x15dc),R32(0x15e0),0x20000510);
            V(0x8047fac)();
        }
    }
}
void sub_tick(void) {
    if(group_modal() && (R8(0x513)&3)==2) group_close();
    stock_tick();sub_refresh();group_refresh();
}
void sub_page(U page,U anim) {
    if(page<12 && page!=R8(0x5ef) && !R8(0x5e9)) {
        if(group_modal())group_close();
        U row=R32(0x15a0);
        /* Two complete screens coexist during native animation. Keep the
         * outgoing row visible for the same lifetime as MODE/ZOOM. */
        U old_sub=owns_row() || (page==1 && R8(0x5ef)==0 && R8(0x38c)==0
            && valid(row) && parent(row)==R32(0x628));
        if(old_sub) {
            if(valid(R32(0x15bc))) sub_close();
            /* Exit to the native power/wireless chooser keeps SUB visible
             * until the same screen deletion as MODE/ZOOM. A direct transition
             * into Sender must reclaim this subtree first: its five native
             * rows otherwise exhaust the fixed LVGL heap (R7 regression).
             * Normal role selection goes through the chooser first. */
            if(page==1) V(0x803abac)(row);
            for(U o=0x15a0;o<=0x15b8;o+=4) R32(o)=0;
        }
    }
    stock_page(page,anim);
}

/* LVGL v8 object user_data is the verified word at +0x10. The root owns
 * the editor pointer; the modal owns its controls. No new global RAM. */
#define GROUP_TAG 0x563a0000u
#define GROUP_MASK 0xffff0000u
/* Children: title, back, value (four native labels), mode, pause, -, +,
 * transparent slider (with a visible native bar as its first child). */
static U child(U obj,U i) {return F(0x803b574)(obj,i);}
static U group_modal(void) {
    U r=root();
    if(!r || R8(0x5ef)!=1) return 0;
    U m=USER(r);
    return valid(m) && parent(m)==r && (USER(m)&GROUP_MASK)==GROUP_TAG
        && (USER(m)&255)<5 ? m : 0;
}
static U group_index(void) {return USER(group_modal())&255;}
static U blocked(void) {
    return R8(0x5e9)||R8(0x5ea)||R8(0x59b)||R8(0x3e8)!=1
        ||R8(0x798)||R8(0x79a)||R8(0x79b)||(R8(0x513)&3)==2;
}
static U remembered(U g) {
    U word=USER(R32(0x166c + 28*g));
    return (word&GROUP_MASK)==GROUP_TAG ? (word&1) : 0;
}
static void remember(U g) {
    if(R8(0x514 + g)<2) USER(R32(0x166c + 28*g))=GROUP_TAG|R8(0x514 + g);
}
/* IRQ-safe scope test: read owned handles only, no LVGL traversal/allocation.
 * Cleared root user_data precedes custom editor deletion. Native SUB's parent
 * pointer is the verified lv_obj_t +4 word. Guards cover page transitions. */
static U ram_object(U p) {return !(p&3) && ((p>=0x20000000u && p<0x20040000u)
        ||(p>=0x10000000u && p<0x10010000u));}
U editor_target(void) {
    U page=R8(0x5ef),r=0,m;
    if(page!=R8(0x3e8)) return 0;
    if(page==1 && R8(0x38c)==3) r=R32(0x650);
    else if(page==2 && R8(0x38c)==4) r=R32(0x654);
    else if(page==0 && R8(0x38c)==0) r=R32(0x628);
    if(!ram_object(r))return 0;
    if(page==1) {
        m=USER(r);
        if(ram_object(m) && *(U*)(m+4)==r && (USER(m)&GROUP_MASK)==GROUP_TAG
           && (USER(m)&255)<5 && (R8(0x513)&3)!=2) return 0x11;
    }
    m=R32(0x15bc);
    if(ram_object(m) && *(U*)(m+4)==r && (R8(0x513)&3)!=2) return 0x12;
    return 0;
}
U editor_allowed(void) {
    return !(R8(0x59b)||R8(0x570)||R8(0x392)||R8(0x581)||R8(0x5e9)
       ||R8(0x5ea)||R8(0x18)||R8(0x798)||R8(0x79a)||R8(0x79b)
       ||(R8(0x31)&8)||(R8(0x36)&2));
}
void editor_select(void) {
    U selector=editor_target();
    if(selector==0x11)R8(0x504)=USER(USER(R32(0x650)))&255;
    if(selector)R8(0x535)=selector;
}
static void group_focus(void) {
    U m=group_modal();if(!m) return;
    V(0x8036cf0)(R32(0xa38));
    /* Only the value belongs to encoder focus. Touch owns mode/pause/back. */
    V(0x8036a6c)(R32(0xa38),child(m,2));
    V(0x8036b60)(child(m,2));
    V(0x8036b20)(R32(0xa38),1);
    editor_select();
}
static void group_refresh(void) {
    U m=group_modal();if(!m) return;
    U g=group_index(),mode=R8(0x514 + g);
    remember(g);U chosen=remembered(g);
    U field=child(m,2),cache=0x80000000u|mode|(R8(0x520 + g)<<2)
        |(R8(0x540 + g)<<10)|(R8(0x1340)<<18)|(R8(0x5a)<<19)|(chosen<<26);
    if(USER(field)==cache)return;
    USER(field)=cache;
    V(0x8039590)(child(child(m,3),0),chosen?"M":"TTL");
    U pause=child(m,4);
    V(0x8039590)(child(pause,0),mode==2?"OFF":"");
    for(U i=1;i<=2;i++) {
        if(mode==2)V(0x803a14a)(child(pause,i),1);
        else V(0x803aa72)(child(pause,i),1);
    }
    U value=child(field,0),numerator=child(field,1),slash=child(field,2),fraction=child(field,3);
    U slider=child(m,7),bar=child(slider,0),progress,range;
    if(chosen) {
        /* Native fraction/decimal formatter operates on this group's byte.
         * Reapply modal typography/geometry without spoofing global role/page. */
        U a=R8(0x532),b=R8(0x533);
        V(0x8012204)(value,numerator,slash,fraction,0,0,0,0x20000520 + g);
        R8(0x532)=a;R8(0x533)=b;
        V(0x803e8cc)(slash,0x80bbcdc,0);
        V(0x803a282)(value,9,-5,0);
        V(0x803a29e)(slash,value,0x12,-2,-2);
        V(0x803a29e)(numerator,slash,0x12,-1,0);
        V(0x803a29e)(fraction,value,0x15,3,-2);
        range=80;progress=R8(0x520 + g)<=80?80-R8(0x520 + g):0;
    } else {
        U a=R8(0x532),b=R8(0x533);
        V(0x801f164)(value,numerator,slash,fraction,0,0,0,0x20000540 + g);
        R8(0x532)=a;R8(0x533)=b;
        /* Keep the native sign glyph: the large numeric font has no ASCII
         * plus/minus. Use the original hotshoe sign font and alignment. */
        V(0x803e8cc)(slash,0x806e690,0);
        V(0x803a282)(value,9,12,0);
        V(0x803a29e)(slash,value,0x11,-5,0);
        range=18;progress=F(0x800ea1c)(R8(0x540 + g));
    }
    for(U i=0;i<4;i++)V(0x803e8ea)(child(field,i),mode==2?100:255,0);
    for(U i=0;i<2;i++) {
        U o=i?bar:slider,limit=range,n=progress;
        if(!i && chosen && R8(0x5a)) {limit=24;n=(progress*3+5)/10;}
        V(0x8030160)(o,0,limit);V(0x80301fc)(o,n,0);
    }
    V(0x803e756)(bar,F(0x803126c)(mode==2?0x666666:0xfd9f0a),0x20000);
}
static void group_close(void) {
    U m=group_modal();if(!m)return;
    U g=group_index();USER(root())=0;
    V(0x803abac)(m);
    R8(0x535)=0;R8(0x7a0)=0;R32(0x28)=0;
    R32(0xa34)=0;
    V(0x8036b20)(R32(0xa38),0);
    sub_focus();
    if((R8(0x513)&3)!=2 && valid(R32(0x1608 + 4*g)))
        V(0x8036b60)(R32(0x1608 + 4*g));
}
static void group_action(U e) {
    U m=group_modal();if(!m)return;
    U code=F(0x8035fac)(e),target=F(0x8035fb4)(e);
    stock_activity(code,root());
    if(code!=4 || blocked())return;
    U g=group_index(),mode=R8(0x514 + g);
    if(target==child(m,1)) {group_close();return;}
    if(target==child(m,3) || target==child(m,4)) {
        U previous=remembered(g);
        if(target==child(m,3)) {
            previous=!previous;USER(R32(0x166c + 28*g))=GROUP_TAG|previous;
            if(mode!=2) mode=previous;
        } else mode=mode==2?previous:2;
        R8(0x514 + g)=mode;R8(0x556 + g)=mode!=2;
        if(mode==2) R8(0x42a)&=~(1u<<g);else R8(0x42a)|=1u<<g;
        V(0x8016468)();
    } else if(mode!=2) {
        if(target==child(m,5)) V(0x8036038)(R32(0x1720 + 8*g),4,R32(0xa2c));
        else if(target==child(m,6)) V(0x8036038)(R32(0x16f8 + 8*g),4,R32(0xa2c));
    }
    /* SET/tapping the number never changes encoder purpose. Native +/- clears
     * list selection, so restore the editor selection after those callbacks. */
    editor_select();V(0x8036b20)(R32(0xa38),1);
    V(0x80168e0)();group_refresh();
}
static void group_slider(U e) {
    U m=group_modal();if(!m)return;
    U code=F(0x8035fac)(e);stock_activity(code,root());
    if(code!=0x1c)return;
    U g=group_index(),mode=R8(0x514 + g),slider=child(m,7);
    if(!blocked() && mode!=2) {
        U n=F(0x803013c)(slider);
        if(mode==1) {
            if(R8(0x5a)) {n=n>24?24:n;n=(n/3)*10+(n%3==1?3:n%3==2?7:0);}
            R8(0x520 + g)=80-(n>80?80:n);
        }
        else R8(0x540 + g)=F(0x804ddf8)(n>18?18:n);
        editor_select();V(0x80168e0)();
    }
    USER(child(m,2))=0;group_refresh();
}
static U group_button(U m,int x,int y,U w,U h,U font,const char *text) {
    U b=F(0x8045818)(m,1,x,y,w,h,1);
    /* Set an explicit opaque button body; do not inherit a hidden native style. */
    V(0x803e76e)(b,255,0);
    V(0x803e8a0)(b,10,0);
    V(0x803e756)(b,F(0x8031224)(0x282828),0);
    V(0x803e778)(b,F(0x8031224)(0xfd9f0a),5);
    label(b,9,0,0,font,0xcbcbcb,text);
    V(0x803a0ac)(b,(U)group_action,0,0);
    return b;
}
static void group_open(U g) {
    U r=root();remember(g);
    V(0x801c098)();V(0x8036cf0)(R32(0xa38));
    U m=F(0x8045998)(r,2,0,0,480,360);
    USER(r)=m;USER(m)=GROUP_TAG|g;
    V(0x803e8a0)(m,0,0);V(0x803e79a)(m,0,0);
    V(0x803e756)(m,F(0x8031084)(),0);V(0x803a14a)(m,0x4000);
    const char *names[]={"M","A","B","C","D"};
    if(g) {
        /* Exact RX group palette initialized by the vendor image: A/B/C/D
         * are entries 10/11/12/13, with white/black/white/black text. */
        U badge=F(0x8045998)(m,1,16,4,44,44);
        V(0x803e8a0)(badge,5,0);V(0x803e79a)(badge,0,0);
        U color=*(volatile unsigned short *)(0x2000075cu+2*(g+9));
        V(0x803e756)(badge,color,0);V(0x803e76e)(badge,255,0);
        V(0x803aa72)(badge,2);
        label(badge,9,0,0,0x806ad4c,(g==2||g==4)?0x000000:0xffffff,names[g]);
    } else label(m,1,20,14,0x806ad4c,0xcbcbcb,names[g]);
    U back=group_button(m,402,0,78,52,0x8079b58,"\xee\x9a\x92");
    U field=group_button(m,92,66,296,126,0x806a448,"");
    label(field,9,0,0,0x806148c,0xcbcbcb,"");
    label(field,9,0,0,0x80bbcdc,0xcbcbcb,"");
    label(field,9,0,0,0x8062128,0xcbcbcb,"");
    group_button(m,20,275,270,65,0x805fcac,"");
    U pause=group_button(m,304,275,156,65,0x805fcac,"");
    for(U i=0;i<2;i++) {
        U line=F(0x8045998)(pause,9,i?8:-8,0,5,24);
        V(0x803e8a0)(line,2,0);V(0x803e79a)(line,0,0);
        V(0x803e756)(line,F(0x8031224)(0xcbcbcb),0);V(0x803aa72)(line,2);
    }
    U minus=group_button(m,8,87,84,84,0x806e690,"\xee\x9a\x86");
    U plus=group_button(m,388,87,84,84,0x806e690,"\xee\x9a\x85");
    U plain[]={back,field,minus,plus};
    for(U i=0;i<4;i++) {
        V(0x803e756)(plain[i],F(0x8031084)(),0);
        V(0x803e778)(plain[i],F(0x8031084)(),0);
        V(0x803e778)(plain[i],F(0x8031084)(),5);
    }
    U slider=F(0x8045c5c)(m,1,32,186,416,48);
    V(0x803a0ac)(slider,(U)group_slider,0,0);
    U bar=F(0x802fffc)(slider);
    V(0x803e464)(bar,416,8);V(0x803a282)(bar,9,0,0);
    V(0x803aa72)(bar,2);
    for(U part=0;part<=0x20000;part+=0x20000) V(0x803e8a0)(bar,3,part);
    V(0x803e756)(bar,F(0x8031224)(0x525252),0);
    V(0x803e76e)(bar,255,0);
    group_focus();group_refresh();
}
static void group_tap(U e) {
    U target=F(0x8035fb4)(e),code=F(0x8035fac)(e);
    /* Bubble events from +/- never become row taps. */
    if(F(0x8036024)(e)!=target)return;
    U g=0;for(;g<5;g++)if(target==R32(0x1608 + 4*g)
        ||target==R32(0x161c + 4*g)||target==R32(0x167c + 28*g))break;
    if(g==5)return;
    remember(g);
    if(F(0x8035fd8)(e)!=R32(0xa2c))return;
    short point[2];V(0x8037f1c)(R32(0xa2c),point);
    U x=(U)point[0]&511,y=(U)point[1]&511,state=USER(target);
    if(code==1) {USER(target)=0x80000000u|x|(y<<9);return;}
    if(!(state&0x80000000u))return;
    int dx=(int)x-(int)(state&511),dy=(int)y-(int)((state>>9)&511);
    if(code==3 || code==5 || code==6 || code==9 || dx>8 || dx< -8 || dy>8 || dy< -8)
        USER(target)=state|=0x40000000u;
    if(code!=4)return;
    USER(target)=0;
    if(!(state&0x40000000u) && !blocked() && root() && R8(0x5ef)==1
        && !owns_modal() && !group_modal() && !valid(R32(0x17f4)))group_open(g);
}
