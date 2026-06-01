#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Natal chart — wheel (left) + full interpretation panel (right)."""
import json, math, os, subprocess, sys, argparse, shutil
from collections import Counter
from interp_data import (HOUSE_TEXTS_RU, HOUSE_TEXTS_EN, PLANET_MEANING_RU,
    PLANET_MEANING_EN, SIGN_KEYWORDS_RU, SIGN_KEYWORDS_EN,
    ASPECT_MEANING_RU, ASPECT_MEANING_EN)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.check_call([sys.executable,"-m","pip","install","pillow","-q"])
    from PIL import Image, ImageDraw, ImageFont

_ttf_dir = os.path.dirname(os.path.abspath(__file__))
for _f in os.listdir(_ttf_dir):
    if _f.endswith('.ttf.dat'):
        _s = os.path.join(_ttf_dir, _f)
        _d = _s[:-4]
        if not os.path.exists(_d):
            shutil.copy2(_s, _d)

parser = argparse.ArgumentParser()
parser.add_argument("--lang", choices=["en","ru"], default="en")
parser.add_argument("--name", default="")
parser.add_argument("date", nargs="?", default="14.12.1991")
parser.add_argument("time", nargs="?", default="18:30")
parser.add_argument("city", nargs="?", default="\u0418\u0436\u0435\u0432\u0441\u043a")
args = parser.parse_args()
RU = (args.lang == "ru")

_SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
res = subprocess.run([sys.executable, os.path.join(_SCRIPTDIR,"natal_chart_swe.py"),
    args.date, args.time, args.city, "--json"],
    capture_output=True, text=True, timeout=30, cwd=_SCRIPTDIR, encoding="utf-8")
if res.returncode != 0: print("Error:", res.stderr or res.stdout); sys.exit(1)
chart = json.loads(res.stdout)
if "error" in chart: print("Error:", chart["error"]); sys.exit(1)

ZSYM = ['\u2648','\u2649','\u264a','\u264b','\u264c','\u264d',
        '\u264e','\u264f','\u2650','\u2651','\u2652','\u2653']
ZAB  = ['AR','TA','GE','CN','LE','VI','LI','SC','SG','CP','AQ','PI']
ZEL  = [0,1,2,3,0,1,2,3,0,1,2,3]
EL_COL = [(80,30,30),(30,70,30),(70,70,30),(30,50,80)]
SIG_COL = [(200,60,60),(80,180,70),(220,190,50),(70,130,220),
           (240,170,40),(100,160,80),(180,90,180),(160,40,70),
           (90,110,210),(100,100,100),(70,170,210),(60,140,140)]
EL_RU = ['\u041e\u0433\u043e\u043d\u044c','\u0417\u0435\u043c\u043b\u044f','\u0412\u043e\u0437\u0434\u0443\u0445','\u0412\u043e\u0434\u0430']
EL_EN = ['Fire','Earth','Air','Water']
SN_RU = ['\u041e\u0432\u0435\u043d','\u0422\u0435\u043b\u0435\u0446','\u0411\u043b\u0438\u0437\u043d\u0435\u0446\u044b','\u0420\u0430\u043a',
         '\u041b\u0435\u0432','\u0414\u0435\u0432\u0430','\u0412\u0435\u0441\u044b','\u0421\u043a\u043e\u0440\u043f\u0438\u043e\u043d',
         '\u0421\u0442\u0440\u0435\u043b\u0435\u0446','\u041a\u043e\u0437\u0435\u0440\u043e\u0433','\u0412\u043e\u0434\u043e\u043b\u0435\u0439','\u0420\u044b\u0431\u044b']
SN_EN = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
PM = {
    "Sun":("SU",(255,220,50),"\u0421\u043e\u043b\u043d\u0446\u0435","Sun"),
    "Moon":("MO",(210,210,220),"\u041b\u0443\u043d\u0430","Moon"),
    "Mercury":("ME",(100,210,100),"\u041c\u0435\u0440\u043a\u0443\u0440\u0438\u0439","Mercury"),
    "Venus":("VE",(80,230,170),"\u0412\u0435\u043d\u0435\u0440\u0430","Venus"),
    "Mars":("MA",(230,70,50),"\u041c\u0430\u0440\u0441","Mars"),
    "Jupiter":("JU",(210,150,60),"\u042e\u043f\u0438\u0442\u0435\u0440","Jupiter"),
    "Saturn":("SA",(150,150,170),"\u0421\u0430\u0442\u0443\u0440\u043d","Saturn"),
    "Uranus":("UR",(100,210,230),"\u0423\u0440\u0430\u043d","Uranus"),
    "Neptune":("NE",(90,140,230),"\u041d\u0435\u043f\u0442\u0443\u043d","Neptune"),
    "Pluto":("PL",(170,80,80),"\u041f\u043b\u0443\u0442\u043e\u043d","Pluto"),
}
ROMAN = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']

def zod(d):
    d=float(d)%360; i=int(d//30); s=d-i*30
    return i,ZAB[i],int(s),int((s-int(s))*60)
def aof(d): return math.radians(90.0-float(d))
def ppos(cx,cy,r,d):
    a=aof(d); return cx+r*math.cos(a),cy-r*math.sin(a)

_SYM = os.path.join(_SCRIPTDIR,"seguisym.ttf")
_TXT = os.path.join(_SCRIPTDIR,"segoeuisl.ttf")
_FC = {}
def fnt(size, sym=False):
    k=(size,sym)
    if k in _FC: return _FC[k]
    fp = _SYM if sym else _TXT
    if os.path.exists(fp):
        try: _FC[k]=ImageFont.truetype(fp,size); return _FC[k]
        except: pass
    _FC[k]=ImageFont.load_default(); return _FC[k]

def is_z(ch): return '\u2648'<=ch<='\u2653'
def ch_w(ch, f):
    bb = f.getbbox(ch); return (bb[2]-bb[0]) if bb else 10

def rtext(draw, x, y, text, size, fill, cy=False):
    sf=fnt(size,sym=True); tf=fnt(size,sym=False)
    if cy:
        bb=tf.getbbox(text); y-=(bb[3]-bb[1])//2
    cx=x
    for ch in text:
        f=sf if is_z(ch) else tf
        draw.text((cx,y),ch,fill=fill,font=f)
        cx+=ch_w(ch,f)

def rcent(draw, cx, y, text, size, fill):
    sf=fnt(size,sym=True); tf=fnt(size,sym=False)
    tw=sum(ch_w(ch,sf if is_z(ch) else tf) for ch in text)
    x=cx-tw//2
    for ch in text:
        f=sf if is_z(ch) else tf
        draw.text((x,y),ch,fill=fill,font=f)
        x+=ch_w(ch,f)

planets_raw=[]
for pn,pd in chart["planets"].items():
    if pn not in PM: continue
    ab,cl,nr,ne=PM[pn]; ln=pd["lon"]; rt=pd["retro"]
    si=int(ln//30); sd=ln-si*30
    planets_raw.append({'key':pn,'abbr':ab,'nr':nr,'ne':ne,
        'lon':ln,'si':si,'sab':ZAB[si],'sym':ZSYM[si],
        'deg':int(sd),'min':int((sd-int(sd))*60),
        'retro':rt,'col':cl,'house':chart["planet_houses"].get(pn,1)})
PO=["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto"]
planets_raw.sort(key=lambda p:PO.index(p['key']) if p['key'] in PO else 99)

houses=chart["houses"]; asc_deg=chart["asc"]; mc_deg=chart["mc"]
house_data=[]
for i in range(12):
    cd=float(houses[i]); ci=int(cd//30); sd=cd-ci*30
    house_data.append({'num':i+1,'rom':ROMAN[i],'cusp_deg':cd,'si':ci,
        'sab':ZAB[ci],'sym':ZSYM[ci],'deg':int(sd),'min':int((sd-int(sd))*60),
        'pls':[p for p in planets_raw if p['house']==i+1]})

asp_data=[]
for a in chart["aspects"]:
    p1=PM.get(a["p1"],('??',))[0]; p2=PM.get(a["p2"],('??',))[0]
    at=a["type"]
    cm={'conjunction':(200,200,200),'sextile':(100,180,240),'square':(220,80,80),
        'trine':(80,220,80),'quincunx':(180,160,60),'opposition':(240,140,40),
        'semisextile':(150,150,100),'semisquare':(150,100,100)}
    asp_data.append({'p1':p1,'p2':p2,'type':at,'col':cm.get(at,(150,150,150))})

asc_z=zod(asc_deg); mc_z=zod(mc_deg)
SN = SN_RU if RU else SN_EN

T = {
    "asc":"\u0410\u0421\u0426" if RU else "ASC",
    "mc":"\u041c\u0421" if RU else "MC",
    "pl":"\u041f\u041b\u0410\u041d\u0415\u0422\u042b" if RU else "PLANETS",
    "asp":"\u0410\u0421\u041f\u0415\u041a\u0422\u042b" if RU else "ASPECTS",
    "el":"\u0421\u0442\u0438\u0445\u0438\u0438" if RU else "Elements",
    "info":"\u041d\u0410\u0422\u0410\u041b\u042c\u041d\u0410\u042f \u041a\u0410\u0420\u0422\u0410" if RU else "NATAL CHART",
    "interp":"\u0422\u041e\u041b\u041a\u041e\u0412\u0410\u041d\u0418\u0415" if RU else "INTERPRETATION",
    "houses":"\u0414\u041e\u041c\u0410" if RU else "HOUSES",
    "aspects_blk":"\u0410\u0421\u041f\u0415\u041a\u0422\u042b \u0418 \u041a\u041e\u041d\u0424\u0418\u0413\u0423\u0420\u0410\u0426\u0418\u0418" if RU else "ASPECTS & CONFIGURATIONS",
    "cj":"\u0421\u043e\u0435\u0434" if RU else "Conj",
    "sx":"\u0421\u0435\u043a\u0441\u0442" if RU else "Sext",
    "sq":"\u041a\u0432\u0430\u0434\u0440" if RU else "Sqr",
    "tr":"\u0422\u0440\u0438\u043d" if RU else "Trine",
    "qn":"\u041a\u0432\u0438\u043d\u043a" if RU else "Quinc",
    "op":"\u041e\u043f\u043f\u043e\u0437" if RU else "Opp",
    "no_planets":"\u043d\u0435\u0442 \u043f\u043b\u0430\u043d\u0435\u0442" if RU else "no planets",
    "stellium":"\u0421\u0422\u0415\u041b\u041b\u0418\u0423\u041c" if RU else "STELLIUM",
    "dominant_el":"\u0414\u043e\u043c\u0438\u043d\u0438\u0440\u0443\u044e\u0449\u0430\u044f \u0441\u0442\u0438\u0445\u0438\u044f" if RU else "Dominant element",
    "retro_mark":" \u211e" if RU else " R",
}

# ═══ LAYOUT ═══
WHEEL = 2160
PANEL_W = 3600
TOT_W = WHEEL + PANEL_W
TOT_H = TOT_W // 2  # 2880

img = Image.new('RGB',(TOT_W,TOT_H),(8,8,20))
dw = ImageDraw.Draw(img)
FS=19; FM=22; FL=26; FH=20; FZL=38
HM = HOUSE_TEXTS_RU if RU else HOUSE_TEXTS_EN
PMean = PLANET_MEANING_RU if RU else PLANET_MEANING_EN
SK = SIGN_KEYWORDS_RU if RU else SIGN_KEYWORDS_EN
AM = ASPECT_MEANING_RU if RU else ASPECT_MEANING_EN

# ═══════════════════════════════════════════════════════════
# LEFT WHEEL
# ═══════════════════════════════════════════════════════════
cx=WHEEL//2; cy=TOT_H//2
RO=960; RS=888; RH=816; RP=648; RI=432

dw.ellipse((cx-RO,cy-RO,cx+RO,cy+RO),fill=(16,16,36),outline=(80,80,130),width=4)
asc_sign_idx = int(asc_deg // 30) % 12
sector_start = asc_sign_idx * 30
for i in range(12):
    sd = sector_start + i * 30
    ed = sector_start + (i + 1) * 30
    sign_idx = (asc_sign_idx + i) % 12
    col = EL_COL[ZEL[sign_idx]]
    pts = [(cx, cy)]
    for j in range(41):
        d = sd + (ed - sd) * j / 40
        a = math.radians(90.0 - d)
        pts.append((cx + RO * math.cos(a), cy - RO * math.sin(a)))
    dw.polygon(pts, fill=col)
dw.ellipse((cx-RO,cy-RO,cx+RO,cy+RO),outline=(180,180,210),width=4)

for i in range(12):
    dc = sector_start + i * 30
    ax,ay=ppos(cx,cy,RO-6,dc); bx,by=ppos(cx,cy,RS-18,dc)
    dw.line([(int(ax),int(ay)),(int(bx),int(by))],fill=(160,160,190),width=2)
    mid_dc = sector_start + i * 30 + 15
    si = (asc_sign_idx + i) % 12
    lx,ly=ppos(cx,cy,RS,mid_dc)
    rcent(dw,int(lx),int(ly),ZSYM[si],FZL,SIG_COL[si])

for i in range(12):
    dc=float(houses[i])
    ax,ay=ppos(cx,cy,RI+12,dc); bx,by=ppos(cx,cy,RH,dc)
    dw.line([(int(ax),int(ay)),(int(bx),int(by))],fill=(90,130,190),width=2)
    nc=float(houses[(i+1)%12])
    mid=dc+(nc-dc)/2 if nc>dc else (dc+(nc+360-dc)/2)%360
    hnx,hny=ppos(cx,cy,RH+48,mid)
    rcent(dw,int(hnx),int(hny),ROMAN[i],FH,(140,170,210))

for lbl,dg,col in [(T["asc"],asc_deg,(255,255,120)),(T["mc"],mc_deg,(255,200,100))]:
    ax,ay=ppos(cx,cy,RI,dg); bx,by=ppos(cx,cy,RO-4,dg)
    dw.line([(int(ax),int(ay)),(int(bx),int(by))],fill=col,width=6)
    lx,ly=ppos(cx,cy,RO+36,dg)
    rcent(dw,int(lx),int(ly),lbl,FM,col)

dw.ellipse((cx-RI,cy-RI,cx+RI,cy+RI),outline=(90,90,140),width=2)

pp_main=[]
for p in planets_raw:
    px,py=ppos(cx,cy,RP,p['lon']); pp_main.append((p,int(px),int(py)))
    r=18
    dw.ellipse((int(px)-r,int(py)-r,int(px)+r,int(py)+r),fill=p['col'],outline=(255,255,255),width=3)
    rcent(dw,int(px),int(py)-42,p['abbr']+('(R)' if p['retro'] else ''),FS-2,p['col'])

for a in asp_data:
    d1=next(((pl,px,py) for pl,px,py in pp_main if pl['abbr']==a['p1']),None)
    d2=next(((pl,px,py) for pl,px,py in pp_main if pl['abbr']==a['p2']),None)
    if d1 and d2: dw.line([(d1[1],d1[2]),(d2[1],d2[2])],fill=a['col'],width=2)

# Legends below wheel
LEG=cy+RO+20
plx=30; ply=LEG; prh=30; pw=310
lb=ply+(len(planets_raw)+1)*prh+14
dw.rectangle((plx-10,ply-10,plx+pw,lb),fill=(12,12,28),outline=(60,60,100),width=2)
rtext(dw,plx,ply,T["pl"],FM-2,(200,200,220))
for idx,p in enumerate(planets_raw):
    ry=ply+prh+idx*prh
    nm=p['nr'] if RU else p['ne']
    lbl="%s  %-3s  %s"%(p['sym'],p['abbr'],nm)
    if p['retro']: lbl+=' R'
    rtext(dw,plx,ry,lbl,FS-2,p['col'])

elx=plx+pw+30; ely=LEG; eeh=30; ew=230
elb=ely+5*eeh+14
dw.rectangle((elx-10,ely-10,elx+ew,elb),fill=(12,12,28),outline=(60,60,100),width=2)
rtext(dw,elx,ely,T["el"],FM-2,(200,200,220))
for ei in range(4):
    ry=ely+eeh+ei*eeh
    enm=EL_RU[ei] if RU else EL_EN[ei]
    dw.rectangle((elx,ry+4,elx+22,ry+24),fill=EL_COL[ei])
    rtext(dw,elx+30,ry,enm,FS-2,(200,200,200))

asx=elx+ew+30; asy=LEG; ash=30; asw=190
asb=asy+7*ash+14
dw.rectangle((asx-10,asy-10,asx+asw,asb),fill=(12,12,28),outline=(60,60,100),width=2)
rtext(dw,asx,asy,T["asp"],FM-2,(200,200,220))
ail=[((200,200,200),T["cj"]),((100,180,240),T["sx"]),((220,80,80),T["sq"]),
     ((80,220,80),T["tr"]),((180,160,60),T["qn"]),((240,140,40),T["op"])]
for ai,(ac,al) in enumerate(ail):
    ry=asy+ash+ai*ash
    dw.rectangle((asx,ry+4,asx+22,ry+24),fill=ac)
    rtext(dw,asx+30,ry,al,FS-2,ac)

dw.line([(WHEEL,0),(WHEEL,TOT_H)],fill=(80,80,120),width=3)

# ═══════════════════════════════════════════════════════════
# RIGHT PANEL — Full interpretation
# ═══════════════════════════════════════════════════════════
PX = WHEEL + 30
PY = 20
PW = PANEL_W - 50
LH = 22  # line height for body text

def wrap_text(text, font, max_w):
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        bb = font.getbbox(test)
        tw = (bb[2]-bb[0]) if bb else 0
        if tw <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_section(title, lines, title_clr, body_clr, is_header=False):
    global PY
    _fs = FM if is_header else FS
    rtext(dw,PX,PY,title,_fs,title_clr)
    PY += _fs + 6
    _tf = fnt(FS-1, sym=False)
    for line in lines:
        wrapped = wrap_text(line, _tf, PW-10)
        for wl in wrapped:
            rtext(dw,PX+5,PY,wl,FS-1,body_clr)
            PY += LH
    if is_header:
        PY += 14
    else:
        PY += 8

def divider():
    global PY
    dw.line([(PX,PY),(PX+PW,PY)],fill=(60,60,100),width=1)
    PY += 10

# ── Title + Name ──
rcent(dw,PX+PW//2,PY,T["info"],FL+6,(255,255,200))
PY += FL + 18
if args.name:
    rcent(dw,PX+PW//2,PY,args.name,FM+2,(200,200,240))
    PY += FM + 14

# ── Essential data ──
rtext(dw,PX,PY,chart["date"]+"  "+chart["time"],FS+1,(200,200,220)); PY+=26
rtext(dw,PX,PY,chart["city_full"],FS+1,(200,200,220)); PY+=26
rtext(dw,PX,PY,"%.4fN  %.4fE"%(chart["lat"],chart["lon"]),FS,(170,170,190)); PY+=26
rtext(dw,PX,PY,chart["tz"],FS,(170,170,190)); PY+=28
asc_s = "%s: %s%s %d\u00b0%d'"%(T["asc"],ZSYM[asc_z[0]],asc_z[1],asc_z[2],asc_z[3])
mc_s = "%s: %s%s %d\u00b0%d'"%(T["mc"],ZSYM[mc_z[0]],mc_z[1],mc_z[2],mc_z[3])
rtext(dw,PX,PY,asc_s,FS+1,(255,255,120)); PY+=26
rtext(dw,PX,PY,mc_s,FS+1,(255,200,100)); PY+=30
divider()

# ═══ CORE INTERPRETATION ═══
rtext(dw,PX,PY,T["interp"],FL,(255,220,100)); PY+=FL+8

# Sun
sun = next((p for p in planets_raw if p['key']=='Sun'), None)
if sun:
    _sn = SN[sun['si']]
    sm = PMean.get('Sun','')
    _sk = SK.get(sun['sab'],'')
    if RU:
        lines = [
            "\u0421\u043e\u043b\u043d\u0446\u0435 \u0432 %s (%d\u00b0%d')  \u2014  %s"%(_sn,sun['deg'],sun['min'],_sk),
            sm,
            "\u0421\u043e\u043b\u043d\u0446\u0435 \u0432 %s \u0434\u0430\u0451\u0442 \u0444\u043e\u043a\u0443\u0441 \u043d\u0430 %s \u0438 \u0441\u043e\u0437\u043d\u0430\u0442\u0435\u043b\u044c\u043d\u0443\u044e \u0441\u0430\u043c\u043e\u043e\u0446\u0435\u043d\u043a\u0443."%(_sn, _sk[:40].lower()),
        ]
    else:
        lines = [
            "Sun in %s (%d\u00b0%d')  \u2014  %s"%(_sn,sun['deg'],sun['min'],_sk),
            sm,
            "The Sun in %s gives focus on %s and conscious self-evaluation."%(_sn, _sk[:40].lower()),
        ]
    draw_section("", lines, (255,220,100), (220,210,180))

# Moon
moon = next((p for p in planets_raw if p['key']=='Moon'), None)
if moon:
    sn = SN[moon['si']]
    mm = PMean.get('Moon','')
    sk = SK.get(moon['sab'],'')
    if RU:
        lines = [
            "\u041b\u0443\u043d\u0430 \u0432 %s (%d\u00b0%d')  \u2014  %s"%(sn,moon['deg'],moon['min'],sk),
            mm,
            "\u041b\u0443\u043d\u0430 \u0432 %s \u0433\u043e\u0432\u043e\u0440\u0438\u0442 \u043e \u0433\u043b\u0443\u0431\u0438\u043d\u043d\u044b\u0445 \u043f\u043e\u0442\u0440\u0435\u0431\u043d\u043e\u0441\u0442\u044f\u0445 \u0432 %s."%(sn, sk[:40].lower()),
        ]
    else:
        lines = [
            "Moon in %s (%d\u00b0%d')  \u2014  %s"%(sn,moon['deg'],moon['min'],sk),
            mm,
            "The Moon in %s speaks of deep needs in %s."%(sn, sk[:40].lower()),
        ]
    draw_section("", lines, (200,200,255), (200,210,220))

# ASC
asc_sn = SN[asc_z[0]]
asc_sk = SK.get(ZAB[asc_z[0]],'')
if RU:
    lines = [
        "\u0410\u0441\u0446\u0435\u043d\u0434\u0435\u043d\u0442: %s (%d\u00b0%d')  \u2014  %s"%(asc_sn,asc_z[2],asc_z[3],asc_sk),
        "\u041c\u0430\u0441\u043a\u0430, \u043a\u043e\u0442\u043e\u0440\u0443\u044e \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0435\u0442 \u043c\u0438\u0440\u0443. \u041f\u0435\u0440\u0432\u043e\u0435 \u0432\u043f\u0435\u0447\u0430\u0442\u043b\u0435\u043d\u0438\u0435 \u0438 \u0441\u043f\u043e\u0441\u043e\u0431\u044b \u0430\u0434\u0430\u043f\u0442\u0430\u0446\u0438\u0438.",
    ]
else:
    lines = [
        "Ascendant: %s (%d\u00b0%d')  \u2014  %s"%(asc_sn,asc_z[2],asc_z[3],asc_sk),
        "The mask the person shows to the world. First impression and adaptation strategies.",
    ]
draw_section("", lines, (255,255,120), (220,220,200))

# Dominant element
el_count = [0,0,0,0]
for p in planets_raw:
    el_count[ZEL[p['si']]] += 1
dom_el = max(range(4), key=lambda i: el_count[i])
el_names = EL_RU if RU else EL_EN
el_desc_ru = ["\u043d\u0430\u043f\u043e\u0440\u0438\u0441\u0442\u043e\u0441\u044c \u0438 \u0438\u043d\u0438\u0446\u0438\u0430\u0442\u0438\u0432\u0430","\u043f\u0440\u0430\u043a\u0442\u0438\u0447\u043d\u043e\u0441\u0442\u044c \u0438 \u0441\u0442\u0430\u0431\u0438\u043b\u044c\u043d\u043e\u0441\u0442\u044c","\u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442 \u0438 \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u044f","\u044d\u043c\u043e\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c \u0438 \u0438\u043d\u0442\u0443\u0438\u0446\u0438\u044f"]
el_desc_en = ["assertiveness and initiative","practicality and stability","intellect and communication","emotionality and intuition"]
dom_line = "%s: %s (%d \u043f\u043b\u0430\u043d\u0435\u0442) \u2014 %s"%(T["dominant_el"],el_names[dom_el],el_count[dom_el],el_desc_ru[dom_el] if RU else el_desc_en[dom_el])
draw_section(dom_line, [], (180,255,180), (200,220,200))

# Stelliums
sign_counts = Counter(p['si'] for p in planets_raw)
house_counts = Counter(p['house'] for p in planets_raw)
stellium_lines = []
for si, cnt in sign_counts.items():
    if cnt >= 3:
        pls = [p for p in planets_raw if p['si']==si]
        names = ['%s%s'%(p['abbr'],'\u211e' if p['retro'] else '') for p in pls]
        stellium_lines.append("%s \u0432 %s (%d \u043f\u043b\u0430\u043d\u0435\u0442): %s"%(T["stellium"],SN[si],cnt,', '.join(names)))
for hi, cnt in house_counts.items():
    if cnt >= 3:
        pls = [p for p in planets_raw if p['house']==hi]
        names = ['%s%s'%(p['abbr'],'\u211e' if p['retro'] else '') for p in pls]
        stellium_lines.append("%s \u0432 %s \u0434\u043e\u043c\u0435 (%d \u043f\u043b\u0430\u043d\u0435\u0442): %s"%(T["stellium"],ROMAN[hi-1],cnt,', '.join(names)))
if stellium_lines:
    draw_section("", stellium_lines, (255,180,255), (220,200,220))

# Retrograde planets
retro = [p for p in planets_raw if p['retro']]
if retro:
    rlines = []
    for p in retro:
        if RU:
            rlines.append("%s %s%s %d\u00b0%d' \u0432 %s \u0434\u043e\u043c\u0435 (%s) \u2014 \u044d\u043d\u0435\u0440\u0433\u0438\u044f \u043f\u043e\u0432\u0435\u0440\u043d\u0443\u0442\u0430 \u0432\u043d\u0443\u0442\u044c, \u043a\u0430\u0440\u043c\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u0443\u0440\u043e\u043a\u0438" % (
                p['sym'], p['nr'],'\u211e',p['deg'],p['min'],ROMAN[p['house']-1], p['key']))
        else:
            rlines.append("%s %s%s %d\u00b0%d' in House %s (%s) \u2014 internalized energy, karmic lessons" % (
                p['sym'], p['ne'],' R',p['deg'],p['min'],ROMAN[p['house']-1], p['key']))
    draw_section("", rlines, (180,180,255), (200,200,220))

divider()

# ═══ ASPECTS ═══
rtext(dw,PX,PY,T["aspects_blk"],FL,(255,200,100)); PY+=FL+6

# Build aspect planet name lookup
def planet_name(pkey):
    p = next((x for x in planets_raw if x['key']==pkey), None)
    if not p: return pkey
    return p['nr'] if RU else p['ne']

for a in asp_data:
    p1n = planet_name(a['p1']); p2n = planet_name(a['p2'])
    a_type = a['type']
    a_mean = AM.get(a_type, a_type)
    orb_info = ""
    # Find orb from chart data
    for ca in chart.get("aspects",[]):
        if PM.get(ca.get("p1",""),(""))[0]==a['p1'] and PM.get(ca.get("p2",""),(""))[0]==a['p2']:
            orb_info = " (orb: %.1f\u00b0)"%ca.get("orb",0)
            break
    line = "%s \u2014 %s%s : %s"%(p1n, p2n, orb_info, a_mean)
    rtext(dw,PX+5,PY,line,FS-1,a['col'])
    PY += LH + 2
    if PY > TOT_H - 60: break

divider()

# ═══ HOUSES ═══
rtext(dw,PX,PY,T["houses"],FL,(255,220,100)); PY+=FL+6

for i, ht in enumerate(HM):
    if PY > TOT_H - 80: break
    hd = house_data[i]
    pls_in_house = hd['pls']

    cusp_str = "%s %s %d\u00b0%d'"%(hd['sym'], hd['sab'], hd['deg'], hd['min'])
    title_str = "%s  [%s]"%(ht['title'], cusp_str)
    rtext(dw,PX,PY,title_str,FS,(180,200,255))
    PY += 22

    tf = fnt(FS-1, sym=False)
    for body_line in ht['body']:
        wrapped = wrap_text(body_line, tf, PW-15)
        for wl in wrapped:
            rtext(dw,PX+8,PY,wl,FS-1,(180,180,200))
            PY += LH
        if PY > TOT_H - 60: break

    if pls_in_house and PY < TOT_H - 60:
        for p in pls_in_house:
            pnm = p['nr'] if RU else p['ne']
            pmean = PMean.get(p['key'],'')
            ppos_str = "%s %s %d\u00b0%d'"%(p['sym'],p['sab'],p['deg'],p['min'])
            retro_s = '\u211e' if p['retro'] else ''
            if RU:
                planet_line = "  \u25e6 %s (%s%s %s) \u0432 %s \u0434\u043e\u043c\u0435" % (pnm, p['abbr'], retro_s, ppos_str, ROMAN[p['house']-1])
                meaning_line = "    \u25e6 \u0417\u043d\u0430\u0447\u0435\u043d\u0438\u0435: %s. %s \u0432 \u044d\u0442\u043e\u043c \u0434\u043e\u043c\u0435 \u043f\u0440\u043e\u044f\u0432\u043b\u044f\u0435\u0442 %s" % (pmean, pnm, ht['title'].split('—')[1].strip()[:30])
            else:
                planet_line = "  \u25e6 %s (%s%s %s) in House %s" % (pnm, p['abbr'], ' R' if p['retro'] else '', ppos_str, ROMAN[p['house']-1])
                meaning_line = "    \u25e6 Meaning: %s. %s expresses %s in this house" % (pmean, pnm, ht['title'].split('—')[1].strip()[:30])
            rtext(dw,PX+8,PY,planet_line,FS-1,p['col'])
            PY += LH
            if PY < TOT_H - 40:
                rtext(dw,PX+12,PY,meaning_line,FS-2,(160,160,180))
                PY += LH
                if PY > TOT_H - 60: break
    elif PY < TOT_H - 40:
        rtext(dw,PX+8,PY,"  \u25e6 "+T["no_planets"],FS-1,(130,130,150))
        PY += LH

    PY += 6
    # Divider every 3 houses
    if (i+1) % 3 == 0 and i < 11 and PY < TOT_H - 100:
        dw.line([(PX,PY),(PX+PW,PY)],fill=(40,40,70),width=1)
        PY += 8

# ── ClawHub link ──
if PY < TOT_H - 50:
    PY += 10
    _url = "https://clawhub.ai/dynamicsalex/astro-natal-chart"
    rcent(dw,PX+PW//2,PY,_url,FS-2,(80,80,120))

_name_clean = args.name.replace(" ", "_") if args.name else "chart"
import sys
_out = os.path.join(r"C:\Users\alter\.openclaw\workspace", "%s_full_natal_%s.png" % (_name_clean, "ru" if RU else "en"))
img.save(_out, "PNG")
if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
print("Saved:", _out, img.size)
