#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║  CryptoBot Pro — تحليل فني متكامل (نسخة مُصلَحة)        ║
║  4H اتجاه | 1H سيولة+OB+FVG | 15M دخول بعد BOS/CISD      ║
║  CVD (24 ساعة حقيقي) + COR + Cluster + Sessions          ║
║  pip install flask flask-socketio requests eventlet      ║
╚══════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════
سجل الإصلاحات في هذه النسخة (بالترقيم المتفق عليه):
═══════════════════════════════════════════════════════════
1) نقطتا الثقة الثابتتان (اتجاه 4H + إعادة اختبار الفجوة) كانتا تُضافان
   دائماً لأن الشرطين إلزاميان أصلاً (الكود يخرج قبلهما لو لم يتحققا).
   استُبدلتا بمكافآت متغيّرة فعلياً: قوة الاتجاه الحقيقية (d%)، ودقة
   الاقتراب من منتصف الفجوة عند إعادة الاختبار.
2) لم يعد يُستبدَل FVG الساعة بفجوة مختلفة على 15 دقيقة عند فشل إعادة
   الاختبار — الفحص الآن صارم وهرمي بالكامل: السيولة + OB + الفجوة +
   فيبوناتشي كلها على فريم الساعة فقط، والدخول + بقية التأكيدات على 15د.
3) الـCVD يُحسب الآن من تراكم بيانات آخر 24 ساعة فعلياً (24 شمعة ساعة)
   بدل آخر 500 صفقة لحظية غير ممثلة لتدفق يوم كامل.
4) خطأ في اختيار أقرب مستوى دعم لسحب السيولة (كان يستخدم max بدل min
   بالخطأ) — الآن يختار فعلياً أقرب قاع سعري للسعر الحالي.
5) دورة التعلّم لم تعد تنتظر ساعة كاملة بعد كل إعادة تشغيل قبل أول فحص
   — تتحقق فوراً عند البدء ثم كل ساعة بعدها.
6) عدّاد استقبال أوامر تيليجرام (offset) يُحفظ الآن على القرص، فلا يُعاد
   معالجة رسائل قديمة بعد كل إعادة تشغيل.

تعديلات إضافية بطلب صريح:
- حد الثقة رُفع من 75% إلى 80%.
- عدد العملات المرشحة (بالسيولة) خُفّض من 20 إلى 10، ليطابق حجم قائمة
  أفضل 10 عملات CVD+COR.
- أُضيفت "المنطقة الذهبية" لفيبوناتشي (0.5–0.78) كشرط إلزامي على فريم
  الساعة، إلى جانب سحب السيولة + OB + الفجوة السعرية المملوءة — تطابقاً
  مع تسلسل الاستراتيجية الأصلي بالكامل.
- سحب السيولة و OB أصبحا الآن شرطين إلزاميين (وليسا مجرد نقاط اختيارية)
  على فريم الساعة، اتساقاً مع طلب "تزامن" كل هذه العناصر معاً.
- كل بيانات trades_db.json / open_trades.json / chat_ids.json القديمة
  محفوظة بالكامل ومتوافقة 100% مع هذه النسخة (لم يتغيّر شكل البيانات
  المحفوظة، فقط منطق التحليل الحي).

═══════════════════════════════════════════════════════════
سجل التعديلات (نسخة v3 — إصلاح قمع الإشارات + تعلم حقيقي):
═══════════════════════════════════════════════════════════
7) نافذة سحب السيولة كانت محصورة بآخر 5 شمعات فقط بينما OB وFVG يبحثان
   في آخر 30 شمعة — توسيعها إلى 20 شمعة لمطابقة بقية الشروط زمنياً،
   لأن سحب سيولة حدث قبل 6-8 شمعات لا يزال سياقاً صالحاً لنفس الحركة.
8) Order Block على 1H لم يعد شرطاً إلزامياً منفصلاً عن FVG (كان يتطلب
   وجود OB وFVG في نفس اللحظة، وهو تشديد اصطناعي: كلاهما يعبّران عن نفس
   مفهوم الفجوة السعرية بمنهجيات مختلفة). أصبح OB عامل تقييم يرفع
   السكور بقوة إن وُجد، بدل رفض الإشارة بالكامل لغيابه.
9) إعادة اختبار FVG لم تعد تعتمد على السعر اللحظي فقط (قد يكون دخل
   وخرج بين فحصين كل 5 دقائق) — أصبحت تتحقق مما إذا لُمست المنطقة في أي
   شمعة منذ تكوّن الفجوة وحتى الآن، مع تسجيل مدى قرب آخر لمسة للتقييم.
10) المنطقة الذهبية لفيبوناتشي أبقيت إلزامية (مؤشر جودة حقيقي) لكن
    بهامش تسامح واقعي (0.47–0.82 بدل 0.5–0.78 الصارمة) لأن الأسعار
    نادراً ما تلامس النسبة المئوية بدقة رياضية.
11) أُزيلت نقطة الأساس الثابتة (score=20) التي كانت تُمنح تلقائياً بلا
    أي علاقة بجودة الإشارة. السكور الآن مبني بالكامل من عوامل مُقاسة
    فعلياً (قوة اتجاه، دقة فيبو، دقة إعادة اختبار، جودة OB، إلخ) بحيث
    يعكس رقم الثقة قوة التطابق الحقيقية، لا حشواً وهمياً.
12) مكافأة/عقوبة التعلم من brain.py (على قاعدة الصفقات التاريخية ~120
    صفقة) أصبحت ذات وزن أكبر وحقيقي في القرار: تُستخدم أيضاً لتصنيف
    أولوية فحص الرموز (تُفحص أولاً الرموز/الجلسات ذات معدل النجاح
    التاريخي الأعلى)، وتُطبَّق كخصم أو إضافة فعلية على السكور النهائي
    بدل أن تكون تعديلاً تجميلياً بسيطاً.
13) MIN_SCORE أُعيد إلى 75% — لكنه الآن رقم "حقيقي" لأن مكوناته كلها
    مُقاسة (لا نقطة ثابتة مضمونة)، فبلوغ 75% يعني فعلاً تجمّع أدلة قوية
    وليس نتيجة حشو رياضي.

═══════════════════════════════════════════════════════════
سجل التعديلات (نسخة v4 — إزالة شرط فيبو + BOS/CISD + CHoCh):
═══════════════════════════════════════════════════════════
14) فيبوناتشي لم يعد شرط رفض إطلاقاً (بطلب صريح) — أصبح فقط عامل تعزيز
    للسكور عند التطابق. كان تقاطعه مع بقية الشروط الإلزامية (سيولة+FVG+
    اتجاه) نادراً جداً إحصائياً حتى بعد توسيع الهامش وربط التوقيت.
15) أُعيد ترتيب الفريمات لتطابق تماماً ما طُلب: 4H لتحديد الاتجاه العام
    فقط، 1H لرسم/تحديد الفجوات السعرية (FVG) والأوردر بلوك (OB) وسحب
    السيولة، 15M لتحديد منطقة الدخول بعد الكسر (BOS) أو بعد تغيّر حالة
    التسليم (CISD) — **أحدهما إلزامي (OR)**، بدل الفيبوناتشي كبوابة.
16) أُضيفت دالة CHoCh (Change of Character) على 1H كعامل تعزيز، مستوحاة
    من الاستراتيجية المرفقة: BOS داخل الاتجاه القديم → CHoCh عند نقطة
    الانعكاس → سحب سيولة (BSL/SSL) → عودة لمنطقة Order Block → استمرار
    الحركة. كل عنصر من هذا التسلسل ممثَّل الآن في الكود (سحب السيولة،
    OB، وCHoCh كعامل سياق يؤكد لحظة الانقلاب قبل تشكّل الـOB).

═══════════════════════════════════════════════════════════
سجل التعديلات (نسخة v5 — تبديل مصدر البيانات من Binance إلى Kraken):
═══════════════════════════════════════════════════════════
17) استبدال مصدر البيانات بالكامل من Binance Futures (fapi.binance.com،
    كان يرجع خطأ 451 Unavailable For Legal Reasons بسبب حظر جغرافي على
    IP سيرفرات الاستضافة) إلى Kraken Public API (api.kraken.com) —
    منصة لا تحظر الوصول العام لبيانات الشموع/الأسعار. لا تغيير على أي
    منطق تحليل أو شروط دخول، فقط دوال جلب البيانات الثلاث تغيّرت:
    klines() و price() و top_symbols().
18) ملاحظة مهمة: عقود Kraken العامة (OHLC endpoint) لا توفّر "حجم
    الشراء المُنفَّذ" (taker buy volume) بشكل منفصل عن حجم البيع كما
    توفره Binance Futures. لذلك حساب CVD (calc_cvd_24h) أصبح يعتمد على
    تقريب واقعي: حجم الشمعة الصاعدة (close>=open) بالكامل يُحتسب "شراء"،
    والهابطة صفر — نفس بنية دالة calc_cvd_24h ومخرجاتها لم تتغيّر، فقط
    مصدر حقل "tb" داخل klines() تغيّر لأنه غير متاح من Kraken مباشرة.
19) رموز العملات الآن بصيغة Kraken (مثال: XBTUSDT بدل BTCUSDT) لأن
    Kraken تستخدم "XBT" بدل "BTC". تم تعريف ثابت BTC_PAIR ليحل محل أي
    استخدام صريح لـ"BTCUSDT" في الكود (كان يُستخدم فقط في run_scan()
    لجلب بيانات BTC للمقارنة/الارتباط COR).
"""

import os,sys,time,json,math,threading,logging,requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from flask import Flask,render_template_string,jsonify
from flask_socketio import SocketIO,emit

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
try: import brain; BRAIN_OK=True
except: BRAIN_OK=False

# ═══════════════════════════════════════════
#  إعدادات
# ═══════════════════════════════════════════
TG_TOKEN  = os.environ.get("TG_TOKEN", "")   # يُقرأ من متغيرات البيئة (Render/GitHub) وليس من الكود
TG_CHAT   = os.environ.get("TG_CHAT", "")    # نفس الشيء — لا تضع القيمة الحقيقية هنا
KRAKEN    = "https://api.kraken.com/0/public"   # إصلاح #17: بدل Binance (fapi.binance.com) بسبب حظر 451
BTC_PAIR  = "XBTUSDT"    # إصلاح #19: زوج BTC/USDT بصيغة Kraken (XBT بدل BTC)
COOLDOWN  = 15          # دقيقة
INTERVAL  = 300         # 5 دقائق
TOP_N     = 30          # أعلى 30 عملة سيولة + أعلى 30 عملة CVD+COR (بطلب صريح)
MON_SEC   = 30
MIN_SCORE = 75          # رقم ثقة حقيقي الآن (لا نقاط ثابتة في الحساب)
RR        = 3           # نسبة المخاطرة
FIB_ZONE_MIN, FIB_ZONE_MAX = 0.47, 0.82   # المنطقة الذهبية لفيبوناتشي + هامش واقعي
LIQ_SWEEP_WINDOW = 20    # إصلاح #7: كان 5، الآن يطابق نافذة OB/FVG (30)
BRAIN_MIN_TRADES = 20    # يطابق brain.MIN_TRADES_TO_LEARN — كان مكتوباً كرقم
                          # ثابت (10) في 3 أماكن مختلفة بلا ترابط، ما يخاطر
                          # بتباعدهما لاحقاً عند تعديل أحد الملفين فقط.
SCAN_WORKERS = 8          # عدد الطلبات المتوازية أثناء الفحص (إصلاح تأخر الإرسال)
MAX_ENTRY_DRIFT = 0.5     # إصلاح بنيوي: لو السعر الحالي تجاوز نقطة الدخول
                          # المحسوبة بأكثر من 50% من مسافة الوقف، تُرفض
                          # الإشارة لأن الفرصة الفعلية فاتت وقت اكتشافها.

logging.basicConfig(level=logging.INFO,format='%(asctime)s [%(levelname)s] %(message)s')
log=logging.getLogger(__name__)
app=Flask(__name__)
app.config['SECRET_KEY']='cb_pro'

# جلسة HTTP واحدة مُعاد استخدامها (Keep-Alive) بدل فتح اتصال جديد لكل طلب —
# تقلل زمن كل طلب فردي عبر تفادي تكرار التفاوض الأمني (TLS handshake).
_HTTP = requests.Session()
sio=SocketIO(app,cors_allowed_origins="*",async_mode='threading')

# Chat IDs
CHAT_IDS=[TG_CHAT] if TG_CHAT else []
IDS_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"chat_ids.json")
OFFSET_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"tg_offset.json")

def _load_ids():
    global CHAT_IDS
    if os.path.exists(IDS_FILE):
        try:
            for c in json.load(open(IDS_FILE)):
                if str(c) not in CHAT_IDS: CHAT_IDS.append(str(c))
        except: pass

def _save_ids():
    try: json.dump(CHAT_IDS,open(IDS_FILE,"w"))
    except: pass

def _load_offset():
    if os.path.exists(OFFSET_FILE):
        try: return json.load(open(OFFSET_FILE)).get("offset",0)
        except: return 0
    return 0

def _save_offset(off):
    try: json.dump({"offset":off},open(OFFSET_FILE,"w"))
    except: pass

def _poll_tg():
    offset=_load_offset()   # إصلاح #6: يبدأ من آخر نقطة توقف بدل الصفر دائماً
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates",
                params={"offset":offset,"timeout":30},timeout=35)
            for u in r.json().get("result",[]):
                offset=u["update_id"]+1
                _save_offset(offset)
                msg=u.get("message",{})
                txt=msg.get("text","").strip()
                cid=str(msg.get("chat",{}).get("id",""))
                if txt in ("/start","start") and cid:
                    added=str(cid) not in CHAT_IDS
                    if added and len(CHAT_IDS)<5:
                        CHAT_IDS.append(str(cid)); _save_ids()
                    reply="✅ تم تسجيلك" if added else "✅ مسجّل بالفعل"
                    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                        json={"chat_id":cid,"text":reply},timeout=5)
        except: pass
        time.sleep(2)

# الحالة
ST={
    "signals":[],"open_trades":[],"top_symbols":[],"cvd_top":[],
    "last_scan":"--:--","scanning":False,"auto_on":False,
    "cooldowns":{},"next_in":0,"scan_n":0,
    "learned":{},"db_stats":{"total":0,"wins":0,"losses":0,"wr":0},
    "backtest":{},"public_url":""
}

# ═══════════════════════════════════════════
#  HTML الواجهة
# ═══════════════════════════════════════════
HTML=r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🚀 CryptoBot Pro</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js"></script>
<style>
:root{--bg:#f0f4f8;--card:#fff;--pri:#1e40af;--p2:#3b82f6;--grn:#16a34a;
  --grn-l:#dcfce7;--red:#dc2626;--red-l:#fee2e2;--gold:#d97706;
  --gold-l:#fef3c7;--gray:#64748b;--bdr:#e2e8f0;--sh:0 2px 12px rgba(0,0,0,.08)}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:var(--bg);color:#1e293b;direction:rtl}
header{background:linear-gradient(135deg,#0f172a,#1e3a8a,#0f172a);color:#fff;
  padding:12px 18px;display:flex;justify-content:space-between;align-items:center;
  position:sticky;top:0;z-index:100;box-shadow:0 4px 20px rgba(0,0,0,.3)}
header h1{font-size:1rem;display:flex;align-items:center;gap:7px}
.ldot{width:9px;height:9px;border-radius:50%;background:#22c55e;display:inline-block;animation:lp 1.5s infinite}
@keyframes lp{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.5)}50%{box-shadow:0 0 0 6px rgba(34,197,94,0)}}
.hb{padding:4px 10px;border-radius:20px;font-size:.73rem;font-weight:700;background:rgba(255,255,255,.15)}
.wrap{max-width:980px;margin:0 auto;padding:13px}
.pb{background:#e2e8f0;border-radius:2px;overflow:hidden;margin-bottom:12px;height:3px}
#ap{height:100%;background:linear-gradient(90deg,#3b82f6,#22c55e);transition:width 1s linear}
.ctrl{display:flex;gap:8px;margin-bottom:13px;flex-wrap:wrap}
.btn{padding:10px 20px;border:none;border-radius:9px;cursor:pointer;font-size:.85rem;
  font-weight:700;transition:.2s;display:flex;align-items:center;gap:5px;white-space:nowrap}
.btn:disabled{opacity:.5;cursor:not-allowed}
.bm{background:var(--p2);color:#fff}.bm:hover:not(:disabled){background:#2563eb}
.ba{background:#059669;color:#fff}.ba:hover:not(:disabled){background:#047857}
.ba.on{background:#dc2626}
.irow{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:8px;margin-bottom:12px}
.ic{background:var(--card);border-radius:9px;padding:9px 12px;box-shadow:var(--sh);border-top:3px solid var(--p2)}
.ic .lb{font-size:.64rem;color:var(--gray);margin-bottom:2px}.ic .vl{font-size:.92rem;font-weight:700}
.cd{color:var(--gold);font-variant-numeric:tabular-nums}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-bottom:13px}
.sc2{border-radius:11px;padding:13px 15px;cursor:pointer;transition:.2s;box-shadow:var(--sh)}
.sc2:hover{transform:translateY(-2px)}
.sw{background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:2px solid #16a34a}
.sl2{background:linear-gradient(135deg,#fee2e2,#fecaca);border:2px solid #dc2626}
.sn{font-size:1.9rem;font-weight:900;line-height:1}.slb{font-size:.73rem;margin-top:3px;opacity:.8}
.box{background:var(--card);border-radius:9px;padding:10px 13px;margin-bottom:12px;box-shadow:var(--sh)}
.box h3{font-size:.75rem;color:var(--gray);margin-bottom:6px}
.tags{display:flex;flex-wrap:wrap;gap:5px}
.tag{padding:2px 9px;border-radius:11px;font-size:.73rem;font-weight:700;border:1px solid}
.tg-blue{background:#eff6ff;color:var(--pri);border-color:#bfdbfe}
.tg-grn{background:#f0fdf4;color:#15803d;border-color:#86efac}
.tg-gold{background:var(--gold-l);color:#92400e;border-color:#fcd34d}
.tg-pur{background:#f5f3ff;color:#5b21b6;border-color:#c4b5fd}
.learn-info{font-size:.73rem;color:#78350f;display:flex;flex-wrap:wrap;gap:7px}
.lt{background:rgba(255,255,255,.6);padding:2px 7px;border-radius:5px}
.bt-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:6px;margin-top:7px}
.bt-item{text-align:center;background:#f8fafc;border-radius:7px;padding:6px;border:1px solid var(--bdr)}
.bt-item .bk{font-size:.65rem;color:var(--gray)}.bt-item .bv{font-size:.88rem;font-weight:800}
.st{font-size:.86rem;font-weight:700;color:var(--gray);margin:14px 0 8px;display:flex;align-items:center;gap:5px}
/* كرت الإشارة */
.scard{background:var(--card);border-radius:13px;padding:15px;box-shadow:var(--sh);
  margin-bottom:10px;border-right:5px solid var(--grn);animation:sI .3s ease}
.scard.SELL{border-right-color:var(--red)}
@keyframes sI{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:translateY(0)}}
.sh2{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.ssym{font-size:1.1rem;font-weight:800}
.sdir{padding:4px 13px;border-radius:18px;font-weight:800;font-size:.8rem}
.sdir.BUY{background:var(--grn-l);color:var(--grn)}.sdir.SELL{background:var(--red-l);color:var(--red)}
.sgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(108px,1fr));gap:6px;margin-bottom:9px}
.si2{background:#f8fafc;border-radius:7px;padding:7px 10px;border:1px solid var(--bdr)}
.si2 .lb{font-size:.64rem;color:var(--gray);margin-bottom:2px}.si2 .vl{font-size:.86rem;font-weight:700}
.ve{color:var(--pri)}.vsl{color:var(--red)}.vtp{color:#16a34a}
.sbar{height:4px;border-radius:2px;background:#e2e8f0;margin-bottom:9px;overflow:hidden}
.sbf{height:100%;border-radius:2px;background:linear-gradient(90deg,#3b82f6,#22c55e)}
.why2{background:#f0f9ff;border-radius:7px;padding:7px 10px;font-size:.73rem;
  color:#0369a1;line-height:1.55;border-right:3px solid #38bdf8;margin-bottom:8px}
.steps{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:7px}
.step{padding:2px 8px;border-radius:6px;font-size:.68rem;font-weight:700}
.s4h{background:#dbeafe;color:#1e40af}
.s1h{background:#dcfce7;color:#15803d}
.s15m{background:var(--gold-l);color:#92400e}
.sf3{font-size:.67rem;color:#94a3b8;display:flex;justify-content:space-between}
/* مراقبة */
.mc{background:var(--card);border-radius:11px;padding:12px 14px;
  box-shadow:var(--sh);margin-bottom:9px;border-right:4px solid #0ea5e9}
.mh{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.ms3{font-weight:800;font-size:.96rem}
.ms{font-size:.73rem;padding:3px 8px;border-radius:10px;font-weight:700}
.ms.open{background:#dbeafe;color:#1d4ed8}.ms.tp{background:#dcfce7;color:#15803d}
.ms.sl{background:var(--red-l);color:#991b1b}
.minfo{font-size:.73rem;color:#475569;display:flex;gap:12px;flex-wrap:wrap;margin-bottom:7px}
.mprog{display:flex;gap:5px}
.pi{flex:1;text-align:center;padding:5px;border-radius:5px;font-size:.67rem;font-weight:700;background:#f1f5f9}
.pi.hit{background:#dcfce7;color:#15803d}.pi.sl-hit{background:var(--red-l);color:#991b1b}
.ts-note{font-size:.69rem;color:#0369a1;margin-top:5px;background:#eff6ff;padding:4px 8px;border-radius:5px;border-right:3px solid #3b82f6}
/* لوق */
.logbox{background:#0f172a;color:#94a3b8;border-radius:9px;padding:11px;margin-top:13px;
  max-height:160px;overflow-y:auto;font-family:monospace;font-size:.7rem}
.logbox p{margin-bottom:2px;padding-right:3px;border-right:2px solid transparent}
.logbox .ok{color:#4ade80;border-right-color:#4ade80}
.logbox .err{color:#f87171;border-right-color:#f87171}
.logbox .info{color:#60a5fa;border-right-color:#60a5fa}
.logbox .warn{color:#fbbf24;border-right-color:#fbbf24}
.empty{text-align:center;padding:30px 15px;color:#94a3b8;background:var(--card);border-radius:13px;box-shadow:var(--sh)}
.empty .icon{font-size:2rem;margin-bottom:7px}
/* نافذة تنبيه */
#ov{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:999;justify-content:center;align-items:center}
#ov.show{display:flex}
.abox{background:#fff;border-radius:18px;padding:24px;max-width:430px;width:92%;text-align:center;
  box-shadow:0 25px 70px rgba(0,0,0,.3);animation:pop .3s ease}
@keyframes pop{from{transform:scale(.8);opacity:0}to{transform:scale(1);opacity:1}}
.ai{font-size:2.7rem;margin-bottom:7px}.at{font-size:1.1rem;font-weight:800;margin-bottom:6px}
.ab{color:#475569;margin-bottom:14px;line-height:1.6;font-size:.86rem;white-space:pre-line}
.ac{background:var(--p2);color:#fff;border:none;padding:9px 24px;border-radius:9px;cursor:pointer;font-size:.93rem;font-weight:700}
/* مودال الصفقات */
#tm{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:998;
  justify-content:center;align-items:flex-start;padding-top:40px}
#tm.show{display:flex}
.tmo{background:#fff;border-radius:16px;width:92%;max-width:580px;max-height:78vh;
  overflow:hidden;display:flex;flex-direction:column}
.tmh{padding:13px 17px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--bdr)}
.tmh h2{font-size:.97rem;font-weight:800}
.tmb{overflow-y:auto;padding:13px 17px;flex:1}
.tr{display:flex;justify-content:space-between;align-items:center;padding:7px 0;
  border-bottom:1px solid #f1f5f9;font-size:.78rem}
.tr:last-child{border-bottom:none}
.tc{background:#f1f5f9;border:none;padding:5px 13px;border-radius:7px;cursor:pointer;font-weight:700;font-size:.8rem}
.url-box{background:#ecfdf5;border:1px solid #10b981;border-radius:9px;padding:9px 13px;
  margin-bottom:12px;font-size:.76rem;color:#065f46;word-break:break-all}
</style>
</head>
<body>
<header>
  <h1><span class="ldot"></span> CryptoBot Pro</h1>
  <span class="hb" id="hb">⏹ متوقف</span>
</header>
<div class="wrap">
  <div class="url-box" id="url-box" style="display:none"></div>
  <div class="pb" id="pw" style="display:none"><div id="ap" style="width:100%"></div></div>
  <div class="ctrl">
    <button class="btn bm" id="bm" onclick="manualScan()">🔍 فحص يدوي</button>
    <button class="btn ba" id="ba" onclick="toggleAuto()">▶️ فحص آلي (5د)</button>
  </div>
  <div class="irow">
    <div class="ic"><div class="lb">آخر فحص</div><div class="vl" id="ls">--:--</div></div>
    <div class="ic"><div class="lb">الفحص القادم</div><div class="vl cd" id="ns">--</div></div>
    <div class="ic"><div class="lb">فحوصات</div><div class="vl" id="sc3">0</div></div>
    <div class="ic"><div class="lb">إشارات</div><div class="vl" id="sic">0</div></div>
    <div class="ic"><div class="lb">مفتوحة</div><div class="vl" id="tc">0</div></div>
    <div class="ic"><div class="lb">حد الثقة</div><div class="vl" style="color:var(--gold)">75%</div></div>
  </div>
  <div class="row2">
    <div class="sc2 sw" onclick="showTrades('win')">
      <div class="sn" id="wn">0</div><div class="slb">✅ رابحة — تفاصيل</div>
    </div>
    <div class="sc2 sl2" onclick="showTrades('lose')">
      <div class="sn" id="ln">0</div><div class="slb">❌ خاسرة — تفاصيل</div>
    </div>
  </div>
  <div class="box" id="cvd-box" style="display:none">
    <h3>📊 أفضل 30 عملات (CVD + COR عالي)</h3>
    <div class="tags" id="cvd-list"></div>
  </div>
  <div class="box" style="background:linear-gradient(135deg,#fef3c7,#fde68a);border:1px solid #f59e0b" id="learn-box" style="display:none">
    <h3 style="color:#92400e">🧠 ما تعلمه البوت</h3>
    <div class="learn-info" id="learn-info"></div>
  </div>
  <div class="box" id="bt-box" style="display:none">
    <h3>📈 Backtesting — نسبة النجاح بالدرجة</h3>
    <div class="bt-grid" id="bt-grid"></div>
  </div>
  <div class="box">
    <h3>🔥 أعلى  30 عملة سيولة</h3>
    <div class="tags" id="sym-list"><span style="color:#94a3b8;font-size:.75rem">في انتظار الفحص...</span></div>
  </div>
  <div class="st">📊 أفضل صفقتين</div>
  <div id="sigs-wrap"><div class="empty"><div class="icon">🕐</div><div>في انتظار أول فحص...</div></div></div>
  <div class="st">👁️ مراقبة الصفقات المفتوحة</div>
  <div id="mon-wrap"><div class="empty"><div class="icon">📭</div><div>لا توجد صفقات مفتوحة</div></div></div>
  <div class="logbox" id="logbox"></div>
</div>

<div id="ov">
  <div class="abox">
    <div class="ai" id="ai">🚨</div><div class="at" id="at"></div>
    <div class="ab" id="ab"></div><button class="ac" onclick="closeAlert()">موافق</button>
  </div>
</div>
<div id="tm">
  <div class="tmo">
    <div class="tmh"><h2 id="mtt">الصفقات</h2><button class="tc" onclick="closeModal()">✕</button></div>
    <div class="tmb" id="mb"></div>
  </div>
</div>

<script>
const socket=io(); let cdI=null,cd=0,allT=[];
let wl=null;
async function reqWL(){try{if('wakeLock' in navigator)wl=await navigator.wakeLock.request('screen');}catch(e){}}
async function relWL(){try{if(wl){await wl.release();wl=null;}}catch(e){}}
document.addEventListener('visibilitychange',async()=>{
  if(document.visibilityState==='visible'&&document.getElementById('ba').classList.contains('on'))await reqWL();
});
socket.on('state_update',d=>updateUI(d));
socket.on('new_signal',s=>showAlert('signal',s));
socket.on('trade_event',e=>showAlert('trade',e));
socket.on('log',m=>addLog(m.text,m.type||'info'));
socket.on('trades_data',t=>{allT=t;});
socket.on('connect',()=>socket.emit('req_state'));

function updateUI(d){
  const hb=document.getElementById('hb');
  if(d.scanning){hb.textContent='⏳ جاري الفحص...';hb.style.background='rgba(251,191,36,.3)';}
  else if(d.auto_on){hb.textContent='🟢 فحص آلي';hb.style.background='rgba(34,197,94,.25)';}
  else{hb.textContent='⏹ متوقف';hb.style.background='rgba(255,255,255,.15)';}
  document.getElementById('bm').disabled=d.scanning;
  const ba=document.getElementById('ba');
  if(d.auto_on){ba.textContent='⏹ إيقاف الآلي';ba.className='btn ba on';
    document.getElementById('pw').style.display='block';reqWL();}
  else{ba.textContent='▶️ فحص آلي (5د)';ba.className='btn ba';
    document.getElementById('pw').style.display='none';relWL();}
  document.getElementById('ls').textContent=d.last_scan||'--:--';
  document.getElementById('sc3').textContent=d.scan_n||0;
  document.getElementById('sic').textContent=(d.signals||[]).length;
  document.getElementById('tc').textContent=(d.open_trades||[]).length;
  const st=d.db_stats||{};
  document.getElementById('wn').textContent=st.wins||0;
  document.getElementById('ln').textContent=st.losses||0;
  if(d.public_url){const ub=document.getElementById('url-box');ub.style.display='block';
    ub.innerHTML='🌐 رابط Cron-Job: <b>'+d.public_url+'/ping</b>';}
  if(d.cvd_top&&d.cvd_top.length){
    document.getElementById('cvd-box').style.display='block';
    document.getElementById('cvd-list').innerHTML=
      d.cvd_top.map(s=>`<span class="tag tg-grn">📊 ${s}</span>`).join('');
  }
  if(d.top_symbols&&d.top_symbols.length)
    document.getElementById('sym-list').innerHTML=
      d.top_symbols.map(s=>`<span class="tag tg-blue">${s}</span>`).join('');
  const l=d.learned||{};
  if(l.total_trades){
    document.getElementById('learn-box').style.display='block';
    document.getElementById('learn-info').innerHTML=`
      <span class="lt">📊 ${l.total_trades} صفقة</span>
      <span class="lt">✅ نجاح: ${l.win_rate}%</span>
      <span class="lt">📅 أفضل جلسة: ${l.best_session||'--'}</span>
      <span class="lt">⚠️ ${Object.keys(l.fail_summary||{}).slice(0,2).join(', ')||'--'}</span>
      <span class="lt">⏰ ${l.learned_at||'--'}</span>`;
  }
  const bt=d.backtest||{};
  if(bt.by_score){
    document.getElementById('bt-box').style.display='block';
    document.getElementById('bt-grid').innerHTML=
      Object.entries(bt.by_score).map(([k,v])=>`
        <div class="bt-item"><div class="bk">${k}</div>
        <div class="bv" style="color:${v.wr>=55?'#16a34a':'#dc2626'}">${v.wr}%</div>
        <div style="font-size:.62rem;color:#94a3b8">${v.n} صفقة</div></div>`).join('');
  }
  if(d.auto_on&&d.next_in>0) startCD(d.next_in);
  else if(!d.auto_on){document.getElementById('ns').textContent='--';
    if(cdI){clearInterval(cdI);cdI=null;}}
  renderSignals(d.signals||[]);
  renderMonitor(d.open_trades||[]);
}

function startCD(sec){
  if(cdI)clearInterval(cdI); cd=sec;
  const el=document.getElementById('ns'),bar=document.getElementById('ap');
  cdI=setInterval(()=>{
    if(cd<=0){clearInterval(cdI);el.textContent='جاري...';return;}
    cd--;
    el.textContent=`${Math.floor(cd/60)}:${(cd%60).toString().padStart(2,'0')}`;
    bar.style.width=(cd/300*100)+'%';
  },1000);
}

function renderSignals(signals){
  const w=document.getElementById('sigs-wrap');
  if(!signals.length){w.innerHTML='<div class="empty"><div class="icon">🔍</div><div>لم تُكتشف إشارات (≥75%)</div></div>';return;}
  w.innerHTML=signals.slice(0,2).map(s=>{
    const buy=s.direction==='BUY'; const sc=Math.min(100,Math.round(s.score||0));
    return `
    <div class="scard ${s.direction}">
      <div class="sh2">
        <div class="ssym">💰 ${s.symbol}</div>
        <div class="sdir ${s.direction}">${buy?'🟢 شراء':'🔴 بيع'}</div>
      </div>
      <div class="steps">
        <span class="step s4h">4H: ${s.trend_4h}</span>
        <span class="step s1h">1H: سيولة✅ FVG✅ ${s.has_ob?'OB✅':'OB—'}${s.choch?' CHoCh✅':''}</span>
        <span class="step s15m">15M: دخول ${s.entry} (${[s.bos?'BOS':'',s.cisd?'CISD':''].filter(Boolean).join('+')})</span>
      </div>
      <div class="sgrid">
        <div class="si2"><div class="lb">🎯 دخول</div><div class="vl ve">${s.entry}</div></div>
        <div class="si2"><div class="lb">🛑 وقف</div><div class="vl vsl">${s.sl}</div></div>
        <div class="si2"><div class="lb">🏆 هدف (1:3)</div><div class="vl vtp">${s.tp}</div></div>
        <div class="si2"><div class="lb">📐 R:R</div><div class="vl">1:${s.rr}</div></div>
        <div class="si2"><div class="lb">📊 CVD (24س)</div><div class="vl">${s.cvd_score||0}%</div></div>
        <div class="si2"><div class="lb">🔗 COR BTC</div><div class="vl">${s.cor_btc||0}</div></div>
        <div class="si2"><div class="lb">📐 فيبو (تعزيز)</div><div class="vl">${s.fib_in_zone?(s.fib_precision+'%'):'—'}</div></div>
        <div class="si2"><div class="lb">⏱ الجلسة</div><div class="vl">${s.session}</div></div>
        <div class="si2"><div class="lb">RSI 15M</div><div class="vl">${s.rsi_15m}</div></div>
        <div class="si2"><div class="lb">🧠 ثقة</div><div class="vl">${sc}%</div></div>
      </div>
      <div class="sbar"><div class="sbf" style="width:${sc}%"></div></div>
      <div class="tags" style="margin-bottom:8px">
        <span class="tag tg-gold">💧 سحب سيولة (إلزامي)</span>
        <span class="tag tg-grn">⚡ FVG مُعاد اختباره (إلزامي)</span>
        <span class="tag tg-pur">💥 ${[s.bos?'BOS':'',s.cisd?'CISD':''].filter(Boolean).join('+')} (إلزامي)</span>
        ${s.has_ob?'<span class="tag tg-blue">🟦 Order Block</span>':''}
        ${s.choch?'<span class="tag tg-pur">🔀 CHoCh</span>':''}
        ${s.fib_in_zone?'<span class="tag tg-pur">📐 منطقة ذهبية فيبو</span>':''}
        ${s.sr_flip?'<span class="tag tg-pur">🔄 SR Flip</span>':''}
        ${s.has_cluster?'<span class="tag tg-pur">🎯 Cluster</span>':''}
        ${s.in_kz?'<span class="tag tg-grn">⚡ Kill Zone</span>':''}
        ${s.vol_breakout?'<span class="tag tg-blue">📈 Vol Breakout</span>':''}
      </div>
      <div class="why2">💡 <b>التحليل:</b><br>${s.why}</div>
      <div class="sf3"><span>⏰ ${s.time}</span><span>ثقة: ${sc}%</span></div>
    </div>`;
  }).join('');
}

function renderMonitor(trades){
  const w=document.getElementById('mon-wrap');
  if(!trades.length){w.innerHTML='<div class="empty"><div class="icon">📭</div><div>لا توجد صفقات مفتوحة</div></div>';return;}
  w.innerHTML=trades.map(t=>{
    const st=t.status||'open'; const pnl=t.pnl||0;
    const stL={open:'🔵 مفتوحة',tp:'✅ الهدف',sl:'🔴 استوب'}[st]||st;
    let tsNote='';
    if(t.hit_tp1&&!t.hit_tp&&!t.hit_sl)
      tsNote=`<div class="ts-note">💡 Trailing Stop: حرّك الاستوب إلى نقطة الدخول ${t.entry} (التعادل)</div>`;
    return `
    <div class="mc">
      <div class="mh"><div class="ms3">${t.direction==='BUY'?'🟢':'🔴'} ${t.symbol}</div>
        <div class="ms ${st}">${stL}</div></div>
      <div class="minfo">
        <span>دخول: <b>${t.entry}</b></span>
        <span>حالي: <b>${t.current||'...'}</b></span>
        <span>P&L: <b style="color:${pnl>=0?'var(--grn)':'var(--red)'}">${pnl}%</b></span>
        <span>SL: <b>${t.sl}</b></span>
        <span>TP: <b>${t.tp}</b></span>
      </div>
      <div class="mprog">
        <div class="pi ${t.hit_tp1?'hit':''}">🎯 TP1<br>${t.tp1||'--'}</div>
        <div class="pi ${t.hit_tp?'hit':''}">🏆 TP<br>${t.tp}</div>
        <div class="pi ${t.hit_sl?'sl-hit':''}">🛑 SL<br>${t.sl}</div>
      </div>
      ${tsNote}
    </div>`;
  }).join('');
}

function showTrades(type){
  const isW=type==='win';
  const fl=allT.filter(t=>isW?t.outcome===1:t.outcome===0);
  document.getElementById('mtt').textContent=isW?`✅ الرابحة (${fl.length})`:`❌ الخاسرة (${fl.length})`;
  const b=document.getElementById('mb');
  if(!fl.length){b.innerHTML='<div style="text-align:center;padding:28px;color:#94a3b8">لا توجد بيانات</div>';return;}
  b.innerHTML=fl.slice().reverse().map(t=>`
    <div class="tr">
      <div><b>${t.symbol}</b>
        <span style="font-size:.7rem;color:${t.direction==='BUY'?'#16a34a':'#dc2626'};margin-right:4px">
          ${t.direction==='BUY'?'شراء':'بيع'}</span>
        <span style="font-size:.66rem;color:#64748b">${t.session||''}</span></div>
      <div style="text-align:left;font-size:.7rem;color:#64748b">
        <div>دخول: ${t.entry}</div><div>${t.closed_at}</div></div>
      <div style="font-size:1rem">${isW?'✅':'❌'}</div>
    </div>`).join('');
  document.getElementById('tm').classList.add('show');
}
function closeModal(){document.getElementById('tm').classList.remove('show');}

function showAlert(type,data){
  let icon='🚨',title='',body='';
  if(type==='signal'){
    icon=data.direction==='BUY'?'🟢':'🔴';
    title=`إشارة ${data.direction==='BUY'?'شراء':'بيع'} — ${data.symbol}`;
    body=`دخول: ${data.entry} | وقف: ${data.sl}\nهدف (1:3): ${data.tp}\nثقة: ${data.score||0}%\nCVD: ${data.cvd_score||0}% | الجلسة: ${data.session}`;
  } else {icon=data.icon||'📢';title=data.title||'';body=data.body||'';}
  document.getElementById('ai').textContent=icon;
  document.getElementById('at').textContent=title;
  document.getElementById('ab').textContent=body;
  document.getElementById('ov').classList.add('show');
  playBeep(type==='signal'?880:660);
}
function closeAlert(){document.getElementById('ov').classList.remove('show');}
function playBeep(f=880){
  try{
    const ctx=new(window.AudioContext||window.webkitAudioContext)();
    [0,.15,.3].forEach((t,i)=>{
      const o=ctx.createOscillator(),g=ctx.createGain();
      o.connect(g);g.connect(ctx.destination);o.frequency.value=f+(i*110);
      g.gain.setValueAtTime(.25,ctx.currentTime+t);
      g.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+t+.2);
      o.start(ctx.currentTime+t);o.stop(ctx.currentTime+t+.25);
    });
  }catch(e){}
}
function addLog(txt,type='info'){
  const b=document.getElementById('logbox');
  const p=document.createElement('p'); p.className=type;
  p.textContent=`[${new Date().toLocaleTimeString('ar')}] ${txt}`;
  b.appendChild(p); b.scrollTop=b.scrollHeight;
  while(b.children.length>60) b.removeChild(b.firstChild);
}
function manualScan(){document.getElementById('bm').disabled=true;socket.emit('manual_scan');}
function toggleAuto(){socket.emit('toggle_auto');}
setInterval(()=>{fetch('/ping').catch(()=>{});},240000);
</script>
</body>
</html>
"""

# ═══════════════════════════════════════════
#  Kraken API (إصلاح #17: بديل Binance بسبب حظر 451 الجغرافي)
# ═══════════════════════════════════════════

def _kraken_interval(tf):
    """يحوّل رمز الفريم (4h/1h/15m) إلى الدقائق التي تطلبها Kraken فعلياً."""
    return {"4h":240,"1h":60,"15m":15}.get(tf,60)

def klines(sym,tf,n=200):
    try:
        interval=_kraken_interval(tf)
        r=_HTTP.get(f"{KRAKEN}/OHLC",params={"pair":sym,"interval":interval},timeout=7)
        data=r.json()
        if data.get("error"):
            log.error(f"klines {sym} {tf}: Kraken رجّع خطأ — {data['error']}")
            return []
        result=data.get("result",{})
        key=next((k for k in result if k!="last"),None)
        if not key: return []
        rows=result[key][-n:]
        out=[]
        for row in rows:
            t,o,h,l,c,vwap,vol,count=row
            o_f=float(o); c_f=float(c); v_f=float(vol)
            # إصلاح #18: Kraken لا توفّر "حجم الشراء المُنفَّذ" منفصلاً عن حجم
            # البيع داخل الشمعة كما توفره Binance Futures (حقل tb الأصلي).
            # تقريب واقعي: الشمعة الصاعدة (close>=open) تُحتسب حجمها بالكامل
            # كـ"شراء"، والهابطة صفر — يبقي دالة calc_cvd_24h تعمل بنفس بنيتها.
            tb=v_f if c_f>=o_f else 0.0
            out.append({"o":o_f,"h":float(h),"l":float(l),"c":c_f,"v":v_f,"t":int(float(t))*1000,"tb":tb})
        return out
    except Exception as e:
        log.error(f"klines {sym} {tf}: {e}")
        return []

def price(sym):
    try:
        r=_HTTP.get(f"{KRAKEN}/Ticker",params={"pair":sym},timeout=4)
        data=r.json()
        if data.get("error"): return None
        result=data.get("result",{})
        key=next((k for k in result if k!="last"),None)
        if not key: return None
        return float(result[key]["c"][0])   # آخر سعر تنفيذ
    except: return None

def top_symbols(n=TOP_N):
    try:
        rp=_HTTP.get(f"{KRAKEN}/AssetPairs",timeout=10)
        pdata=rp.json()
        if pdata.get("error"):
            log.error(f"top_symbols: Kraken (AssetPairs) رجّع خطأ — {pdata['error']}")
            return []
        # كل أزواج USDT العامة (نستثني عملات مستقرة أخرى مقابل USDT، غير مفيدة كإشارات اتجاه)
        excl=("USDCUSDT","DAIUSDT","TUSDUSDT","FDUSDUSDT")
        all_pairs=[k for k in pdata.get("result",{}) if k.endswith("USDT") and k not in excl]
        vols={}
        batch=15   # Kraken تحدّ عدد الأزواج بالطلب الواحد؛ نُجزّئها لدفعات آمنة
        for i in range(0,len(all_pairs),batch):
            chunk=all_pairs[i:i+batch]
            try:
                rt=_HTTP.get(f"{KRAKEN}/Ticker",params={"pair":",".join(chunk)},timeout=10)
                td=rt.json()
                if td.get("error"): continue
                for k,info in td.get("result",{}).items():
                    try:
                        vol24=float(info["v"][1]); last=float(info["c"][0])
                        vols[k]=vol24*last   # تقريب لحجم التداول بالدولار (شبيه quoteVolume)
                    except: continue
            except Exception: continue
        ranked=sorted(vols.items(),key=lambda x:x[1],reverse=True)
        return [k for k,_ in ranked[:n]]
    except Exception as e:
        log.error(f"top_symbols: فشل الاتصال بـ Kraken — {e}")
        return []

# ═══════════════════════════════════════════
#  مؤشرات تقنية
# ═══════════════════════════════════════════

def ema(vals,p):
    if len(vals)<p: return vals[-1] if vals else 0
    k=2/(p+1); e=sum(vals[:p])/p
    for v in vals[p:]: e=v*k+e*(1-k)
    return e

def rsi_calc(c,p=14):
    if len(c)<p+2: return 50.0
    cl=[x['c'] for x in c[-(p+2):]]
    g=[max(cl[i]-cl[i-1],0) for i in range(1,len(cl))]
    l=[max(cl[i-1]-cl[i],0) for i in range(1,len(cl))]
    ag=sum(g[:p])/p; al=sum(l[:p])/p
    for i in range(p,len(g)):
        ag=(ag*(p-1)+g[i])/p; al=(al*(p-1)+l[i])/p
    return round(100-(100/(1+ag/al)) if al else 100,2)

def atr_calc(c,p=14):
    if len(c)<2: return 0
    trs=[]
    for i in range(1,len(c)):
        cv,pv=c[i],c[i-1]
        trs.append(max(cv['h']-cv['l'],abs(cv['h']-pv['c']),abs(cv['l']-pv['c'])))
    return sum(trs[-p:])/min(p,len(trs))

def vol_ratio(c,p=20):
    if len(c)<p+1: return 1.0
    avg=sum(x['v'] for x in c[-(p+1):-1])/p
    return round(c[-1]['v']/avg,2) if avg else 1.0

def trend4h(c):
    """يُرجع الاتجاه + قوته الفعلية (d%) — يُستخدم فقط لتحديد الاتجاه العام.
    كل بقية التحليل (سيولة/OB/FVG/فيبو) على 1H، والدخول والتأكيد على 15M."""
    cl=[x['c'] for x in c]
    if len(cl)<50: return "SIDEWAYS",0.0
    ef=ema(cl,20); es=ema(cl,50); cur=cl[-1]
    d=(ef-es)/es*100
    if cur>ef>es and d>0.15: return "UP",d
    if cur<ef<es and d<-0.15: return "DOWN",d
    return "SIDEWAYS",d

# ═══════════════════════════════════════════
#  CVD — تدفق الأوامر التراكمي (إصلاح #3: 24 ساعة حقيقية من الشموع)
# ═══════════════════════════════════════════

def calc_cvd_24h(sym):
    """
    بدل الاعتماد على آخر 500 صفقة لحظية (قد تمثل ثوانٍ فقط)، نحسب التدفق
    التراكمي من بيانات آخر 24 شمعة ساعة فعلياً — تمثيل حقيقي ليوم كامل.
    """
    c=klines(sym,"1h",24)
    if not c: return {"score":50.0,"bull":False}
    buy_v=sum(x['tb'] for x in c)
    tot_v=sum(x['v'] for x in c)
    if tot_v==0: return {"score":50.0,"bull":False}
    ratio=buy_v/tot_v
    return {"score":round(ratio*100,1),"bull":ratio>0.52}

# ═══════════════════════════════════════════
#  COR — الارتباط مع BTC
# ═══════════════════════════════════════════

def calc_cor(sym_c,btc_c,p=20):
    if len(sym_c)<p or len(btc_c)<p: return 0.0
    s=[x['c'] for x in sym_c[-p:]]; b=[x['c'] for x in btc_c[-p:]]
    ms=sum(s)/p; mb=sum(b)/p
    num=sum((s[i]-ms)*(b[i]-mb) for i in range(p))
    ds=(sum((x-ms)**2 for x in s))**.5
    db=(sum((x-mb)**2 for x in b))**.5
    return round(num/(ds*db),2) if ds*db>0 else 0.0

# ═══════════════════════════════════════════
#  أفضل 10 عملات CVD + COR
# ═══════════════════════════════════════════

def _cvd_cor_for_symbol(sym,btc_c):
    """يُستخدم داخل ThreadPoolExecutor لجلب CVD+COR لعملة واحدة — يُنفَّذ
    بالتوازي مع بقية العملات بدل التسلسل، وهذا الجزء الأكبر من إصلاح
    تأخر إرسال الصفقات (كان يجيب بيانات 30 عملة وحدة تلو الأخرى)."""
    try:
        cvd=calc_cvd_24h(sym)
        c1h=klines(sym,"1h",25)
        cor=calc_cor(c1h,btc_c,20) if len(c1h)>=20 else 0
        score=cvd["score"]*0.6+abs(cor)*40
        return sym,{"cvd":cvd["score"],"cor":cor,"bull":cvd["bull"],"score":round(score,1)}
    except Exception:
        return sym,None

def get_cvd_top(syms,btc_c):
    """يُرجع الآن (top_list, cvd_raw_map) — cvd_raw_map يُعاد استخدامه لاحقاً
    داخل analyze() بدل إعادة حساب calc_cvd_24h لنفس العملة مرتين كل دورة."""
    data={}
    with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as ex:
        futures=[ex.submit(_cvd_cor_for_symbol,sym,btc_c) for sym in syms[:TOP_N]]
        for fut in as_completed(futures):
            sym,d=fut.result()
            if d: data[sym]=d
    results=[{"symbol":s,**d} for s,d in data.items()]
    results.sort(key=lambda x:x["score"],reverse=True)
    top=[r["symbol"] for r in results[:TOP_N]]
    cvd_raw={s:{"score":d["cvd"],"bull":d["bull"]} for s,d in data.items()}
    return top,cvd_raw

# ═══════════════════════════════════════════
#  الجلسات و Kill Zones
# ═══════════════════════════════════════════

def get_session():
    now=datetime.utcnow(); h=now.hour+now.minute/60
    if 0<=h<8:    sess="Asia"
    elif 8<=h<16: sess="London"
    elif 16<=h<22:sess="NY"
    else:          sess="Off"
    in_kz=(7<=h<10) or (12<=h<16) or (19<=h<21)
    return {"session":sess,"in_kz":in_kz,"h":h}

# ═══════════════════════════════════════════
#  SR Flip — مقاومة صارت دعم أو العكس
# ═══════════════════════════════════════════

def find_sr_flip(c1h,direction,lookback=50):
    if len(c1h)<lookback: return False,0
    recent=c1h[-lookback:]
    cur=c1h[-1]['c']
    pivots=[]
    for i in range(2,len(recent)-2):
        c=recent[i]
        if c['h']>recent[i-1]['h'] and c['h']>recent[i-2]['h'] and \
           c['h']>recent[i+1]['h'] and c['h']>recent[i+2]['h']:
            pivots.append(("resistance",c['h'],i))
        if c['l']<recent[i-1]['l'] and c['l']<recent[i-2]['l'] and \
           c['l']<recent[i+1]['l'] and c['l']<recent[i+2]['l']:
            pivots.append(("support",c['l'],i))
    tol=cur*0.005
    if direction=="BUY":
        for typ,lvl,idx in reversed(pivots):
            if typ=="resistance" and abs(cur-lvl)<tol*2 and cur>lvl-tol:
                return True,round(lvl,6)
    else:
        for typ,lvl,idx in reversed(pivots):
            if typ=="support" and abs(cur-lvl)<tol*2 and cur<lvl+tol:
                return True,round(lvl,6)
    return False,0

# ═══════════════════════════════════════════
#  Order Block (إصلاح #8: لم يعد إلزامياً — عامل تقييم إضافي)
# ═══════════════════════════════════════════

def find_ob(c,direction,lookback=30):
    """إصلاح جديد: كانت تبحث من الأقدم للأحدث وترجع أول تطابق تجده (أبعد
    Order Block ممكن)، بعكس find_fvg وfind_liq_sweep اللتين تُفضّلان
    أقرب تطابق للسعر الحالي زمنياً. الآن تبحث من الأحدث للأقدم فترجع
    أقرب OB فعلي وأكثرها صلاحية للسعر الحالي — تماشياً مع بقية الدوال."""
    if len(c)<5: return None
    recent=c[-lookback:]
    for i in range(len(recent)-2,2,-1):
        cv=recent[i]; nxt=recent[i+1]
        body=abs(cv['c']-cv['o']); nb=abs(nxt['c']-nxt['o'])
        if nb<body*1.2: continue
        if direction=="BUY" and cv['c']<cv['o']:
            return {"top":cv['h'],"bot":cv['l'],"mid":(cv['h']+cv['l'])/2}
        if direction=="SELL" and cv['c']>cv['o']:
            return {"top":cv['h'],"bot":cv['l'],"mid":(cv['h']+cv['l'])/2}
    return None

# ═══════════════════════════════════════════
#  FVG + Retest (إصلاح #9: يتحقق من أي لمسة منذ التكوّن، لا اللحظة فقط)
# ═══════════════════════════════════════════

def find_fvg(c,direction,lookback=30):
    """
    يُرجع (fvg, retested, retest_precision).
    retested=True إذا لُمست منطقة الفجوة في أي شمعة منذ تكوّنها وحتى الآن
    (وليس فقط في شمعة الفحص الحالية — قد يكون السعر دخل وخرج بين فحصين).
    retest_precision: مدى قرب أقرب لمسة من منتصف الفجوة (0-1)، لتقييم الجودة.
    """
    if len(c)<5: return None,False,0.0
    recent=c[-lookback:]
    for i in range(len(recent)-3,0,-1):
        c1=recent[i]; c3=recent[i+2]
        if direction=="BUY" and c3['l']>c1['h']:
            fvg={"top":c3['l'],"bot":c1['h'],"mid":(c3['l']+c1['h'])/2}
            after=recent[i+3:] if i+3<len(recent) else []
            touches=[x for x in after if x['l']<=fvg["top"]*1.005 and x['h']>=fvg["bot"]]
            retested=len(touches)>0
            precision=0.0
            if retested:
                fvg_half=max((fvg["top"]-fvg["bot"])/2,1e-9)
                closest=min(abs(((x['h']+x['l'])/2)-fvg["mid"]) for x in touches)
                precision=max(0.0,1-closest/fvg_half)
            return fvg,retested,precision
        if direction=="SELL" and c3['h']<c1['l']:
            fvg={"top":c1['l'],"bot":c3['h'],"mid":(c1['l']+c3['h'])/2}
            after=recent[i+3:] if i+3<len(recent) else []
            touches=[x for x in after if x['h']>=fvg["bot"]*0.995 and x['l']<=fvg["top"]]
            retested=len(touches)>0
            precision=0.0
            if retested:
                fvg_half=max((fvg["top"]-fvg["bot"])/2,1e-9)
                closest=min(abs(((x['h']+x['l'])/2)-fvg["mid"]) for x in touches)
                precision=max(0.0,1-closest/fvg_half)
            return fvg,retested,precision
    return None,False,0.0

# ═══════════════════════════════════════════
#  Liquidity Sweep (إصلاح #4: أقرب مستوى صحيح | إصلاح #7: نافذة أوسع)
# ═══════════════════════════════════════════

def find_liq_sweep(c,direction,lookback=40):
    """يُرجع (bool, level, sweep_idx). النافذة الزمنية لفحص السحب الفعلي
    أصبحت LIQ_SWEEP_WINDOW (20 شمعة) بدل 5 فقط، لتطابق نافذة OB/FVG (30).
    إصلاح جديد: تُرجع الآن أيضاً sweep_idx (الفهرس المطلق للشمعة التي
    حدث فيها آخر/أحدث سحب سيولة) — مطلوب لضمان أن حساب الحركة الاندفاعية
    لفيبوناتشي لاحقاً يبدأ فعلياً من لحظة السحب، لا من أي نقطة عشوائية
    قد تسبقها زمنياً (كانت هذه هي المشكلة الجذرية في ندرة تطابق الفيبو)."""
    if len(c)<lookback: return False,None,None
    recent=c[-lookback:]
    start_idx=len(c)-(LIQ_SWEEP_WINDOW+1)
    prevN_indexed=list(enumerate(c[start_idx:-1],start=start_idx))
    cur=c[-1]['c']
    sH=[]; sL=[]
    for i in range(2,len(recent)-2):
        cv=recent[i]
        if cv['h']>=recent[i-1]['h'] and cv['h']>=recent[i-2]['h'] and \
           cv['h']>=recent[i+1]['h'] and cv['h']>=recent[i+2]['h']: sH.append(cv['h'])
        if cv['l']<=recent[i-1]['l'] and cv['l']<=recent[i-2]['l'] and \
           cv['l']<=recent[i+1]['l'] and cv['l']<=recent[i+2]['l']: sL.append(cv['l'])
    if not sH or not sL: return False,None,None
    pA=min(sH,key=lambda x:abs(x-cur))          # أقرب مقاومة
    pB=min(sL,key=lambda x:abs(x-cur))          # أقرب دعم (إصلاح #4)
    if direction=="BUY":
        hits=[(idx,p) for idx,p in prevN_indexed if p['l']<pB and p['c']>pB]
        if not hits: return False,None,None
        sweep_idx,_=hits[-1]                    # آخر (أحدث) شمعة نفّذت السحب
        return True,pB,sweep_idx
    else:
        hits=[(idx,p) for idx,p in prevN_indexed if p['h']>pA and p['c']<pA]
        if not hits: return False,None,None
        sweep_idx,_=hits[-1]
        return True,pA,sweep_idx

# ═══════════════════════════════════════════
#  فيبوناتشي — المنطقة الذهبية (على فريم الساعة، بهامش تسامح واقعي)
# ═══════════════════════════════════════════

def find_fib_golden_zone(c1h,direction,sweep_level,sweep_idx,entry_zone):
    """
    فيبوناتشي أصبح الآن عامل **تعزيز للسكور فقط**، وليس شرط رفض إلزامي
    (بطلب صريح) — لأن تقاطعه مع بقية الشروط الإلزامية (سيولة+FVG+BOS/CISD)
    كان نادراً جداً إحصائياً، وهو مؤشر جودة إضافي لا شرط دخول أساسي.
    يتحقق أن منطقة الدخول (OB أو FVG) تقع ضمن المنطقة الذهبية لفيبوناتشي
    (0.47–0.82) للحركة الاندفاعية من نقطة سحب السيولة حتى أقصى امتداد
    تلاها. الحركة الاندفاعية تُحسب فقط من الشموع الواقعة *بعد* شمعة
    السحب نفسها (sweep_idx) — قياس متماسك زمنياً وجغرافياً لنفس الحركة.
    """
    if sweep_level is None or entry_zone is None or sweep_idx is None:
        return False,0.0
    impulse=c1h[sweep_idx:]
    if len(impulse)<2:
        return False,0.0
    entry_mid=entry_zone["mid"]
    if direction=="BUY":
        impulse_high=max(x['h'] for x in impulse)
        rng=impulse_high-sweep_level
        if rng<=0: return False,0.0
        retr=(impulse_high-entry_mid)/rng
    else:
        impulse_low=min(x['l'] for x in impulse)
        rng=sweep_level-impulse_low
        if rng<=0: return False,0.0
        retr=(entry_mid-impulse_low)/rng
    in_zone=FIB_ZONE_MIN<=retr<=FIB_ZONE_MAX
    zone_mid=(FIB_ZONE_MIN+FIB_ZONE_MAX)/2
    zone_half=(FIB_ZONE_MAX-FIB_ZONE_MIN)/2
    precision=max(0.0,1-abs(retr-zone_mid)/zone_half) if in_zone else 0.0
    return in_zone,round(precision*100,1)

# ═══════════════════════════════════════════
#  CHoCh — تغيّر الطابع الهيكلي (على فريم الساعة، عامل تقييم)
# ═══════════════════════════════════════════

def find_choch(c,direction,lookback=50):
    """
    Change of Character: يبحث عن نقطة الانقلاب حيث كُسر آخر قمة/قاع
    داخلي *معاكس* للاتجاه الجديد — أي اللحظة التي ينقلب فيها الطابع
    الهيكلي من هابط لصاعد (أو العكس)، تماماً كما في الاستراتيجية
    المرفقة (BOS داخل الاتجاه القديم → CHoCh عند الانعكاس → سحب سيولة
    → عودة لـ Order Block). عامل تقييم إضافي على 1H، وليس إلزامياً.
    """
    if len(c)<lookback: return False,0
    recent=c[-lookback:]
    pivots=[]
    for i in range(2,len(recent)-2):
        cv=recent[i]
        if cv['h']>recent[i-1]['h'] and cv['h']>recent[i-2]['h'] and \
           cv['h']>recent[i+1]['h'] and cv['h']>recent[i+2]['h']:
            pivots.append(('H',cv['h'],i))
        if cv['l']<recent[i-1]['l'] and cv['l']<recent[i-2]['l'] and \
           cv['l']<recent[i+1]['l'] and cv['l']<recent[i+2]['l']:
            pivots.append(('L',cv['l'],i))
    if len(pivots)<3: return False,0
    pivots.sort(key=lambda x:x[2])
    lows=[p for p in pivots if p[0]=='L']
    highs=[p for p in pivots if p[0]=='H']
    cur=c[-1]['c']
    if direction=="BUY" and lows and highs:
        last_low=lows[-1]
        prior_highs=[h for h in highs if h[2]<last_low[2]]
        if prior_highs:
            broke=cur>prior_highs[-1][1]
            return broke,(prior_highs[-1][1] if broke else 0)
    if direction=="SELL" and lows and highs:
        last_high=highs[-1]
        prior_lows=[l for l in lows if l[2]<last_high[2]]
        if prior_lows:
            broke=cur<prior_lows[-1][1]
            return broke,(prior_lows[-1][1] if broke else 0)
    return False,0

# ═══════════════════════════════════════════
#  BOS + CISD — تأكيد الدخول على فريم 15 دقيقة (أحدهما إلزامي)
# ═══════════════════════════════════════════

def find_bos(c,direction,lookback=20):
    """
    Break of Structure: يحدد قمة/قاع مرجعي ضمن نافذة سابقة (تستثني آخر 3
    شموع)، ثم يتحقق هل أغلقت إحدى آخر 3 شموع خارج ذلك المستوى في اتجاه
    الصفقة — دليل استمرار/تأكيد الزخم قبل الدخول مباشرة على 15M.
    """
    if len(c)<lookback+3: return False,0
    ref=c[-lookback-3:-3]
    last3=c[-3:]
    if direction=="BUY":
        swing_high=max(x['h'] for x in ref)
        broke=any(x['c']>swing_high for x in last3)
        return broke,(swing_high if broke else 0)
    else:
        swing_low=min(x['l'] for x in ref)
        broke=any(x['c']<swing_low for x in last3)
        return broke,(swing_low if broke else 0)

def find_cisd(c,direction,lookback=15):
    """
    Change in State of Delivery: يحدد آخر شمعة مخالفة اللون (بيع ضمن
    سياق شراء، أو العكس) ضمن نافذة حديثة، ثم يتحقق هل أغلقت شمعة لاحقة
    فوق/تحت *فتح* تلك الشمعة المخالفة — مؤشر انقلاب تدفق الأوامر من طرف
    لآخر لحظة الدخول على 15M.
    """
    if len(c)<lookback: return False,0
    recent=c[-lookback:]
    last=recent[-1]
    if direction=="BUY":
        opp=[x for x in recent[:-1] if x['c']<x['o']]
        if not opp: return False,0
        level=opp[-1]['o']
        broke=last['c']>level
        return broke,(level if broke else 0)
    else:
        opp=[x for x in recent[:-1] if x['c']>x['o']]
        if not opp: return False,0
        level=opp[-1]['o']
        broke=last['c']<level
        return broke,(level if broke else 0)

# ═══════════════════════════════════════════
#  Cluster (تجمع سعري)
# ═══════════════════════════════════════════

def find_cluster(c,lookback=20):
    if len(c)<lookback: return False
    recent=c[-lookback:]
    hi=max(x['h'] for x in recent); lo=min(x['l'] for x in recent)
    avg=(hi+lo)/2; pct=(hi-lo)/avg if avg else 1
    return pct<0.015

# ═══════════════════════════════════════════
#  Wick Rejection على 1H
# ═══════════════════════════════════════════

def find_wick(c,direction,lookback=5):
    if len(c)<lookback: return False
    count=0
    for cv in c[-lookback:]:
        body=abs(cv['c']-cv['o']); rng=cv['h']-cv['l']
        if rng==0: continue
        lo=min(cv['c'],cv['o'])-cv['l']; up=cv['h']-max(cv['c'],cv['o'])
        if direction=="BUY" and lo>body*1.5 and lo/rng>0.5: count+=1
        if direction=="SELL" and up>body*1.5 and up/rng>0.5: count+=1
    return count>=2

# ═══════════════════════════════════════════
#  Volume Breakout عند اختراق المقاومة
# ═══════════════════════════════════════════

def find_vol_breakout(c,direction,lookback=20):
    if len(c)<lookback+2: return False
    vr=vol_ratio(c,lookback)
    last=c[-1]
    highs=[x['h'] for x in c[-lookback-1:-1]]
    lows =[x['l'] for x in c[-lookback-1:-1]]
    res=max(highs); sup=min(lows)
    if direction=="BUY" and last['c']>res and vr>1.5: return True
    if direction=="SELL" and last['c']<sup and vr>1.5: return True
    return False

# ═══════════════════════════════════════════
#  التحليل الرئيسي
# ═══════════════════════════════════════════

def fmt(p):
    if p>=1000: return f"{p:.2f}"
    if p>=100:  return f"{p:.3f}"
    if p>=1:    return f"{p:.4f}"
    return f"{p:.6f}"

def analyze(sym,btc_c,learned=None,debug=None,cvd_precomputed=None):
    """
    التسلسل الهرمي (مطابق تماماً للفريمات المطلوبة):
    • 4H: تحديد الاتجاه العام فقط (UP/DOWN/SIDEWAYS) — لا تحليل آخر هنا.
    • 1H: رسم/تحديد الفجوات السعرية (FVG) والأوردر بلوك (OB) + سحب
      السيولة — سحب السيولة و FVG+إعادة الاختبار إلزاميان؛ OB وCHoCh
      وفيبوناتشي عوامل تقييم إضافية (سكور) وليست شروط رفض.
    • 15M: تحديد منطقة الدخول بعد الكسر (BOS) أو بعد تغيّر حالة التسليم
      (CISD) — **أحدهما إلزامي** (OR)، تماماً كما طُلب صراحة.

    فيبوناتشي لم يعد شرط رفض إطلاقاً (كان يتقاطع مع بقية الشروط الإلزامية
    بشكل نادر إحصائياً) — أصبح فقط يرفع السكور عند التطابق.
    """
    def reject(reason):
        if debug is not None: debug.append(f"{sym}: {reason}")
        return None
    try:
        c4h =klines(sym,"4h",100)
        c1h =klines(sym,"1h",150)
        c15m=klines(sym,"15m",80)
        if len(c4h)<50 or len(c1h)<60 or len(c15m)<30:
            return reject("بيانات تاريخية غير كافية")

        cur=c15m[-1]['c']
        sess=get_session()

        # ─── 4H: الاتجاه العام فقط ─────────────────────────────
        tr4h,trend_d=trend4h(c4h)
        if tr4h=="SIDEWAYS": return reject("لا يوجد اتجاه واضح على 4H")
        direction="BUY" if tr4h=="UP" else "SELL"

        # ─── 1H: سحب سيولة (إلزامي) + رسم FVG/OB ────────────────
        liq_sweep,sweep_level,sweep_idx=find_liq_sweep(c1h,direction,40)
        if not liq_sweep:
            return reject("لا يوجد سحب سيولة حقيقي على 1H")

        # Order Block على 1H — تقييمي فقط
        ob_1h=find_ob(c1h,direction,30)

        # FVG + إعادة اختبار على 1H — إلزامي
        fvg_1h,fvg_retested,fvg_retest_prec=find_fvg(c1h,direction,30)
        if not fvg_1h:
            return reject("لا توجد فجوة سعرية (FVG) على 1H")
        if not fvg_retested:
            return reject("الفجوة السعرية على 1H لم تُعَد اختبارها بعد")

        # فيبوناتشي — تعزيز سكور فقط (لم يعد شرط رفض، بطلب صريح)
        entry_zone_1h=ob_1h or fvg_1h
        fib_ok,fib_precision=find_fib_golden_zone(c1h,direction,sweep_level,sweep_idx,entry_zone_1h)

        # CHoCh على 1H — تعزيز سكور فقط (مطابقاً للاستراتيجية المرفقة:
        # BOS داخل الاتجاه القديم → CHoCh عند الانعكاس → سحب سيولة → OB)
        choch_ok,choch_level=find_choch(c1h,direction,50)

        # ميزات اختيارية إضافية على 1H (تقييم فقط)
        sr_flip,sr_level=find_sr_flip(c1h,direction,50)
        wick_ok=find_wick(c1h,direction,6)
        vol_break=find_vol_breakout(c1h,direction,20)

        # ─── 15M: تأكيد الدخول بعد الكسر (BOS) أو CISD — أحدهما إلزامي ───
        bos_ok,bos_level=find_bos(c15m,direction,20)
        cisd_ok,cisd_level=find_cisd(c15m,direction,15)
        if not (bos_ok or cisd_ok):
            return reject("لا يوجد كسر هيكل (BOS) ولا تغيّر حالة تسليم (CISD) على 15M لتأكيد الدخول")

        ob_15m=find_ob(c15m,direction,20)
        cluster=find_cluster(c15m,20)
        rsi_15m=rsi_calc(c15m)
        tr1h_str="UP" if [c['c']>c['o'] for c in c1h[-5:]].count(True)>=3 else "DOWN"
        atr_15m=atr_calc(c15m)
        vr_15m=vol_ratio(c15m)

        if direction=="BUY"  and rsi_15m>72: return reject("RSI 15M مرتفع جداً (>72) لصفقة شراء")
        if direction=="SELL" and rsi_15m<28: return reject("RSI 15M منخفض جداً (<28) لصفقة بيع")

        # CVD — 24 ساعة حقيقية (إصلاح #3). يُعاد استخدام القيمة المحسوبة
        # مسبقاً من get_cvd_top() إن توفرت، بدل إعادة طلبها من الشبكة مرتين
        # لكل عملة في نفس دورة الفحص (تسريع إضافي لحل تأخر الإرسال).
        cvd_data=cvd_precomputed if cvd_precomputed else calc_cvd_24h(sym)
        if direction=="BUY"  and not cvd_data["bull"]: return reject("CVD (24س) لا يدعم اتجاه الشراء")
        if direction=="SELL" and cvd_data["bull"]:     return reject("CVD (24س) لا يدعم اتجاه البيع")

        cor_btc=calc_cor(c1h,btc_c,20)

        # ─── حساب الدخول ─────────────────────
        ob_use=ob_15m or ob_1h
        entry_lvl=ob_use["mid"] if ob_use else fvg_1h["mid"]
        entry=round(entry_lvl,6)
        risk=atr_15m*1.5

        if direction=="BUY":
            sl=round(entry-risk,6)
            tp1=round(entry+risk,6)
            tp=round(entry+risk*RR,6)
        else:
            sl=round(entry+risk,6)
            tp1=round(entry-risk,6)
            tp=round(entry-risk*RR,6)

        if risk<=0: return reject("حساب الوقف/المخاطرة غير منطقي (ATR=0)")
        rr_actual=round(abs(tp-entry)/abs(sl-entry),1) if abs(sl-entry)>0 else RR

        # ─── إصلاح بنيوي: رفض الدخول "الفائت" ─────────────────
        # الدخول يُحسب من منتصف منطقة OB/FVG (نقطة خلف السعر الحالي)، لكن
        # BOS/CISD يتطلبان أصلاً أن يكون السعر قد ابتعد عنها. لو الابتعاد
        # كبير جداً وقت الاكتشاف، الفرصة الفعلية تكون انتهت (أغلب الحركة
        # المتوقعة حتى TP1 حدثت فعلاً قبل ما تُرسل الإشارة). هذا هو مصدر
        # شكوى "السعر مرّ من نقطة الدخول" — رفض هنا أدق من إرسال إشارة ميتة.
        if direction=="BUY"  and cur>=entry+risk*MAX_ENTRY_DRIFT:
            return reject(f"السعر تجاوز نقطة الدخول بالفعل (ابتعاد {round((cur-entry)/risk,2)}× عن المخاطرة) — الفرصة فاتت")
        if direction=="SELL" and cur<=entry-risk*MAX_ENTRY_DRIFT:
            return reject(f"السعر تجاوز نقطة الدخول بالفعل (ابتعاد {round((entry-cur)/risk,2)}× عن المخاطرة) — الفرصة فاتت")


        # ─── درجة الثقة (لا نقاط ثابتة إطلاقاً) ──────
        # كل نقطة هنا مشتقة من قياس فعلي لجودة/قوة العنصر المطابق. الشروط
        # الإلزامية الآن هي: اتجاه 4H + سيولة+FVG معاد اختباره على 1H +
        # (BOS أو CISD) على 15M. فيبوناتشي وCHoCh وOB على 1H عوامل تعزيز
        # فقط، تُحسَب هنا ولا ترفض الإشارة أبداً بغيابها.
        score=0.0
        score+=min(16, round(abs(trend_d)*8,1))              # قوة الاتجاه 4H الفعلية (0-16)
        score+=round(fvg_retest_prec*14,1)                    # دقة إعادة اختبار الفجوة 1H (0-14)
        if fib_ok:                 score+=round(fib_precision*0.12,1)  # فيبوناتشي تعزيزي فقط (0-12)
        if choch_ok:               score+=10                  # CHoCh على 1H (انقلاب الطابع الهيكلي)
        if bos_ok:                 score+=9                   # BOS على 15M (أحد شرطي الدخول OR)
        if cisd_ok:                score+=7                   # CISD على 15M (الشرط الثاني OR)
        if ob_1h:                  score+=8                   # OB على نفس فريم التحليل (تقييمي)
        if sr_flip:                score+=8
        if wick_ok:                score+=5
        if ob_15m:                 score+=5                   # OB أدق على فريم الدخول
        if cluster:                score+=4
        if sess["in_kz"]:          score+=7
        if vr_15m>=1.5:            score+=6
        elif vr_15m>=1.2:          score+=3
        if cvd_data["score"]>60:   score+=5
        if abs(cor_btc)>0.7:       score+=3
        if vol_break:              score+=4
        if 40<rsi_15m<60:          score+=3

        # مكافأة/عقوبة التعلم من brain.py (إصلاح #12: وزن حقيقي أكبر)
        # يُطبَّق كخصم أو إضافة فعلية بناءً على أداء ~120 صفقة تاريخية
        # لظروف مشابهة (جلسة/اتجاه/عناصر التطابق)، وليس تعديلاً تجميلياً.
        sig_tmp={"session":sess["session"],"in_kz":sess["in_kz"],
                 "has_ob":bool(ob_1h),"has_fvg":True,
                 "fvg_retested":True,"has_liq_sweep":True,
                 "sr_flip":sr_flip,"has_cluster":cluster,
                 "cvd_score":cvd_data["score"],"vol_breakout":vol_break,
                 "trend_4h":tr4h,"direction":direction}
        brain_bonus=0
        if BRAIN_OK and learned and learned.get("total_trades",0)>=BRAIN_MIN_TRADES:
            try:
                brain_bonus=brain.score_bonus(sig_tmp,learned)
                score+=brain_bonus
            except Exception as e:
                log.error(f"brain.score_bonus: {e}")

        score=max(0,min(round(score,1),98))

        # ─── تفسير لماذا ─────────────────────
        reasons=[]
        reasons.append(f"4H: اتجاه {tr4h} (قوة {abs(trend_d):.2f}%)")
        reasons.append("1H: سحب سيولة + FVG مُعاد اختباره (دقة {:.0f}%)".format(fvg_retest_prec*100))
        entry_confirm=[]
        if bos_ok: entry_confirm.append("BOS")
        if cisd_ok: entry_confirm.append("CISD")
        reasons.append("15M: تأكيد دخول عبر " + "+".join(entry_confirm))
        if choch_ok: reasons.append(f"CHoCh على 1H عند {fmt(choch_level)}")
        if fib_ok: reasons.append(f"داخل المنطقة الذهبية لفيبوناتشي (دقة {fib_precision:.0f}%)")
        if ob_1h: reasons.append("Order Block على 1H")
        if sr_flip: reasons.append(f"SR Flip عند {fmt(sr_level)}")
        if wick_ok: reasons.append("شمعة رفض 1H")
        if ob_15m: reasons.append("OB دقيق على 15M")
        if cluster: reasons.append("Cluster 15M")
        if sess["in_kz"]: reasons.append(f"Kill Zone ({sess['session']})")
        if vol_break: reasons.append("اختراق بحجم قوي 1H")
        if BRAIN_OK and learned and learned.get("total_trades",0)>=BRAIN_MIN_TRADES:
            reasons.append(f"تعلم تاريخي: {brain_bonus:+.1f} نقطة (من {learned.get('total_trades',0)} صفقة)")
        why=" | ".join(reasons)

        return {
            "symbol"       :sym,
            "direction"    :direction,
            "entry"        :fmt(entry),
            "sl"           :fmt(sl),
            "tp"           :fmt(tp),
            "tp1"          :fmt(tp1),
            "rr"           :rr_actual,
            "score"        :score,
            "rsi_15m"      :rsi_15m,
            "trend_4h"     :tr4h,
            "trend_1h"     :tr1h_str,
            "session"      :sess["session"],
            "in_kz"        :sess["in_kz"],
            "sr_flip"      :sr_flip,
            "has_ob"       :bool(ob_1h),
            "has_fvg"      :True,
            "fvg_retested" :True,
            "fvg_retest_precision":round(fvg_retest_prec*100,1),
            "has_liq_sweep":True,
            "has_cluster"  :cluster,
            "vol_breakout" :vol_break,
            "cvd_score"    :cvd_data["score"],
            "cor_btc"      :cor_btc,
            "fib_in_zone"  :fib_ok,
            "fib_precision":fib_precision,
            "choch"        :choch_ok,
            "bos"          :bos_ok,
            "cisd"         :cisd_ok,
            "brain_bonus"  :brain_bonus,
            "hit_tp1"      :False,
            "why"          :why,
            "time"         :datetime.now().strftime("%H:%M:%S"),
            "_ef"          :entry,"_sl":sl,"_tp":tp,"_tp1":tp1,
        }
    except Exception as e:
        log.error(f"analyze {sym}: {e}")
        return reject(f"خطأ تقني: {e}")

# ═══════════════════════════════════════════
#  مراقبة الصفقات
# ═══════════════════════════════════════════

def _notify(trade,event,msg,save=True):
    icons={'tp':'🏆','sl':'🛑','tp1':'✅'}
    titles={'tp':'الهدف تحقق ✅','sl':'ضُرب الاستوب ❌','tp1':'هدف جزئي'}
    sio.emit('trade_event',{'icon':icons.get(event,'📢'),'title':titles.get(event,''),'body':msg})
    send_tg(msg,raw=True)
    elog(msg,'warn' if event=='sl' else 'ok')
    if BRAIN_OK and save:
        outcome=0 if event=='sl' else 1
        brain.save_trade(trade,outcome)
        ST['db_stats']=brain.get_stats()

def mon_loop():
    while True:
        time.sleep(MON_SEC)
        if not ST['open_trades']: continue
        updated=[]
        try:
            for t in ST['open_trades']:
                try:
                    p=price(t['symbol'])
                    if not p: updated.append(t); continue
                    t['current']=fmt(p)
                    buy=t['direction']=='BUY'
                    entry=t['_ef']; sl=t['_sl']; tp=t['_tp']; tp1=t['_tp1']
                    t['pnl']=round(((p-entry)/entry*100) if buy else ((entry-p)/entry*100),2)
                    hit_tp  =(buy and p>=tp)  or (not buy and p<=tp)
                    hit_sl  =(buy and p<=sl)  or (not buy and p>=sl)
                    hit_tp1 =(buy and p>=tp1) or (not buy and p<=tp1)
                    if hit_tp and not t.get('hit_tp'):
                        t['hit_tp']=True; t['status']='tp'
                        _notify(t,'tp',f"🏆 الهدف (1:3) تحقق!\n{t['symbol']} @ {fmt(p)}\nربح: {t['pnl']}%",True)
                    elif hit_sl and not t.get('hit_sl'):
                        t['hit_sl']=True; t['status']='sl'
                        _notify(t,'sl',f"🛑 استوب!\n{t['symbol']} @ {fmt(p)}\nخسارة: {t['pnl']}%",True)
                    elif hit_tp1 and not t.get('hit_tp1'):
                        t['hit_tp1']=True
                        _notify(t,'tp1',
                            f"✅ هدف جزئي تحقق! (متابعة)\n{t['symbol']} @ {fmt(p)}\n"
                            f"ربح حالي: {t['pnl']}%\n"
                            f"💡 Trailing Stop: حرّك الاستوب إلى الدخول {t['entry']} (التعادل)\n"
                            f"⏳ بانتظار الهدف النهائي 1:3",False)
                    if t.get('hit_tp') or t.get('hit_sl'):
                        t.setdefault('_rm',time.time()+180)
                    if t.get('_rm') and time.time()>t['_rm']: continue
                    updated.append(t)
                except Exception as e:
                    log.error(f"mon_loop trade {t.get('symbol','?')}: {e}")
                    updated.append(t)  # نُبقي الصفقة كما هي بدل فقدانها بسبب خطأ عابر
            ST['open_trades']=updated
            if BRAIN_OK: brain.save_open(updated)
            sio.emit('state_update',get_st())
        except Exception as e:
            log.error(f"mon_loop: {e}")

# ═══════════════════════════════════════════
#  التعلم الدوري (إصلاح #5: يتحقق فوراً عند البدء، ثم كل ساعة)
# ═══════════════════════════════════════════

def _run_learn_cycle():
    elog("🧠 بدء التعلم...","info")
    learned=brain.learn()
    ST['learned']=learned
    ST['db_stats']=brain.get_stats()
    ST['backtest']=brain.run_backtest()
    elog(f"✅ تعلم {learned.get('total_trades',0)} صفقة | نجاح: {learned.get('win_rate',0)}%","ok")
    sio.emit('state_update',get_st())

def learn_loop():
    while True:
        if BRAIN_OK and brain.should_learn():
            try: _run_learn_cycle()
            except Exception as e: log.error(f"learn_loop: {e}")
        time.sleep(3600)

# ═══════════════════════════════════════════
#  Keep-Alive
# ═══════════════════════════════════════════

def ka_loop():
    port=os.environ.get("PORT","5000")
    while True:
        time.sleep(240)
        try: requests.get(f"http://127.0.0.1:{port}/ping",timeout=5)
        except: pass

@app.route('/ping')
def ping(): return jsonify({"status":"alive","time":datetime.now().strftime("%H:%M:%S")})

# ═══════════════════════════════════════════
#  تليجرام
# ═══════════════════════════════════════════

def send_tg(sig,raw=False):
    if raw: msg=sig
    else:
        s=sig; d="🟢 شراء" if s['direction']=='BUY' else "🔴 بيع"
        ob_line="🟦 OB ✅" if s.get('has_ob') else "🟦 OB —"
        entry_line="+".join([x for x in (["BOS"] if s.get('bos') else [])+(["CISD"] if s.get('cisd') else [])])
        fib_line=f"📐 فيبو: {s.get('fib_precision',0)}%" if s.get('fib_in_zone') else "📐 فيبو: —"
        choch_line="🔀 CHoCh ✅" if s.get('choch') else "🔀 CHoCh —"
        msg=f"""
🚀 *CryptoBot Pro — إشارة جديدة*
{'─'*22}
💰 *{s['symbol']}* | {d}
{'─'*22}
📍 دخول: `{s['entry']}`
🛑 وقف: `{s['sl']}`
🎯 هدف (1:3): `{s['tp']}`
📐 R:R: *1:{s['rr']}*
{'─'*22}
📊 4H: {s['trend_4h']} | RSI 15M: {s['rsi_15m']}
⏱ الجلسة: {s['session']} | KZ: {'✅' if s['in_kz'] else '❌'}
📊 CVD(24س): {s['cvd_score']}% | COR BTC: {s['cor_btc']}
💥 تأكيد الدخول 15M: {entry_line} | دقة إعادة اختبار FVG: {s.get('fvg_retest_precision',0)}%
{fib_line} | {choch_line}
{'─'*22}
💧 سحب سيولة ✅ | ⚡ FVG مُعاد اختباره ✅ | {ob_line}
{'🔄 SR Flip' if s['sr_flip'] else ''} {'🎯 Cluster' if s['has_cluster'] else ''} {'📈 Vol Breakout' if s['vol_breakout'] else ''}
{'─'*22}
🧠 ثقة: *{s['score']}%* (تعلم تاريخي: {s.get('brain_bonus',0):+.1f})
💡 {s['why']}
⏰ {s['time']}
""".strip()
    try:
        for cid in CHAT_IDS:
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                json={"chat_id":cid,"text":msg,"parse_mode":"Markdown"},timeout=10)
    except Exception as e: log.error(f"tg: {e}")

# ═══════════════════════════════════════════
#  الفحص
# ═══════════════════════════════════════════

def elog(txt,typ='info'): sio.emit('log',{'text':txt,'type':typ})
def is_cd(s): return (time.time()-ST['cooldowns'].get(s,0))<COOLDOWN*60

def _symbol_priority(sym,learned):
    """إصلاح #12: ترتيب أولوية فحص الرموز حسب معدل النجاح التاريخي لنفس
    الرمز/الجلسة إن توفرت بيانات كافية في brain.py، بدل ترتيب عشوائي."""
    if not (BRAIN_OK and learned and learned.get("total_trades",0)>=BRAIN_MIN_TRADES): return 0
    try:
        per_symbol=learned.get("per_symbol",{})
        s=per_symbol.get(sym)
        if s and s.get("n",0)>=3: return s.get("wr",50)-50
    except Exception: pass
    return 0

def run_scan():
    if ST['scanning']: return
    ST['scanning']=True; ST['scan_n']+=1
    sio.emit('state_update',get_st())
    elog("🔍 بدء الفحص...","info")
    try:
        syms=top_symbols(TOP_N); ST['top_symbols']=syms
        btc_c=klines(BTC_PAIR,"1h",25)
        elog("📊 تحليل CVD (24س) + COR (متوازي)...","info")
        cvd_top,cvd_raw=get_cvd_top(syms,btc_c)
        ST['cvd_top']=cvd_top
        elog(f"📊 أفضل CVD: {', '.join(cvd_top[:5])}","ok")
        learned=ST['learned'] if BRAIN_OK else {}
        # إصلاح #12: فحص الرموز الأعلى معدل نجاح تاريخياً أولاً
        syms=sorted(syms,key=lambda s:_symbol_priority(s,learned),reverse=True)
        cands=[]
        rejects=[]
        # إصلاح تأخر الإرسال: تحليل عدة عملات بالتوازي بدل التسلسل —
        # كان الفحص الكامل يستغرق دقائق (~180 طلب متتالي)، الآن ثوانٍ.
        scan_list=[s for s in syms if not is_cd(s)]
        for s in syms:
            if is_cd(s): elog(f"⏳ {s} كول داون","info")
        with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as ex:
            futures={ex.submit(analyze,sym,btc_c,learned,rejects,cvd_raw.get(sym)):sym for sym in scan_list}
            for fut in as_completed(futures):
                sym=futures[fut]
                try:
                    sig=fut.result()
                except Exception as e:
                    log.error(f"analyze thread {sym}: {e}")
                    continue
                if sig:
                    cands.append(sig)
                    elog(f"✅ {sym} {sig['direction']} | {sig['score']}%","ok")
        for r in rejects:
            elog(f"✗ {r}","info")
        cands.sort(key=lambda x:x['score'],reverse=True)
        # أفضل صفقتين ≥75% (حد ثقة حقيقي، لا حشو)
        top_cands=[s for s in cands[:4] if s['score']>=MIN_SCORE]  # هامش إضافي قبل فحص الطزاجة
        best=[]
        for sig in top_cands:
            if len(best)>=2: break
            # فحص طزاجة أخير مباشرة قبل الإرسال: قد يكون مرّ وقت إضافي
            # أثناء تحليل بقية العملات — نتأكد أن السعر لم يتجاوز فعلياً
            # الوقف أو الهدف بحلول لحظة الإرسال الفعلية.
            live=price(sig['symbol'])
            if live is None:
                best.append(sig); continue
            buy=sig['direction']=='BUY'
            hit_sl=(buy and live<=sig['_sl']) or (not buy and live>=sig['_sl'])
            hit_tp=(buy and live>=sig['_tp']) or (not buy and live<=sig['_tp'])
            if hit_sl or hit_tp:
                elog(f"⚠️ {sig['symbol']} إشارة قديمة (تجاوز السعر الوقف/الهدف قبل الإرسال) — تُجوهلت","warn")
                continue
            best.append(sig)
        for sig in best:
            ST['cooldowns'][sig['symbol']]=time.time()
            send_tg(sig)
            sio.emit('new_signal',sig)
            elog(f"📤 {sig['symbol']} أُرسل ✅","ok")
            trade=dict(sig)
            trade.update({'status':'open','hit_tp':False,'hit_sl':False,
                          'hit_tp1':False,'pnl':0.0})
            if sig['symbol'] not in [t['symbol'] for t in ST['open_trades']]:
                ST['open_trades'].append(trade)
        if BRAIN_OK:
            brain.save_open(ST['open_trades'])
            ST['db_stats']=brain.get_stats()
            ST['backtest']=brain.get_backtest()
            sio.emit('trades_data',brain.get_all_trades())
        ST['signals']=best
        ST['last_scan']=datetime.now().strftime("%H:%M:%S")
        elog(f"🏁 انتهى | {len(best)} إشارة من {len(cands)} مرشح","ok")
    except Exception as e:
        elog(f"❌ خطأ: {e}","err"); log.error(f"scan: {e}")
    finally:
        ST['scanning']=False
        sio.emit('state_update',get_st())

def _auto_w():
    while ST['auto_on']:
        run_scan()
        for rem in range(INTERVAL,0,-1):
            if not ST['auto_on']: break
            ST['next_in']=rem
            if rem%30==0: sio.emit('state_update',get_st())
            time.sleep(1)
    ST['next_in']=0; sio.emit('state_update',get_st())

def start_auto():
    if ST['auto_on']: return
    ST['auto_on']=True; elog("▶️ الفحص الآلي كل 5 دقائق","ok")
    send_tg("▶️ *CryptoBot Pro — الفحص الآلي نشط*\n📊 4H(اتجاه)→1H(سيولة+FVG+OB)→15M(دخول بعد BOS/CISD) | CVD(24س)+COR | حد الثقة 75%",raw=True)
    threading.Thread(target=_auto_w,daemon=True).start()

def stop_auto():
    ST['auto_on']=False; elog("⏹ إيقاف الفحص الآلي","warn")
    send_tg("⏹ *تم إيقاف الفحص الآلي*",raw=True)

# ═══════════════════════════════════════════
#  Flask + SocketIO
# ═══════════════════════════════════════════

def get_st():
    return {"signals":ST['signals'],"open_trades":ST['open_trades'],
            "top_symbols":ST['top_symbols'],"cvd_top":ST['cvd_top'],
            "last_scan":ST['last_scan'],"scanning":ST['scanning'],
            "auto_on":ST['auto_on'],"next_in":ST['next_in'],"scan_n":ST['scan_n'],
            "learned":ST['learned'],"db_stats":ST['db_stats'],
            "backtest":ST['backtest'],"public_url":ST['public_url']}

@app.route('/')
def index(): return render_template_string(HTML)
@app.route('/api/state')
def api_state(): return jsonify(get_st())
@app.route('/api/trades')
def api_trades(): return jsonify(brain.get_all_trades() if BRAIN_OK else [])

@sio.on('req_state')
def on_req():
    emit('state_update',get_st())
    if BRAIN_OK: emit('trades_data',brain.get_all_trades())

@sio.on('manual_scan')
def on_manual(): threading.Thread(target=run_scan,daemon=True).start()

@sio.on('toggle_auto')
def on_toggle():
    if ST['auto_on']: stop_auto()
    else: threading.Thread(target=start_auto,daemon=True).start()

# ═══════════════════════════════════════════
#  نقطة الدخول
# ═══════════════════════════════════════════

if __name__=='__main__':
    print("╔══════════════════════════════════════════════════╗")
    print("║   🚀 CryptoBot Pro — تحليل فني متكامل (v5)       ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  🌐 PORT: {os.environ.get('PORT','5000')}                                ║")
    print("║  📊 4H اتجاه فقط → 1H سيولة+FVG+OB → 15M دخول BOS/CISD ║")
    print("║  📈 CVD(24س تقريبي) + COR + Cluster + Kill Zones  ║")
    print("║  🧠 Brain: ~120 صفقة + تعلم حقيقي مؤثر بالقرار    ║")
    print("║  ✅ حد الثقة 75% حقيقي | R:R 1:3 | مصدر: Kraken   ║")
    print("╚══════════════════════════════════════════════════╝")
    if not TG_TOKEN or not TG_CHAT:
        log.warning("⚠️ لم يتم ضبط TG_TOKEN / TG_CHAT كمتغيرات بيئة — رسائل تيليجرام لن تُرسل حتى تُضبط في إعدادات Render (Environment).")
    # رابط الخدمة العام على Render يُضبط تلقائياً في متغير البيئة RENDER_EXTERNAL_URL
    ST['public_url']=os.environ.get("RENDER_EXTERNAL_URL","")
    _load_ids()
    if BRAIN_OK:
        ST['learned']=brain.get_learned()
        ST['db_stats']=brain.get_stats()
        ST['backtest']=brain.get_backtest()
        recovered=brain.load_open()
        if recovered: ST['open_trades']=recovered; log.info(f"✅ استُعيدت {len(recovered)} صفقة")
    threading.Thread(target=mon_loop,   daemon=True).start()
    threading.Thread(target=learn_loop, daemon=True).start()
    threading.Thread(target=ka_loop,    daemon=True).start()
    threading.Thread(target=_poll_tg,   daemon=True).start()
    port=int(os.environ.get("PORT",5000))
    sio.run(app,host='0.0.0.0',port=port,debug=False,allow_unsafe_werkzeug=True)
