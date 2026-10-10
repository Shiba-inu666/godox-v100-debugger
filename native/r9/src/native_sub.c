/* V100F 1.03 only. Native UI research module; NO firing-path patch.
 * All addresses are verified against the exact original image. */
typedef unsigned int U;
typedef unsigned char B;
#define R8(o) (*(volatile B *)(0x20000000u+(o)))
#define R32(o) (*(volatile U *)(0x20000000u+(o)))
#define F(a) ((U (*)())((a)|1u))
#define V(a) ((void (*)())((a)|1u))
extern void stock_sender(void),stock_rx(void),stock_focus(void),stock_close(void);
extern void stock_tick(void),stock_page(U,U),stock_activity(U,U);
extern void stock_sender_event(U),stock_rx_event(U);
static U group_modal(void);
static void group_focus(void),group_close(void),group_refresh(void),group_tap(U);
U editor_target(void);
void editor_select(void);
extern void stock_rx_mode(void);
extern void stock_format(U,U,U,U,U,U,U,U);
extern void stock_sender_fields(U,U*,U*,U*);
static U valid(U obj) {return obj && F(0x0803cdbc)(obj);}
static U parent(U obj) {return obj ? F(0x0803b788)(obj) : 0;}
static U root(void) {
    U r=0;
    if (R8(0x59f)==1 && R8(0x33c)==3) r=R32(0x600);
    if (R8(0x59f)==2 && R8(0x33c)==4) r=R32(0x604);
    return valid(r) ? r : 0;
}
static U owns_row(void) {
    U r=root(),row=R32(0x1550);
    if (!r || !valid(row)) return 0;
    return parent(row)==(R8(0x59f)==1 ? R32(0x15b4) : r);
}
static U owns_modal(void) {
    U r=root(),m=R32(0x156c);
    return r && valid(m) && parent(m)==r && owns_row();
}
/* Only the added SUB editor uses Wi-Off geometry. Never spoof global page/role. */
void sub_format(U a,U b,U c,U d,U slider,U bar,U extra,U value) {
    stock_format(a,b,c,d,slider,bar,extra,value);
    if(value!=0x200004c0 || a!=R32(0x1578) || !owns_modal()) return;
    V(0x0803e85c)(c,0x080bbd4c,0);
    V(0x0803a212)(a,9,-5,-66);
    V(0x0803a22e)(c,a,0x12,-2,-2);
    V(0x0803a22e)(b,c,0x12,-1,0);
    V(0x0803a22e)(d,a,0x15,3,-2);
    V(0x0803e6e6)(bar,F(0x080311fc)(0xfd9f0a),0x20000);
}
static U visible(void) {return R8(0x496)==1 && (R8(0x4c3)&3)!=2;}
static void format_row(void) {
    if(R8(0x59f)==1) {
        /* Native Sender numerical field and original fractional/decimal formatting.
         * Its shared slider refresh uses scratch group indices; preserve those. */
        U a=R8(0x4e2),b=R8(0x4e3);
        V(0x0801249c)(R32(0x155c),R32(0x1560),R32(0x1558),R32(0x1564),0,0,0,0x200004c0);
        R8(0x4e2)=a;R8(0x4e3)=b;
        if(!R8(0x4c1)) {
            V(0x08039520)(R32(0x155c),"OFF");
            V(0x08039520)(R32(0x1560),"");
            V(0x08039520)(R32(0x1558),"");
            V(0x08039520)(R32(0x1564),"");
        }
        V(0x0803e87a)(R32(0x1554),R8(0x4c1)?255:127,0);
        if(R8(0x544)==1 || !R8(0x4c1)) V(0x0803a0da)(R32(0x1568),1);
        else V(0x0803aa02)(R32(0x1568),1);
        return;
    }
    V(0x0800e12c)(R32(0x1550),R32(0x1554),R32(0x1558),R32(0x155c),R32(0x1560),R32(0x1564),R32(0x1568));
}
static void add(U off) {V(0x080369fc)(R32(0x9e8),R32(off));}
void sub_focus(void) {
    if(group_modal()) {group_focus();return;}
    stock_focus();
    if (!owns_row() || !visible() || owns_modal()) return;
    U focused=F(0x08036c10)(R32(0x9e8));
    V(0x08036c80)(R32(0x9e8));
    if (R8(0x59f)==1) {
        add(0x15b8);add(0x1550);
        for(U i=1;i<5;i++) add(0x15b8+4*i);
        add(0x1758);add(0x1774);
    } else {
        add(0x1860);add(0x17e4);add(0x1828);add(0x1844);add(0x1550);
    }
    if (valid(focused)) V(0x08036af0)(focused);
}
void sub_close(void) {
    U own=owns_modal();
    stock_close();
    if(own && owns_row() && visible()) {
        /* Native close applies the compact hotshoe footer formatter first. */
        if(R8(0x59f)==1) format_row();
        V(0x08036af0)(R32(0x1550));
    }
}
void sub_activity(U code,U original_root) {
    if(owns_modal() && original_root==R32(0x5d8)) original_root=root();
    stock_activity(code,original_root);
}
void sub_sender_event(U e) {
    if(group_modal()) {
        U code=F(0x08035f3c)(e);
        V(0x0802b5d6)(code,0x200005a2,0x19,0);
        if(code==0xc && F(0x08037e84)(F(0x08037e78)())==2) {
            if(!R8(0x5a2)) group_close();
            R8(0x5a2)=0;
        }
        return;
    }
    if(owns_modal()) V(0x0801a950)(e); else stock_sender_event(e);
}
void sub_rx_event(U e) {
    if(owns_modal()) V(0x0801a950)(e); else stock_rx_event(e);
}
static void layout(U show) {
    if(R8(0x59f)==1) {
        for(U i=1;i<5;i++) V(0x0803e344)(R32(0x15b8+4*i),0,(i+show)*86);
    } else {
        /* Multi keeps its stock full-width ZOOM footer. */
        if ((R8(0x4c3)&3)==2) return;
        V(0x0803e3f4)(R32(0x1828),show?156:237,55);
        V(0x0803e3f4)(R32(0x1844),show?156:237,55);
        V(0x0803a212)(R32(0x1844),show?5:6,0,-1);
        V(0x0800c3d4)(R32(0x1844),R32(0x1848),R32(0x184c),R32(0x1850),R32(0x1854),R32(0x1858),R32(0x185c));
    }
}
static void entry(U event) {
    U code=F(0x08035f3c)(event),r=root();
    if(!r || !owns_row()) return;
    stock_activity(code,r);
    if(code!=4 || R8(0x599) || R8(0x59a) || R8(0x54b) || !visible()
       || R8(0x398)!=R8(0x59f) || valid(R32(0x156c)) || group_modal()) return;
    if(R8(0x59f)==1) V(0x0801bf44)(); else V(0x0801c350)();
    V(0x08048c64)(r);
    V(0x08036af0)(R32(0x1574));
    if(F(0x08035f68)(event)==R32(0x9e0))
        V(0x08035fc8)(R32(0x1574),4,R32(0x9e0));
}
static U label(U p,U align,int x,int y,U font,U color,const char *text) {
    return F(0x080459f0)(p,align,x,y,font,F(0x080311b4)(color),text);
}
static void step(U event,U decrease) {
    U code=F(0x08035f3c)(event),r=root();
    if(!r || R8(0x59f)!=1 || !owns_row()) return;
    stock_activity(code,r);
    if(code!=4 || owns_modal() || group_modal() || R8(0x599) || R8(0x59a) || R8(0x54b)
       || !visible() || R8(0x398)!=1 || !R8(0x4c1)) return;
    /* Exact native SUB button rule (1A814): 1D7FC steps; clamp at 70.
     * No main/group values, selector, radio packet or firing call is involved. */
    U value=R8(0x4c0);
    if(!decrease || value<70) value=F(0x0801d7fc)(decrease,value,3);
    R8(0x4c0)=value>70?70:value;
    format_row();
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
    U tile=F(0x0804591c)(row,7,0,0,46,78);
    V(0x0803e830)(tile,0,0);V(0x0803e72a)(tile,0,0);
    V(0x0803e6e6)(tile,F(0x080311b4)(0x525252),0);
    V(0x0803aa02)(tile,2);
    U strip=F(0x0804591c)(row,7,44,0,60,78);
    V(0x0803e830)(strip,0,0);V(0x0803e72a)(strip,0,0);
    V(0x0803e6e6)(strip,F(0x080311b4)(0x282828),0);
    V(0x0803aa02)(strip,2);
    /* Re-enter native factory after its unused slider/bar allocation. */
    stock_sender_fields(row,field,down,up);
    R32(0x155c)=field[0];R32(0x1560)=field[1];
    R32(0x1558)=field[2];R32(0x1564)=field[3];
    V(0x0803a03c)(down[0],(U)minus,0,0);
    V(0x0803a03c)(up[0],(U)plus,0,0);
    /* Verified native S glyph; the numerical 0x0805B304 font lacks letters. */
    R32(0x1554)=label(row,7,0,0,(U)&s_font,0xcbcbcb,"S");
    V(0x0803a22e)(R32(0x1554),tile,9,0,-3);
    R32(0x1568)=label(row,3,-73,4,0x080a1c84,0xcbcbcb,(const char *)0x0804af84);
}
static void build(U sender) {
    U r=root(); if(!r) return;
    /* Native SU-1 globals belong to the active page; never borrow remote state. */
    for(U o=0x1550;o<=0x1568;o+=4) R32(o)=0;
    U p=sender ? R32(0x15b4) : r;
    U row=F(0x0804579c)(p,sender?0:6,0,sender?86:-1,sender?480:156,sender?82:55,sender?2:1);
    R32(0x1550)=row;
    V(0x0803e830)(row,0,0);
    V(0x0803e708)(row,F(0x080311b4)(0xfd9f0a),5);
    if(sender) sender_controls(row);
    else {
        R32(0x1554)=label(row,1,8,2,0x08053084,0x999999,R8(0x12fa)?(const char*)0x0804ae38:(const char*)0x0804ae30);
        R32(0x155c)=label(row,9,0,10,0x080613d4,0xcbcbcb,"");
        R32(0x1560)=label(row,9,0,10,0x08053760,0xcbcbcb,"");
        R32(0x1564)=label(row,9,0,10,0x08053760,0xcbcbcb,"");
        R32(0x1568)=label(row,3,-6,4,0x080a1c84,0xcbcbcb,(const char *)0x0804af84);
    }
    V(0x0803a03c)(row,(U)entry,0,0);
    if(sender) {
        /* Native row/power arrays remain [M,A,B,C,D]. Only visual positions move. */
        V(0x0803d054)(row,1);
    } else {
        /* Stock RX constructs the drawer before this added root-level footer.
         * Keep SUB immediately behind that same screen's drawer, matching the
         * native MODE/ZOOM layer for drawing and reverse-order touch search. */
        U drawer=R32(0x13b4);
        if(valid(drawer) && parent(drawer)==r)
            V(0x0803d054)(row,F(0x0803b6e2)(drawer));
    }
    layout(visible());
    if(!visible()) V(0x0803a0da)(row,1);
    format_row();
    R8(0x394)=R8(0x496);R8(0x38c)=R8(0x4c0);R8(0x38e)=R8(0x544);R8(0x395)=R8(0x4c1);
    sub_focus();
}
void sub_sender(void) {
    stock_sender();build(1);
    /* Add a short-tap observer AFTER the original callbacks. Native title,
     * slider, long-press, +/- and scrolling flags/callbacks remain intact. */
    for(U g=0;g<5;g++) {
        V(0x0803a03c)(R32(0x15b8+4*g),(U)group_tap,0,0);
        V(0x0803a03c)(R32(0x15cc+4*g),(U)group_tap,0,0);
        V(0x0803a03c)(R32(0x162c+28*g),(U)group_tap,0,0);
    }
}
void sub_rx(void) {stock_rx();build(0);}
/* Stock mode refresh resets RX ZOOM width and alignment, including on first tick. */
void sub_rx_mode(void) {
    stock_rx_mode();
    if (R8(0x59f)==2 && owns_row()) layout(visible());
}
void sub_refresh(void) {
    if(!owns_row()) return;
    U row=R32(0x1550),show=visible();
    U hidden=F(0x0803c616)(row,1);
    if(!show && owns_modal()) sub_close();
    if((show && hidden) || (!show && !hidden)) {
        if(show) V(0x0803aa02)(row,1); else V(0x0803a0da)(row,1);
        layout(show);
        /* Attachment visibility changes must not replace the drawer's focus
         * list while it is open, scrolling, or finishing its scroll event. */
        if(!owns_modal() && !R8(0x748) && !R8(0x74a) && !R8(0x74b)) sub_focus();
    }
    if(R8(0x394)!=R8(0x496) || R8(0x38c)!=R8(0x4c0) || R8(0x38e)!=R8(0x544) || R8(0x395)!=R8(0x4c1)) {
        R8(0x394)=R8(0x496);R8(0x38c)=R8(0x4c0);R8(0x38e)=R8(0x544);R8(0x395)=R8(0x4c1);
        format_row();
        if(owns_modal()) {
            V(0x0801249c)(R32(0x1578),R32(0x157c),R32(0x1580),R32(0x1584),R32(0x1588),R32(0x158c),R32(0x1590),0x200004c0);
            V(0x08047f0c)();
        }
    }
}
void sub_tick(void) {
    if(group_modal() && (R8(0x4c3)&3)==2) group_close();
    stock_tick();sub_refresh();group_refresh();
}
void sub_page(U page,U anim) {
    if(page<12 && page!=R8(0x59f) && !R8(0x599)) {
        if(group_modal())group_close();
        U row=R32(0x1550);
        /* Two complete screens coexist during native animation. Keep the
         * outgoing row visible for the same lifetime as MODE/ZOOM. */
        U old_sub=owns_row() || (page==1 && R8(0x59f)==0 && R8(0x33c)==0
            && valid(row) && parent(row)==R32(0x5d8));
        if(old_sub) {
            if(valid(R32(0x156c))) sub_close();
            /* Exit to the native power/wireless chooser keeps SUB visible
             * until the same screen deletion as MODE/ZOOM. A direct transition
             * into Sender must reclaim this subtree first: its five native
             * rows otherwise exhaust the fixed LVGL heap (R7 regression).
             * Normal role selection goes through the chooser first. */
            if(page==1) V(0x0803ab3c)(row);
            for(U o=0x1550;o<=0x1568;o+=4) R32(o)=0;
        }
    }
    stock_page(page,anim);
}

/* LVGL v8 object user_data is the verified word at +0x10. The root owns
 * the editor pointer; the modal owns its controls. No new global RAM. */
#define USER(o) (*(volatile U *)((o)+0x10))
#define GROUP_TAG 0x56390000u
#define GROUP_MASK 0xffff0000u
/* Children: title, back, value (four native labels), mode, pause, -, +,
 * transparent slider (with a visible native bar as its first child). */
static U child(U obj,U i) {return F(0x0803b504)(obj,i);}
static U group_modal(void) {
    U r=root();
    if(!r || R8(0x59f)!=1) return 0;
    U m=USER(r);
    return valid(m) && parent(m)==r && (USER(m)&GROUP_MASK)==GROUP_TAG
        && (USER(m)&255)<5 ? m : 0;
}
static U group_index(void) {return USER(group_modal())&255;}
static U blocked(void) {
    return R8(0x599)||R8(0x59a)||R8(0x54b)||R8(0x398)!=1
        ||R8(0x748)||R8(0x74a)||R8(0x74b)||(R8(0x4c3)&3)==2;
}
static U remembered(U g) {
    U word=USER(R32(0x161c+28*g));
    return (word&GROUP_MASK)==GROUP_TAG ? (word&1) : 0;
}
static void remember(U g) {
    if(R8(0x4c4+g)<2) USER(R32(0x161c+28*g))=GROUP_TAG|R8(0x4c4+g);
}
/* IRQ-safe scope test: read owned handles only, no LVGL traversal/allocation.
 * Cleared root user_data precedes custom editor deletion. Native SUB's parent
 * pointer is the verified lv_obj_t +4 word. Guards cover page transitions. */
static U ram_object(U p) {return !(p&3) && ((p>=0x20000000u && p<0x20040000u)
        ||(p>=0x10000000u && p<0x10010000u));}
U editor_target(void) {
    U page=R8(0x59f),r=0,m;
    if(page!=R8(0x398)) return 0;
    if(page==1 && R8(0x33c)==3) r=R32(0x600);
    else if(page==2 && R8(0x33c)==4) r=R32(0x604);
    else if(page==0 && R8(0x33c)==0) r=R32(0x5d8);
    if(!ram_object(r))return 0;
    if(page==1) {
        m=USER(r);
        if(ram_object(m) && *(U*)(m+4)==r && (USER(m)&GROUP_MASK)==GROUP_TAG
           && (USER(m)&255)<5 && (R8(0x4c3)&3)!=2) return 0x11;
    }
    m=R32(0x156c);
    if(ram_object(m) && *(U*)(m+4)==r && (R8(0x4c3)&3)!=2) return 0x12;
    return 0;
}
U editor_allowed(void) {
    return !(R8(0x54b)||R8(0x51e)||R8(0x342)||R8(0x531)||R8(0x599)
       ||R8(0x59a)||R8(0x18)||R8(0x748)||R8(0x74a)||R8(0x74b)
       ||(R8(0x31)&8)||(R8(0x36)&2));
}
void editor_select(void) {
    U selector=editor_target();
    if(selector==0x11)R8(0x4b4)=USER(USER(R32(0x600)))&255;
    if(selector)R8(0x4e5)=selector;
}
static void group_focus(void) {
    U m=group_modal();if(!m) return;
    V(0x08036c80)(R32(0x9e8));
    /* Only the value belongs to encoder focus. Touch owns mode/pause/back. */
    V(0x080369fc)(R32(0x9e8),child(m,2));
    V(0x08036af0)(child(m,2));
    V(0x08036ab0)(R32(0x9e8),1);
    editor_select();
}
static void group_refresh(void) {
    U m=group_modal();if(!m) return;
    U g=group_index(),mode=R8(0x4c4+g);
    remember(g);U chosen=remembered(g);
    U field=child(m,2),cache=0x80000000u|mode|(R8(0x4d0+g)<<2)
        |(R8(0x4ef+g)<<10)|(R8(0x12f0)<<18)|(R8(0x5a)<<19)|(chosen<<26);
    if(USER(field)==cache)return;
    USER(field)=cache;
    V(0x08039520)(child(child(m,3),0),chosen?"M":"TTL");
    U pause=child(m,4);
    V(0x08039520)(child(pause,0),mode==2?"OFF":"");
    for(U i=1;i<=2;i++) {
        if(mode==2)V(0x0803a0da)(child(pause,i),1);
        else V(0x0803aa02)(child(pause,i),1);
    }
    U value=child(field,0),numerator=child(field,1),slash=child(field,2),fraction=child(field,3);
    U slider=child(m,7),bar=child(slider,0),progress,range;
    if(chosen) {
        /* Native fraction/decimal formatter operates on this group's byte.
         * Reapply modal typography/geometry without spoofing global role/page. */
        U a=R8(0x4e2),b=R8(0x4e3);
        V(0x0801249c)(value,numerator,slash,fraction,0,0,0,0x200004d0+g);
        R8(0x4e2)=a;R8(0x4e3)=b;
        V(0x0803e85c)(slash,0x080bbd4c,0);
        V(0x0803a212)(value,9,-5,0);
        V(0x0803a22e)(slash,value,0x12,-2,-2);
        V(0x0803a22e)(numerator,slash,0x12,-1,0);
        V(0x0803a22e)(fraction,value,0x15,3,-2);
        range=80;progress=R8(0x4d0+g)<=80?80-R8(0x4d0+g):0;
    } else {
        U a=R8(0x4e2),b=R8(0x4e3);
        V(0x0801efc4)(value,numerator,slash,fraction,0,0,0,0x200004ef+g);
        R8(0x4e2)=a;R8(0x4e3)=b;
        /* Keep the native sign glyph: the large numeric font has no ASCII
         * plus/minus. Use the original hotshoe sign font and alignment. */
        V(0x0803e85c)(slash,0x0806e700,0);
        V(0x0803a212)(value,9,12,0);
        V(0x0803a22e)(slash,value,0x11,-5,0);
        range=18;progress=F(0x0800e5cc)(R8(0x4ef+g));
    }
    for(U i=0;i<4;i++)V(0x0803e87a)(child(field,i),mode==2?100:255,0);
    for(U i=0;i<2;i++) {
        U o=i?bar:slider,limit=range,n=progress;
        if(!i && chosen && R8(0x5a)) {limit=24;n=(progress*3+5)/10;}
        V(0x080300f0)(o,0,limit);V(0x0803018c)(o,n,0);
    }
    V(0x0803e6e6)(bar,F(0x080311fc)(mode==2?0x666666:0xfd9f0a),0x20000);
}
static void group_close(void) {
    U m=group_modal();if(!m)return;
    U g=group_index();USER(root())=0;
    V(0x0803ab3c)(m);
    R8(0x4e5)=0;R8(0x750)=0;R32(0x28)=0;
    R32(0x9e4)=0;
    V(0x08036ab0)(R32(0x9e8),0);
    sub_focus();
    if((R8(0x4c3)&3)!=2 && valid(R32(0x15b8+4*g)))
        V(0x08036af0)(R32(0x15b8+4*g));
}
static void group_action(U e) {
    U m=group_modal();if(!m)return;
    U code=F(0x08035f3c)(e),target=F(0x08035f44)(e);
    stock_activity(code,root());
    if(code!=4 || blocked())return;
    U g=group_index(),mode=R8(0x4c4+g);
    if(target==child(m,1)) {group_close();return;}
    if(target==child(m,3) || target==child(m,4)) {
        U previous=remembered(g);
        if(target==child(m,3)) {
            previous=!previous;USER(R32(0x161c+28*g))=GROUP_TAG|previous;
            if(mode!=2) mode=previous;
        } else mode=mode==2?previous:2;
        R8(0x4c4+g)=mode;R8(0x504+g)=mode!=2;
        if(mode==2) R8(0x3da)&=~(1u<<g);else R8(0x3da)|=1u<<g;
        V(0x0801687c)();
    } else if(mode!=2) {
        if(target==child(m,5)) V(0x08035fc8)(R32(0x16d0+8*g),4,R32(0x9dc));
        else if(target==child(m,6)) V(0x08035fc8)(R32(0x16a8+8*g),4,R32(0x9dc));
    }
    /* SET/tapping the number never changes encoder purpose. Native +/- clears
     * list selection, so restore the editor selection after those callbacks. */
    editor_select();V(0x08036ab0)(R32(0x9e8),1);
    V(0x08016cf4)();group_refresh();
}
static void group_slider(U e) {
    U m=group_modal();if(!m)return;
    U code=F(0x08035f3c)(e);stock_activity(code,root());
    if(code!=0x1c)return;
    U g=group_index(),mode=R8(0x4c4+g),slider=child(m,7);
    if(!blocked() && mode!=2) {
        U n=F(0x080300cc)(slider);
        if(mode==1) {
            if(R8(0x5a)) {n=n>24?24:n;n=(n/3)*10+(n%3==1?3:n%3==2?7:0);}
            R8(0x4d0+g)=80-(n>80?80:n);
        }
        else R8(0x4ef+g)=F(0x0804de50)(n>18?18:n);
        editor_select();V(0x08016cf4)();
    }
    USER(child(m,2))=0;group_refresh();
}
static U group_button(U m,int x,int y,U w,U h,U font,const char *text) {
    U b=F(0x0804579c)(m,1,x,y,w,h,1);
    V(0x0803e830)(b,10,0);
    V(0x0803e6e6)(b,F(0x080311b4)(0x282828),0);
    V(0x0803e708)(b,F(0x080311b4)(0xfd9f0a),5);
    label(b,9,0,0,font,0xcbcbcb,text);
    V(0x0803a03c)(b,(U)group_action,0,0);
    return b;
}
static void group_open(U g) {
    U r=root();remember(g);
    V(0x0801bf44)();V(0x08036c80)(R32(0x9e8));
    U m=F(0x0804591c)(r,2,0,0,480,360);
    USER(r)=m;USER(m)=GROUP_TAG|g;
    V(0x0803e830)(m,0,0);V(0x0803e72a)(m,0,0);
    V(0x0803e6e6)(m,F(0x08031014)(),0);V(0x0803a0da)(m,0x4000);
    const char *names[]={"M","A","B","C","D"};
    label(m,1,20,14,0x0806adbc,0xcbcbcb,names[g]);
    U back=group_button(m,402,0,78,52,0x08079bc8,(const char*)0x08049448);
    U field=group_button(m,92,66,296,126,0x0806a4b8,"");
    label(field,9,0,0,0x080614fc,0xcbcbcb,"");
    label(field,9,0,0,0x080bbd4c,0xcbcbcb,"");
    label(field,9,0,0,0x08062198,0xcbcbcb,"");
    group_button(m,20,275,270,65,0x0805fd1c,"");
    U pause=group_button(m,304,275,156,65,0x0805fd1c,"");
    for(U i=0;i<2;i++) {
        U line=F(0x0804591c)(pause,9,i?8:-8,0,5,24);
        V(0x0803e830)(line,2,0);V(0x0803e72a)(line,0,0);
        V(0x0803e6e6)(line,F(0x080311b4)(0xcbcbcb),0);V(0x0803aa02)(line,2);
    }
    U minus=group_button(m,8,87,84,84,0x0806e700,"\xee\x9a\x86");
    U plus=group_button(m,388,87,84,84,0x0806e700,"\xee\x9a\x85");
    U plain[]={back,field,minus,plus};
    for(U i=0;i<4;i++) {
        V(0x0803e6e6)(plain[i],F(0x08031014)(),0);
        V(0x0803e708)(plain[i],F(0x08031014)(),0);
        V(0x0803e708)(plain[i],F(0x08031014)(),5);
    }
    U slider=F(0x08045be0)(m,1,32,186,416,48);
    V(0x0803a03c)(slider,(U)group_slider,0,0);
    U bar=F(0x0802ff8c)(slider);
    V(0x0803e3f4)(bar,416,8);V(0x0803a212)(bar,9,0,0);
    V(0x0803aa02)(bar,2);
    for(U part=0;part<=0x20000;part+=0x20000) V(0x0803e830)(bar,3,part);
    V(0x0803e6e6)(bar,F(0x080311b4)(0x525252),0);
    V(0x0803e6fe)(bar,255,0);
    group_focus();group_refresh();
}
static void group_tap(U e) {
    U target=F(0x08035f44)(e),code=F(0x08035f3c)(e);
    /* Bubble events from +/- never become row taps. */
    if(F(0x08035fb4)(e)!=target)return;
    U g=0;for(;g<5;g++)if(target==R32(0x15b8+4*g)
        ||target==R32(0x15cc+4*g)||target==R32(0x162c+28*g))break;
    if(g==5)return;
    remember(g);
    if(F(0x08035f68)(e)!=R32(0x9dc))return;
    short point[2];V(0x08037eac)(R32(0x9dc),point);
    U x=(U)point[0]&511,y=(U)point[1]&511,state=USER(target);
    if(code==1) {USER(target)=0x80000000u|x|(y<<9);return;}
    if(!(state&0x80000000u))return;
    int dx=(int)x-(int)(state&511),dy=(int)y-(int)((state>>9)&511);
    if(code==3 || code==5 || code==6 || code==9 || dx>8 || dx< -8 || dy>8 || dy< -8)
        USER(target)=state|=0x40000000u;
    if(code!=4)return;
    USER(target)=0;
    if(!(state&0x40000000u) && !blocked() && root() && R8(0x59f)==1
        && !owns_modal() && !group_modal() && !valid(R32(0x17a4)))group_open(g);
}
