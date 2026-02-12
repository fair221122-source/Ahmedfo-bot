import pandas as pd
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio
from twelvedata import TDClient
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- الإعدادات ---
TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0" 
API_KEY = "5a983de3d79043e9bfb2ec2e8618f905"

FOREX_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY', 'EUR/JPY', 
    'AUD/JPY', 'USD/CAD', 'EUR/GBP', 'GBP/AUD', 
    'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'GBP/CAD'
]

td = TDClient(apikey=API_KEY)

# --- سيرفر وهمي لـ Render (Health Check) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Successfully")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# --- منطق التحليل المعدل ---
def analyze_strategy(pair):
    try:
        ts = td.time_series(symbol=pair, interval="5min", outputsize=40)
        df = ts.as_pandas()
        if df.empty or len(df) < 30: return None
        df = df.sort_index(ascending=True)
        lookback = df.iloc[-31:-1].copy()
        
        green_count = len(lookback[lookback['close'] > lookback['open']])
        red_count = len(lookback[lookback['close'] < lookback['open']])
        
        if green_count >= 18:
            trend, dom_ratio = "BUY", green_count / 30
        elif red_count >= 18:
            trend, dom_ratio = "SELL", red_count / 30
        else:
            return None

        target_candles = lookback[lookback['close'] > lookback['open']] if trend == "BUY" else lookback[lookback['close'] < lookback['open']]
        body_eff = (abs(target_candles['close'] - target_candles['open']) / (target_candles['high'] - target_candles['low'])).mean() * 100
        score = int((dom_ratio * 50) + (body_eff * 0.5))
        
        if score >= 85: label, expiry = "ممتااازة", "3 دقائق"
        elif score >= 70: label, expiry = "جيدة جداً", "3 دقائق"
        elif score >= 65: label, expiry = "جيدة", "5 دقائق"
        elif score >= 40: label, expiry = "مقبولة", "7 دقائق"
        else: label, expiry = "ضعيفة", "10 دقائق"

        return {"pair": pair, "trend": trend, "score": score, "label": label, "expiry": expiry, "price": float(df['close'].iloc[-1]), "emoji": "🟢" if trend == "BUY" else "🔴"}
    except: return None

async def start_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بدأت فحص الـ 13 زوجاً.. سأستغرق دقيقتين لتجنب الحظر ⏳")
    all_signals = []
    riyadh_time = datetime.utcnow() + timedelta(hours=3)
    
    for pair in FOREX_PAIRS:
        res = analyze_strategy(pair)
        if res: all_signals.append(res)
        await asyncio.sleep(9.0) 

    all_signals = sorted(all_signals, key=lambda x: x['score'], reverse=True)[:3]
    if not all_signals:
        await update.message.reply_text("عفواً ... لا توجد إشارات قوية حالياً.")
        return

    response = "🎯 أفضل 3 إشارات متوفرة حالياً:\n----------------------------------------\n"
    for s in all_signals:
        response += f"{s['emoji']} {s['pair']}\n📈 {s['trend']}\n💰 {s['price']:.5f} (مطابق)\n💪 قوة الإشارة: {s['label']} {s['score']}%\n⏱️ الوقت: {s['expiry']}\n📅 {riyadh_time.strftime('%Y-%m-%d')} | {riyadh_time.strftime('%I:%M:%S %p')}\n----------------------------------------\n"
    response += "GOOD LUCK AHMED 👍"
    await update.message.reply_text(response)

if __name__ == '__main__':
    # تشغيل سيرفر الـ Health Check
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # تهيئة بيئة العمل
    nest_asyncio.apply()
    
    # بناء التطبيق
    application = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة الأوامر
    application.add_handler(CommandHandler('start', start_analysis))
    application.add_handler(CommandHandler('signals', start_analysis))
    
    print("🚀 البوت ينطلق الآن على نسخة مستقرة...")
    
    # تشغيل البوت مع إعدادات حماية من أخطاء الاتصال
    application.run_polling(drop_pending_updates=True, stop_signals=None)
