#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brain.py — الدماغ الذكي (نسخة مُصلَحة — جولة 3: تزامن + has_ob + per_symbol)
يحفظ الصفقات ويتعلم منها فعلياً | سعة 100,000 صفقة

═══════════════════════════════════════════════════════════
تحديث الجولة الثالثة (مطابقة لأحدث app.py):
═══════════════════════════════════════════════════════════
A) قفل مزامنة (threading.Lock): app.py يشغّل عدة Threads متوازية تكتب/
   تقرأ من نفس ملفي trades_db.json و open_trades.json في آن واحد
   (مراقبة الصفقات كل 30 ثانية، التعلم كل ساعة، فحص يدوي/آلي، استقبال
   تيليجرام). بدون قفل، كتابتان متزامنتان على نفس الملف قد تُتلفان
   الـ JSON بالكامل (Race Condition حقيقية). أُضيف قفلان منفصلان:
   واحد لملف الصفقات (_DB_LOCK) وواحد للصفقات المفتوحة (_OPEN_LOCK).

B) has_ob لم يعد إلزامياً دائماً True في app.py الحالي (أصبح True/False
   فعلياً حسب وجود Order Block على 1H) — لذا أُعيد استخدامه في
   score_bonus() و _update_fail() كميزة تمييزية حقيقية، بعد أن كان قد
   استُبعد خطأً في الجولة السابقة على افتراض أنه إلزامي دائماً.

C) أُضيف حساب per_symbol فعلياً في learn() (معدل نجاح لكل رمز على حدة)
   — كان app.py يحاول قراءة learned["per_symbol"] لترتيب أولوية فحص
   الرموز، لكنه لم يكن موجوداً إطلاقاً في هذا الملف (كود ميت من طرف
   واحد). الآن يُحسب ويُخزَّن فعلياً.

═══════════════════════════════════════════════════════════
تحديث الجولة الثانية (بالتزامن مع إصلاح app.py):
═══════════════════════════════════════════════════════════
app.py آنذاك جعل has_ob و has_liq_sweep إلزاميين دائماً (True) على
فريم الساعة، بالإضافة إلى fvg_retested الذي كان إلزامياً أصلاً. لذا
أُزيلا من _update_fail و score_bonus لتفادي إعادة نفس مشكلة "الكود
الميت". has_liq_sweep و fvg_retested ما زالا إلزاميين دائماً في app.py
الحالي (لا تُقاس التفرقة فيهما أصلاً)، لذا بقيا مستبعدين بحق. أما
has_ob فقد تغيّر — انظر (B) أعلاه.

═══════════════════════════════════════════════════════════
التعديلات الجوهرية عن النسخة الأصلية (ولماذا):
═══════════════════════════════════════════════════════════
1) score_bonus(): المقارنة أصبحت نسبية لخط الأساس (baseline) وهو معدل
   النجاح العام الفعلي، فأي ميزة أفضل من المتوسط تُكافأ فوراً وأي ميزة
   أسوأ منه تُعاقَب فوراً، بغض النظر عن مستوى الأداء العام.
2) _update_fail(): تتبّع فقط الميزات "الاختيارية" التي تتفاوت فعلياً
   بين الصفقات المُرسلة.
3) استخدام direction_wr و ideal_rsi_win اللذين كانا محسوبين ومُهمَلين
   تماماً — أصبحا يؤثران فعلياً على الثقة النهائية.
4) should_learn(): فاصل ساعة واحدة + تعلّم فوري إجباري إذا تراكمت 15
   صفقة مغلقة جديدة منذ آخر تعلّم.
5) min_trades للتعلّم = 20 — عيّنة أصغر غير موثوقة إحصائياً.
"""

import json, os, time, gzip, shutil, threading
from datetime import datetime

BASE     = os.path.dirname(os.path.abspath(__file__))
DB_FILE  = os.path.join(BASE, "trades_db.json")
OP_FILE  = os.path.join(BASE, "open_trades.json")
MAX_T    = 100_000
MIN_TRADES_TO_LEARN = 20     # عيّنة أصغر غير موثوقة إحصائياً
LEARN_INTERVAL_SEC  = 3600   # تعلّم كل ساعة

# إصلاح (A): قفلان منفصلان لمنع تلف الملفات عند الكتابة المتزامنة من
# عدة Threads (مراقبة الصفقات + التعلم الدوري + الفحص اليدوي/الآلي).
_DB_LOCK   = threading.Lock()
_OPEN_LOCK = threading.Lock()

# ── قاعدة البيانات ─────────────────────────

def _empty():
    return {"trades":[], "learned":{}, "last_learn":0,
            "stats":{"wins":0,"losses":0,"total":0},
            "fail_patterns":{}, "backtest":{}}

def _load():
    if not os.path.exists(DB_FILE): return _empty()
    try:
        with open(DB_FILE,"r",encoding="utf-8") as f: return json.load(f)
    except: return _empty()

def _atomic_write(path, write_func):
    """كتابة آمنة: تُكتب البيانات في ملف مؤقت أولاً، ثم يُستبدل الملف الأصلي
    دفعة واحدة (os.replace). هذا يمنع تلف trades_db.json / open_trades.json
    لو تم إيقاف العملية فجأة أثناء الكتابة (إعادة نشر، نفاد ذاكرة، إلخ) —
    فإما أن تنجح الكتابة بالكامل، أو يبقى الملف القديم سليماً كما هو."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        write_func(f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def _save(db):
    _atomic_write(DB_FILE, lambda f: json.dump(db,f,ensure_ascii=False,separators=(',',':')))
    n=len(db["trades"])
    if n>0 and n%10_000==0:
        arc=DB_FILE.replace(".json",f"_arc{n}.json.gz")
        with open(DB_FILE,"rb") as fi, gzip.open(arc,"wb") as fo:
            shutil.copyfileobj(fi,fo)

# ── حفظ صفقة ──────────────────────────────

def save_trade(signal, outcome):
    """outcome=1 ربح | outcome=0 خسارة"""
    with _DB_LOCK:
        db=_load()
        recent=db["trades"][-50:]
        for t in recent:
            if t.get("symbol")==signal.get("symbol") and \
               abs(time.time()-t.get("timestamp",0))<120:
                return None
        rec={
            "id"          : db["stats"]["total"]+1,
            "outcome"     : outcome,
            "symbol"      : signal.get("symbol",""),
            "direction"   : signal.get("direction",""),
            "entry"       : signal.get("entry",0),
            "sl"          : signal.get("sl",0),
            "tp"          : signal.get("tp",0),
            "score"       : signal.get("score",0),
            "rsi_15m"     : signal.get("rsi_15m",50),
            "trend_4h"    : signal.get("trend_4h",""),
            "trend_1h"    : signal.get("trend_1h",""),
            "session"     : signal.get("session",""),
            "in_kz"       : signal.get("in_kz",False),
            "has_ob"      : signal.get("has_ob",False),
            "has_fvg"     : signal.get("has_fvg",False),
            "fvg_retested": signal.get("fvg_retested",False),
            "has_liq_sweep":signal.get("has_liq_sweep",False),
            "sr_flip"     : signal.get("sr_flip",False),
            "has_cluster" : signal.get("has_cluster",False),
            "cvd_score"   : signal.get("cvd_score",0),
            "cor_btc"     : signal.get("cor_btc",0),
            "vol_breakout": signal.get("vol_breakout",False),
            "closed_at"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp"   : time.time()
        }
        db["trades"].append(rec)
        db["stats"]["total"]+=1
        if outcome==1: db["stats"]["wins"]+=1
        else:
            db["stats"]["losses"]+=1
            _update_fail(db,rec)
        if len(db["trades"])>MAX_T:
            db["trades"]=db["trades"][1000:]
            db["stats"]["wins"]  =sum(1 for t in db["trades"] if t["outcome"]==1)
            db["stats"]["losses"]=sum(1 for t in db["trades"] if t["outcome"]==0)
        _save(db)
        return rec

def _update_fail(db,rec):
    """
    يتتبّع فقط الميزات "الاختيارية" فعلياً في نسخة app.py الحالية.
    ملاحظة: has_liq_sweep و fvg_retested إلزاميان دائماً True في app.py
    الحالي (لا تمييز ممكن)، فيبقيان مستبعدين. أما has_ob فقد أصبح
    اختيارياً فعلياً (إصلاح B) فأُعيد تتبعه هنا.
    """
    fp=db.setdefault("fail_patterns",{})
    conds=[]
    if not rec.get("has_ob"):              conds.append("no_ob")
    if not rec.get("sr_flip"):             conds.append("no_sr_flip")
    if not rec.get("has_cluster"):         conds.append("no_cluster")
    if not rec.get("vol_breakout"):        conds.append("no_vol_breakout")
    if rec.get("cvd_score",0)<=50:         conds.append("weak_cvd")
    if rec.get("score",0)<85:              conds.append("score_under_85")
    for c in conds: fp[c]=fp.get(c,0)+1
    db["fail_patterns"]=fp

# ── التعلم ─────────────────────────────────

def learn():
    with _DB_LOCK:
        db=_load(); trades=db["trades"]
        if len(trades)<MIN_TRADES_TO_LEARN:
            return db.get("learned",{})

        sess_s={}; ob_w=ob_t=fvg_w=fvg_t=ret_w=ret_t=0
        liq_w=liq_t=sr_w=sr_t=kz_w=kz_t=clust_w=clust_t=0
        cvd_w=cvd_t=vol_w=vol_t=0
        dir_s={"BUY":[0,0],"SELL":[0,0]}
        sym_s={}
        rsi_win=[]; rsi_los=[]; sc_win=[]; sc_los=[]

        for t in trades:
            o=t["outcome"]
            sess=t.get("session","")
            if sess:
                sess_s.setdefault(sess,[0,0]); sess_s[sess][1]+=1
                if o: sess_s[sess][0]+=1
            d=t.get("direction","")
            if d in dir_s:
                dir_s[d][1]+=1
                if o: dir_s[d][0]+=1
            sym=t.get("symbol","")
            if sym:
                sym_s.setdefault(sym,[0,0]); sym_s[sym][1]+=1
                if o: sym_s[sym][0]+=1
            if t.get("has_ob"):        ob_t+=1;    ob_w+=int(o)
            if t.get("has_fvg"):       fvg_t+=1;   fvg_w+=int(o)
            if t.get("fvg_retested"):  ret_t+=1;   ret_w+=int(o)
            if t.get("has_liq_sweep"): liq_t+=1;   liq_w+=int(o)
            if t.get("sr_flip"):       sr_t+=1;    sr_w+=int(o)
            if t.get("in_kz"):         kz_t+=1;    kz_w+=int(o)
            if t.get("has_cluster"):   clust_t+=1; clust_w+=int(o)
            if t.get("cvd_score",0)>50:cvd_t+=1;  cvd_w+=int(o)
            if t.get("vol_breakout"):  vol_t+=1;   vol_w+=int(o)
            rsi=t.get("rsi_15m",50); sc=t.get("score",0)
            (rsi_win if o else rsi_los).append(rsi)
            (sc_win  if o else sc_los ).append(sc)

        def wr(w,t): return round(w/t*100,1) if t>0 else None  # None = عيّنة غير كافية (وليس 50 وهمي)
        def avg(l):  return round(sum(l)/len(l),1) if l else None

        overall_wr = wr(db["stats"]["wins"], len(trades)) or 0.0

        # إصلاح (C): معدل نجاح فعلي لكل رمز — يُستخدم في app.py لترتيب
        # أولوية فحص العملات (كان مفقوداً بالكامل، كود ميت من طرف app.py).
        per_symbol={k:{"wr":wr(v[0],v[1]),"n":v[1]} for k,v in sym_s.items() if v[1]>0}

        learned={
            "session_wr"  :{k:wr(v[0],v[1]) for k,v in sess_s.items()},
            "direction_wr":{d:wr(v[0],v[1]) for d,v in dir_s.items()},
            "per_symbol"  :per_symbol,
            "ob_wr"       :wr(ob_w,ob_t),
            "fvg_wr"      :wr(fvg_w,fvg_t),
            "retest_wr"   :wr(ret_w,ret_t),
            "liq_wr"      :wr(liq_w,liq_t),
            "sr_wr"       :wr(sr_w,sr_t),
            "kz_wr"       :wr(kz_w,kz_t),
            "cluster_wr"  :wr(clust_w,clust_t),
            "cvd_wr"      :wr(cvd_w,cvd_t),
            "vol_wr"      :wr(vol_w,vol_t),
            "ideal_rsi_win":avg(rsi_win),
            "ideal_score_win":avg(sc_win),
            "total_trades":len(trades),
            "win_rate"    :overall_wr,
            "learned_at"  :datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fail_summary":dict(sorted(
                {k:round(v/(db["stats"]["losses"] or 1)*100,1)
                 for k,v in db.get("fail_patterns",{}).items()}.items(),
                key=lambda x:x[1],reverse=True)[:8]),
        }
        ss=sorted(((k,v) for k,v in learned["session_wr"].items() if v is not None),
                  key=lambda x:x[1],reverse=True)
        learned["best_session"]=ss[0][0] if ss else ""
        db["learned"]=learned; db["last_learn"]=time.time(); _save(db)
        return learned

def should_learn():
    db=_load()
    last_learn_ts = db.get("last_learn",0)
    trades_now = len(db.get("trades",[]))
    trades_at_last_learn = db.get("learned",{}).get("total_trades",0)
    # تعلّم إذا مرّت ساعة، أو إذا تراكمت 15 صفقة جديدة مغلقة منذ آخر تعلّم
    time_due  = (time.time()-last_learn_ts) > LEARN_INTERVAL_SEC
    count_due = (trades_now - trades_at_last_learn) >= 15
    return (time_due or count_due) and trades_now >= MIN_TRADES_TO_LEARN

def get_learned(): return _load().get("learned",{})

def get_all_trades(limit=500): return _load()["trades"][-limit:]

def get_stats():
    db=_load(); t=db["stats"]["total"]
    w=db["stats"]["wins"]; l=db["stats"]["losses"]
    return {"total":t,"wins":w,"losses":l,
            "wr":round(w/t*100,1) if t else 0,
            "last_learn":db.get("learned",{}).get("learned_at","لم يتعلم بعد"),
            "best_session":db.get("learned",{}).get("best_session","--")}

# ── مكافأة الدرجة (مُصلَحة: مقارنة نسبية لخط الأساس بدل عتبة ثابتة 60%) ──

def score_bonus(signal, learned):
    """
    الإصلاح الجوهري: بدل اشتراط 'نسبة نجاح الميزة > 60% ثابتة' (شبه
    مستحيل التحقق إذا كان أداء البوت العام أقل من ذلك)، نقارن كل ميزة
    بخط الأساس (معدل النجاح العام الفعلي) — أي ميزة أفضل من المتوسط
    تُكافأ، وأي ميزة أسوأ تُعاقَب، بالتناسب مع حجم الفرق.
    """
    if not learned or learned.get("total_trades", 0) < MIN_TRADES_TO_LEARN:
        return 0

    baseline = learned.get("win_rate", 25.0) or 25.0
    b = 0.0

    def rel(feature_wr, weight, min_sample_ok=True):
        """كل 5 نقاط فرق عن الخط العام = نقطة تقييم واحدة تقريباً، بحد أقصى weight."""
        if feature_wr is None or not min_sample_ok:
            return 0.0
        diff = feature_wr - baseline
        return max(min(diff / 5.0, weight), -weight)

    sess = signal.get("session", "")
    b += rel(learned.get("session_wr", {}).get(sess), 8)

    d = signal.get("direction", "")
    b += rel(learned.get("direction_wr", {}).get(d), 6)

    # معدل نجاح الرمز نفسه تاريخياً، إن توفرت عيّنة كافية (n>=3)
    sym = signal.get("symbol", "")
    sym_stat = learned.get("per_symbol", {}).get(sym)
    if sym_stat and sym_stat.get("n", 0) >= 3:
        b += rel(sym_stat.get("wr"), 7)

    # إصلاح (B): has_ob أصبح اختيارياً فعلياً في app.py (لم يعد إلزامياً
    # دائماً True)، فمقارنة win rate عند وجوده تحمل قيمة تمييزية حقيقية.
    if signal.get("has_ob"):
        b += rel(learned.get("ob_wr"), 6)

    # ملاحظة: has_liq_sweep و fvg_retested لا يزالان يُستبعدان هنا لأنهما
    # إلزاميان دائماً True في app.py الحالي (بلا قيمة تمييزية).

    if signal.get("sr_flip"):
        b += rel(learned.get("sr_wr"), 8)
    if signal.get("in_kz"):
        b += rel(learned.get("kz_wr"), 6)
    if signal.get("has_cluster"):
        b += rel(learned.get("cluster_wr"), 5)
    if signal.get("vol_breakout"):
        b += rel(learned.get("vol_wr"), 5)
    if signal.get("cvd_score", 0) > 50:
        b += rel(learned.get("cvd_wr"), 6)

    # قرب RSI الحالي من متوسط RSI للصفقات الرابحة تاريخياً
    ideal_rsi = learned.get("ideal_rsi_win")
    if ideal_rsi is not None:
        rsi_diff = abs(signal.get("rsi_15m", 50) - ideal_rsi)
        if rsi_diff < 5:
            b += 3
        elif rsi_diff > 20:
            b -= 3

    # عقوبات إضافية من fail_summary — تفحص فقط ميزات فعلاً اختيارية الآن
    fail = learned.get("fail_summary", {})
    if not signal.get("has_ob")         and fail.get("no_ob", 0) > 45:            b -= 5
    if not signal.get("sr_flip")        and fail.get("no_sr_flip", 0) > 45:       b -= 6
    if not signal.get("has_cluster")    and fail.get("no_cluster", 0) > 45:       b -= 4
    if not signal.get("vol_breakout")   and fail.get("no_vol_breakout", 0) > 45:  b -= 5

    return max(min(round(b), 25), -25)

# ── Backtest ────────────────────────────────

def run_backtest():
    with _DB_LOCK:
        db=_load(); trades=db["trades"]
        if len(trades)<10: return {"status":"بيانات غير كافية"}
        bk={"<65":[],"65-75":[],"75-85":[],"85+":[],"الكل":[]}
        for t in trades:
            sc=t.get("score",0); o=t["outcome"]
            bk["الكل"].append(o)
            if   sc<65: bk["<65"].append(o)
            elif sc<75: bk["65-75"].append(o)
            elif sc<85: bk["75-85"].append(o)
            else:       bk["85+"].append(o)
        def wr(lst): return round(sum(lst)/len(lst)*100,1) if lst else 0
        result={"by_score":{k:{"n":len(v),"wr":wr(v)} for k,v in bk.items()},
                "ran_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        wins=[t for t in trades if t["outcome"]==1]
        if wins:
            result["win_factors"]={
                "kz"    :round(sum(1 for t in wins if t.get("in_kz"))/len(wins)*100,1),
                "ob"    :round(sum(1 for t in wins if t.get("has_ob"))/len(wins)*100,1),
                "retest":round(sum(1 for t in wins if t.get("fvg_retested"))/len(wins)*100,1),
                "liq"   :round(sum(1 for t in wins if t.get("has_liq_sweep"))/len(wins)*100,1),
                "sr"    :round(sum(1 for t in wins if t.get("sr_flip"))/len(wins)*100,1),
            }
        db["backtest"]=result; _save(db)
        return result

def get_backtest(): return _load().get("backtest",{})

# ── الصفقات المفتوحة ────────────────────────

def save_open(trades):
    with _OPEN_LOCK:
        try:
            _atomic_write(OP_FILE, lambda f: json.dump(trades,f,ensure_ascii=False,indent=2))
        except Exception as e: print(f"save_open error: {e}")

def load_open():
    if not os.path.exists(OP_FILE): return []
    try:
        with open(OP_FILE,"r",encoding="utf-8") as f:
            t=json.load(f)
        print(f"✅ استُعيدت {len(t)} صفقة مفتوحة")
        return t
    except: return []
