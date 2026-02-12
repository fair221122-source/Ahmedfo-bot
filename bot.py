import yfinance as yf
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 1. إعدادات البوت
TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0" # ضع التوكن بالكامل هنا

FOREX_PAIRS = [
    'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'GBPJPY=X', 'EURJPY=X', 
    'AUDUSD=X', 'AUDJPY=X', 'USDCAD=X', 'EURGBP=X', 'GBPAUD=X', 
    'CADJPY=X', 'CHFJPY=X', 'EURCAD=X', 'GBPCAD=X', 'AUDCAD=X'
]

def get_signal_details(score):
    if score >= 85: return "ممتااازة", "3 دقائق", score
    if score >= 70: return "جيدة جداً", "3 دقائق", score
    if score >= 65: return "جيدة", "5 دقائق", score
    if score >= 40: return "مقبولة", "7 دقائق", score
    return "ضعيفة", "10 دقائق", score

def analyze_strategy(pair):
    try:
        data = yf.download(pair, period='1d', interval='5m', progress=False)
        if data.empty or len(data) < 30: return None
        
        lookback = data.iloc[-31:-1]
        green_count = len(lookback[lookback['Close'] > lookback['Open']])
        red_count = len(lookback[lookback['Close'] < lookback['Open']])
        
        if green_count >= 18:
            trend = "BUY"
            dom_ratio = green_count / 30
        elif red_count >= 18:
            trend = "SHORT"
            dom_ratio = red_count / 30
        else:
            return None

        target_candles = lookback[lookback['Close'] > lookback['Open']] if trend == "BUY" else lookback[lookback['Close'] < lookback['Open']]
        body_eff = (abs(target_candles['Close'] - target_candles['Open']) / (target_candles['High'] - target_candles['Low'])).mean() * 100
        
        score = int((dom_ratio * 50) + (body_eff * 0.5))
        label, expiry, final_score = get_signal_details(score)
        
        current_price = float(data['Close'].iloc[-1])
        riyadh_time = datetime.utcnow() + timedelta(hours=3)
        formatted_time = riyadh_time.strftime("%I:%M:%S %p")
        formatted_date = riyadh_time.strftime("%Y-%m-%d")

        return {
            "pair": pair.replace('=X', ''),
            "dir_emoji": "🟢" if trend == "BUY" else "🔴",
            "trend": trend,
            "price": current_price,
            "label": label,
            "score": final_score,
            "expiry": expiry,
            "time": formatted_time,
            "date": formatted_date
        }
    except:
        return None

async def start_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("جارِ تحليل السوق، إنتظر ثواني ...⏳")
    
    all_signals = []
    for pair in FOREX_PAIRS:
        res = analyze_strategy(pair)
        if res: all_signals.append(res)
    
    all_signals = sorted(all_signals, key=lambda x: x['score'], reverse=True)[:3]

    if not all_signals:
        await update.message.reply_text("عفواً ... لا توجد إشارات نشطة حالياً ...")
        return

    response = "🎯 أفضل 3 إشارات متوفرة حالياً:\n"
    for s in all_signals:
        price_formated = "{:.5f}".format(s['price'])
        response += f"{s['dir_emoji']} {s['pair']}\n"
        response += f"📈 {s['trend']}\n"
        response += f"💰 {price_formated}\n"
        response += f"💪 قوة الإشارة: {s['label']} {s['score']}%\n"
        response += f"⏱️ الوقت: {s['expiry']}\n"
        response += f"📅 {s['date']} | {s['time']}\n"
        response += "----------------------------------------\n"
    
    response += "GOOD LUCK AHMED 👍"
    await update.message.reply_text(response)

if __name__ == '__main__':
    # التشغيل بنظام polling المباشر لبيئة Render المستقرة
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start_analysis))
    application.add_handler(CommandHandler('signals', start_analysis))
    print("✅ البوت يعمل الآن بنظام الترند وتوقيت الرياض على Render.")
    application.run_polling()
