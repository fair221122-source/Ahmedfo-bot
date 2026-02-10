import os
import yfinance as yf
import telebot
import pandas as pd
import numpy as np
import time
from flask import Flask
import threading

# --- إعداد السيرفر لـ Render ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# --- إعدادات البوت ---
TELEGRAM_TOKEN = "8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

SYMBOLS = [
    'AUDCAD=X', 'AUDCHF=X', 'AUDJPY=X', 'AUDNZD=X', 'AUDUSD=X',
    'CADCHF=X', 'CADJPY=X', 'CHFJPY=X', 'EURAUD=X', 'EURCAD=X',
    'EURCHF=X', 'EURGBP=X', 'EURJPY=X', 'EURNZD=X', 'EURUSD=X',
    'GBPAUD=X', 'GBPCAD=X', 'GBPCHF=X', 'GBPJPY=X', 'GBPNZD=X', 
    'GBPUSD=X', 'NZDCHF=X', 'NZDJPY=X', 'NZDUSD=X', 'USDCAD=X', 
    'USDCHF=X', 'USDJPY=X'
]

@bot.message_handler(commands=['signals', 'start'])
def handle(message):
    bot.send_message(message.chat.id, "🎯 جاري فحص السوق واستخراج أفضل الإشارات...")
    try:
        data = yf.download(tickers=SYMBOLS, period='1d', interval='1m', group_by='ticker', progress=False)
        results = []

        for s in SYMBOLS:
            df = data[s].dropna()
            if df.empty or len(df) < 15: continue
            
            close, open_val = df['Close'].iloc[-1], df['Open'].iloc[-1]
            avg_move = np.mean(np.abs(df['Close'] - df['Open']).iloc[-15:-1]) + 1e-9
            score = abs(close - open_val) / avg_move
            
            if score > 0.8:
                trend_up = close > df['Close'].iloc[-10:].mean()
                results.append({
                    "pair": s.replace("=X", ""),
                    "dir": "🟢 BUY" if trend_up else "🔴 SELL",
                    "emoji": "📈" if trend_up else "📉",
                    "price": f"{close:.5f}",
                    "score_val": score
                })

        if not results:
            bot.send_message(message.chat.id, "⚠️ السوق هادئ حالياً، لا توجد إشارات قوية.")
            return

        top = sorted(results, key=lambda x: x["score_val"], reverse=True)[:3]
        
        response = "🎯 **أفضل الإشارات المتوفرة حالياً:**\n\n"
        for item in top:
            # تحديد قوة الإشارة بناءً على الرقم
            if item['score_val'] > 2.0: strength, t = "قوية جداً 🔥", "1 دقيقة"
            elif item['score_val'] > 1.2: strength, t = "قوية 💪", "3 دقائق"
            else: strength, t = "متوسطة ⚡", "5 دقائق"

            response += f"{item['dir']} **{item['pair']}**\n"
            response += f"{item['emoji']} {item['dir'].split()[1]}\n"
            response += f"💰 {item['price']}\n"
            response += f"💪 قوة الإشارة: {strength}\n"
            response += f"⏱️ الوقت: {t}\n"
            response += "-------------------\n"
        
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, "❌ حدث خطأ في جلب البيانات، يرجى المحاولة لاحقاً.")

bot.remove_webhook()
bot.infinity_polling()
