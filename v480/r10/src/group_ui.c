/* V480F V1.03 only. R10 interaction port to the native 320 x 240 LVGL UI.
 * Uses exact V480 addresses; firing and radio protocol implementations unchanged. */
typedef unsigned int U; typedef unsigned char B;
#define R8(o) (*(volatile B *)(0x20000000u+(o)))
#define R32(o) (*(volatile U *)(0x20000000u+(o)))
#define USER(o) (*(volatile U *)((o)+0x10))
#define F(a) ((U (*)())((a)|1u))
#define V(a) ((void (*)())((a)|1u))
extern void stock_sender(void),stock_focus(void),stock_tick(void),stock_page(U,U),stock_sender_event(U);
extern void stock_save(void);
static U group_modal(void);static void group_close(void),group_focus(void),group_refresh(void),group_tap(U);
static void receiver_refresh(void);
static U valid(U o) {return o && F(0x803d94c)(o);}
/* The stock record already owns RX group at byte 9. Request a commit from
 * its main-loop service after selection closes, only when that byte changed.
 * Keep its record comparison, wear rotation, erase and shutdown paths intact;
 * never program flash from an encoder ISR or allocate another NVM location. */
void sub_save(void) {
    U g=R8(0x55b);
    if(R8(0x350)==4 && g>=1 && g<=5 && g!=R8(0xff5)
       && !R32(0x18e0) && R8(0x53d)!=24)R8(0x33b)=1;
    stock_save();
}
static U parent(U o) {return o?F(0x803c318)(o):0;}
static U root(void) {U r=R32(0x664);return R8(0x5fb)==1 && R8(0x350)==3 && valid(r)?r:0;}
static void stock_activity(U c,U r) {V(0x80522c8)(c,r);}
static U label(U p,U align,int x,int y,U font,U color,const char *text) {
    return F(0x80464b8)(p,align,x,y,font,F(0x8031d40)(color),text);
}
void sub_focus(void) {if(group_modal())group_focus();else stock_focus();}
void sub_sender(void) {
    if(group_modal())group_close();
    stock_sender();
    if((R8(0x51b)&3)==2)return;
    for(U g=0;g<5;g++) {
        V(0x803abcc)(R32(0x1630+4*g),(U)group_tap,0,0);
        V(0x803abcc)(R32(0x1644+4*g),(U)group_tap,0,0);
        V(0x803abcc)(R32(0x16a4+28*g),(U)group_tap,0,0);
    }
}
void sub_tick(void) {
    if(group_modal() && (R8(0x51b)&3)==2)group_close();
    stock_tick();group_refresh();receiver_refresh();
}
void sub_page(U page,U anim) {
    if(page<12 && page!=R8(0x5fb) && !R8(0x5f5) && group_modal())group_close();
    stock_page(page,anim);
}
void sub_sender_event(U e) {
    if(!group_modal()) {stock_sender_event(e);return;}
    U c=F(0x8036ac8)(e);
    V(0x802c152)(c,0x200005fe,0x2a,0);
    if(c==0xc && F(0x8038a14)(F(0x8038a08)())==2) {
        if(!R8(0x5fe))group_close();R8(0x5fe)=0;
    }
}
/* LVGL v8 object user_data is the verified word at +0x10. The root owns
 * the editor pointer; the modal owns its controls. No new global RAM. */
#define GROUP_TAG 0x563a0000u
#define GROUP_MASK 0xffff0000u
/* Children: title, back, value (four native labels), mode, pause, -, +,
 * transparent slider (with a visible native bar as its first child). */
static U child(U obj,U i) {return F(0x803c094)(obj,i);}
static U group_modal(void) {
    U r=root();
    if(!r || R8(0x5fb)!=1) return 0;
    U m=USER(r);
    return valid(m) && parent(m)==r && (USER(m)&GROUP_MASK)==GROUP_TAG
        && (USER(m)&255)<5 ? m : 0;
}
static U group_index(void) {return USER(group_modal())&255;}
static U blocked(void) {
    return R8(0x5f5)||R8(0x5f6)||R8(0x5a3)||R8(0x3af)!=1
        ||R8(0x7ae)||R8(0x7b0)||R8(0x7b1)||(R8(0x51b)&3)==2;
}
static U remembered(U g) {
    U word=USER(R32(0x1694+28*g));
    return (word&GROUP_MASK)==GROUP_TAG ? (word&1) : 0;
}
static void remember(U g) {
    if(R8(0x51c+g)<2) USER(R32(0x1694+28*g))=GROUP_TAG|R8(0x51c+g);
}
/* IRQ-safe scope test: read owned handles only, no LVGL traversal/allocation.
 * Cleared root user_data precedes custom editor deletion. The parent pointer
 * is the verified lv_obj_t +4 word. Guards cover page transitions. */
static U ram_object(U p) {return !(p&3) && ((p>=0x20000000u && p<0x20060000u)
        ||(p>=0x10000000u && p<0x10010000u));}
U editor_target(void) {
    if(R8(0x5fb)!=1 || R8(0x3af)!=1 || R8(0x350)!=3 || (R8(0x51b)&3)==2)return 0;
    U r=R32(0x664);if(!ram_object(r))return 0;
    U m=USER(r);
    return ram_object(m) && *(U*)(m+4)==r && (USER(m)&GROUP_MASK)==GROUP_TAG
        && (USER(m)&255)<5 ? 0x11 : 0;
}
U editor_allowed(void) {
    return !(R8(0x5a3)||R8(0x576)||R8(0x358)||R8(0x589)||R8(0x5f5)
       ||R8(0x5f6)||R8(0x18)||R8(0x7ae)||R8(0x7b0)||R8(0x7b1)
       ||(R8(0x31)&8)||(R8(0x3a)&2));
}
/* Receiver reuses the native hotshoe selectors: M writes power[RX group],
 * TTL writes the native FEC byte. Keep explicit selections (ZOOM/group/mode),
 * overlays and transitions on their original input path. Called under PRIMASK. */
U receiver_target(void) {
    if(R8(0x5fb)!=2 || R8(0x3af)!=2 || R8(0x350)!=4 || R8(0x53d)
       ||!ram_object(R32(0x668)) || R32(0x18e0) || R32(0x1bb4) || R32(0x15e4)
       ||!editor_allowed())return 0;
    U mode=R8(0x51b)&3;
    return mode==0?6:mode==1 && R8(0x55b)>=1 && R8(0x55b)<=5?2:0;
}
static void receiver_refresh(void) {
    if(R8(0x5fb)!=2 || R8(0x3af)!=2 || R8(0x350)!=4 || R8(0x5f5)
       ||!valid(R32(0x668)))return;
    U value=R32(0x1860);if(!valid(value))return;
    if((R8(0x51b)&3)!=0) {USER(value)=0;return;}
    /* Stock RX tick only tracks M/Multi values because TTL was a fixed word.
     * Track FEC in the existing label and reuse the patched native formatter. */
    U cache=0x52580000u|R8(0x543);if(USER(value)==cache)return;
    USER(value)=cache;
    V(0x801f424)(value,R32(0x1864),R32(0x1868),R32(0x186c),
        R32(0x1870),R32(0x1874),R32(0x1878),0x20000543);
}
void editor_select(void) {
    U selector=editor_target();
    if(selector==0x11)R8(0x50c)=USER(USER(R32(0x664)))&255;
    if(selector)R8(0x53d)=selector;
}
static void group_focus(void) {
    U m=group_modal();if(!m) return;
    V(0x803780c)(R32(0xa60));
    /* Only the value belongs to encoder focus. Touch owns mode/pause/back. */
    V(0x8037588)(R32(0xa60),child(m,2));
    V(0x803767c)(child(m,2));
    V(0x803763c)(R32(0xa60),1);
    editor_select();
}
static void group_refresh(void) {
    U m=group_modal();if(!m) return;
    U g=group_index(),mode=R8(0x51c+g);
    remember(g);U chosen=remembered(g);
    U field=child(m,2),cache=0x80000000u|mode|(R8(0x528+g)<<2)
        |(R8(0x547+g)<<10)|(R8(0x1368)<<18)|(R8(0x5e)<<19)|(chosen<<26);
    if(USER(field)==cache)return;
    USER(field)=cache;
    V(0x803a0b0)(child(child(m,3),0),chosen?"M":"TTL");
    U pause=child(m,4);
    V(0x803a0b0)(child(pause,0),mode==2?"OFF":"");
    for(U i=1;i<=2;i++) {
        if(mode==2)V(0x803ac6a)(child(pause,i),1);
        else V(0x803b592)(child(pause,i),1);
    }
    U value=child(field,0),numerator=child(field,1),slash=child(field,2),fraction=child(field,3);
    U slider=child(m,7),bar=child(slider,0),progress,range;
    if(chosen) {
        /* Native fraction/decimal formatter operates on this group's byte.
         * Reapply modal typography/geometry without spoofing global role/page. */
        U a=R8(0x53a),b=R8(0x53b);
        V(0x80122c4)(value,numerator,slash,fraction,0,0,0,0x20000528+g);
        R8(0x53a)=a;R8(0x53b)=b;
        V(0x803f3ec)(slash,0x808c044,0);
        V(0x803ada2)(value,9,-5,0);
        V(0x803adbe)(slash,value,0x12,-2,-2);
        V(0x803adbe)(numerator,slash,0x12,-1,0);
        V(0x803adbe)(fraction,value,0x15,3,-2);
        range=80;progress=R8(0x528+g)<=80?80-R8(0x528+g):0;
    } else {
        U a=R8(0x53a),b=R8(0x53b);
        V(0x801f424)(value,numerator,slash,fraction,0,0,0,0x20000547+g);
        R8(0x53a)=a;R8(0x53b)=b;
        /* Keep the native sign glyph: the large numeric font has no ASCII
         * plus/minus. Use the original hotshoe sign font and alignment. */
        V(0x803f3ec)(slash,0x80652d8,0);
        V(0x803ada2)(value,9,12,0);
        V(0x803adbe)(slash,value,0x11,-5,0);
        range=18;progress=F(0x800e588)(R8(0x547+g));
    }
    V(0x803f3ec)(value,0x8061cec,0);
    for(U i=0;i<4;i++)V(0x803f40a)(child(field,i),mode==2?100:255,0);
    for(U i=0;i<2;i++) {
        U o=i?bar:slider,limit=range,n=progress;
        if(!i && chosen && R8(0x5e)) {limit=24;n=(progress*3+5)/10;}
        V(0x8030c7c)(o,0,limit);V(0x8030d18)(o,n,0);
    }
    V(0x803f276)(bar,F(0x8031d88)(mode==2?0x666666:0xfd9f0a),0x20000);
}
static void group_close(void) {
    U m=group_modal();if(!m)return;
    U g=group_index();USER(root())=0;
    V(0x803b6cc)(m);
    R8(0x53d)=0;R8(0x7b6)=0;R32(0x28)=0;
    R32(0xa5c)=0;
    V(0x803763c)(R32(0xa60),0);
    sub_focus();
    if((R8(0x51b)&3)!=2 && valid(R32(0x1630+4*g)))
        V(0x803767c)(R32(0x1630+4*g));
}
static void group_action(U e) {
    U m=group_modal();if(!m)return;
    U code=F(0x8036ac8)(e),target=F(0x8036ad0)(e);
    stock_activity(code,root());
    if(code!=4 || blocked())return;
    U g=group_index(),mode=R8(0x51c+g);
    if(target==child(m,1)) {group_close();return;}
    if(target==child(m,3) || target==child(m,4)) {
        U previous=remembered(g);
        if(target==child(m,3)) {
            previous=!previous;USER(R32(0x1694+28*g))=GROUP_TAG|previous;
            if(mode!=2) mode=previous;
        } else mode=mode==2?previous:2;
        R8(0x51c+g)=mode;R8(0x55c+g)=mode!=2;
        if(mode==2) R8(0x436)&=~(1u<<g);else R8(0x436)|=1u<<g;
        V(0x80168b4)();
    } else if(mode!=2) {
        if(target==child(m,5)) V(0x8036b54)(R32(0x1748+8*g),4,R32(0xa54));
        else if(target==child(m,6)) V(0x8036b54)(R32(0x1720+8*g),4,R32(0xa54));
    }
    /* SET/tapping the number never changes encoder purpose. Native +/- clears
     * list selection, so restore the editor selection after those callbacks. */
    editor_select();V(0x803763c)(R32(0xa60),1);
    V(0x8016e14)();group_refresh();
}
static void group_slider(U e) {
    U m=group_modal();if(!m)return;
    U code=F(0x8036ac8)(e);stock_activity(code,root());
    if(code!=0x1c)return;
    U g=group_index(),mode=R8(0x51c+g),slider=child(m,7);
    if(!blocked() && mode!=2) {
        U n=F(0x8030c58)(slider);
        if(mode==1) {
            if(R8(0x5e)) {n=n>24?24:n;n=(n/3)*10+(n%3==1?3:n%3==2?7:0);}
            R8(0x528+g)=80-(n>80?80:n);
        }
        else R8(0x547+g)=F(0x804e894)(n>18?18:n);
        editor_select();V(0x8016e14)();
    }
    USER(child(m,2))=0;group_refresh();
}
static U group_button(U m,int x,int y,U w,U h,U font,const char *text) {
    U b=F(0x8046264)(m,1,x,y,w,h,1);
    V(0x803f3c0)(b,8,0);
    V(0x803f2ba)(b,0,0);
    V(0x803f276)(b,F(0x8031d40)(0x282828),0);
    V(0x803f298)(b,F(0x8031d40)(0xfd9f0a),5);
    label(b,9,0,0,font,0xcbcbcb,text);
    V(0x803abcc)(b,(U)group_action,0,0);
    return b;
}
static void group_open(U g) {
    U r=root();remember(g);
    V(0x801c1b8)();V(0x803780c)(R32(0xa60));
    U m=F(0x80463e4)(r,2,0,0,320,240);
    USER(r)=m;USER(m)=GROUP_TAG|g;
    V(0x803f3c0)(m,0,0);V(0x803f2ba)(m,0,0);
    V(0x803f276)(m,F(0x8031ba0)(),0);V(0x803ac6a)(m,0x4000);
    const char *names[]={"M","A","B","C","D"};
    if(g) {
        /* Exact RX group palette initialized by the vendor image: A/B/C/D
         * are entries 10/11/12/13, with white/black/white/black text. */
        U badge=F(0x80463e4)(m,1,12,2,44,44);
        V(0x803f3c0)(badge,5,0);V(0x803f2ba)(badge,0,0);
        U color=*(volatile unsigned short *)(0x20000770u+2*(g+9));
        V(0x803f276)(badge,color,0);V(0x803f28e)(badge,255,0);
        V(0x803b592)(badge,2);
        label(badge,9,0,0,0x80625f0,(g==2||g==4)?0x000000:0xffffff,names[g]);
    } else label(m,1,14,7,0x80625f0,0xcbcbcb,names[g]);
    U back=group_button(m,264,0,56,42,0x806c04c,"\xee\x9a\x92");
    U field=group_button(m,60,48,200,86,0x8061cec,"");
    label(field,9,0,0,0x805c8fc,0xcbcbcb,"");
    label(field,9,0,0,0x808c044,0xcbcbcb,"");
    label(field,9,0,0,0x805cf4c,0xcbcbcb,"");
    group_button(m,12,188,176,44,0x805bb74,"");
    U pause=group_button(m,200,188,108,44,0x805bb74,"");
    for(U i=0;i<2;i++) {
        U line=F(0x80463e4)(pause,9,i?6:-6,0,4,18);
        V(0x803f3c0)(line,2,0);V(0x803f2ba)(line,0,0);
        V(0x803f276)(line,F(0x8031d40)(0xcbcbcb),0);V(0x803b592)(line,2);
    }
    U minus=group_button(m,0,60,60,62,0x80652d8,"\xee\x9a\x86");
    U plus=group_button(m,260,60,60,62,0x80652d8,"\xee\x9a\x85");
    U plain[]={back,field,minus,plus};
    for(U i=0;i<4;i++) {
        V(0x803f276)(plain[i],F(0x8031ba0)(),0);
        V(0x803f298)(plain[i],F(0x8031ba0)(),0);
        V(0x803f298)(plain[i],F(0x8031ba0)(),5);
    }
    U slider=F(0x80466a8)(m,1,20,137,280,38);
    V(0x803abcc)(slider,(U)group_slider,0,0);
    U bar=F(0x8030b18)(slider);
    V(0x803ef84)(bar,280,6);V(0x803ada2)(bar,9,0,0);
    V(0x803b592)(bar,2);
    for(U part=0;part<=0x20000;part+=0x20000) V(0x803f3c0)(bar,3,part);
    V(0x803f276)(bar,F(0x8031d40)(0x525252),0);
    V(0x803f28e)(bar,255,0);
    group_focus();group_refresh();
}
static void group_tap(U e) {
    U target=F(0x8036ad0)(e),code=F(0x8036ac8)(e);
    /* Bubble events from +/- never become row taps. */
    if(F(0x8036b40)(e)!=target)return;
    U g=0;for(;g<5;g++)if(target==R32(0x1630+4*g)
        ||target==R32(0x1644+4*g)||target==R32(0x16a4+28*g))break;
    if(g==5)return;
    remember(g);
    if(F(0x8036af4)(e)!=R32(0xa54))return;
    short point[2];V(0x8038a3c)(R32(0xa54),point);
    U x=(U)point[0]&511,y=(U)point[1]&511,state=USER(target);
    if(code==1) {USER(target)=0x80000000u|x|(y<<9);return;}
    if(!(state&0x80000000u))return;
    int dx=(int)x-(int)(state&511),dy=(int)y-(int)((state>>9)&511);
    if(code==3 || code==5 || code==6 || code==9 || dx>8 || dx< -8 || dy>8 || dy< -8)
        USER(target)=state|=0x40000000u;
    if(code!=4)return;
    USER(target)=0;
    if(!(state&0x40000000u) && !blocked() && root() && R8(0x5fb)==1
        && !group_modal() && !valid(R32(0x181c)))group_open(g);
}
