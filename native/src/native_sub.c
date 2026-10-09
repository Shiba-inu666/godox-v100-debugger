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
       || R8(0x398)!=R8(0x59f) || valid(R32(0x156c))) return;
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
    if(code!=4 || owns_modal() || R8(0x599) || R8(0x59a) || R8(0x54b)
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
    R32(0x1554)=label(row,7,0,0,0x080bbbe8,0xcbcbcb,"S");
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
        R32(0x1554)=label(row,1,8,2,0x08053084,0x999999,"S");
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
void sub_sender(void) {stock_sender();build(1);}
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
void sub_tick(void) {stock_tick();sub_refresh();}
void sub_page(U page,U anim) {
    if(page<12 && page!=R8(0x59f) && !R8(0x599)) {
        U row=R32(0x1550);
        /* Two complete screens coexist during native animation. Reclaim the
         * outgoing SUB subtree before constructing the new Sender controls.
         * Globals are shared between pages, and no outgoing SUB input remains.
         * Verify ownership even for the stock Hotshoe -> Sender transition. */
        U old_sub=owns_row() || (page==1 && R8(0x59f)==0 && R8(0x33c)==0
            && valid(row) && parent(row)==R32(0x5d8));
        if(old_sub) {
            if(valid(R32(0x156c))) sub_close();
            V(0x0803ab3c)(row);
            for(U o=0x1550;o<=0x1568;o+=4) R32(o)=0;
        }
    }
    stock_page(page,anim);
}
