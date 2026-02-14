import os
import telebot
from twelvedata import TDClient
from datetime import datetime, timedelta

# سحب المفاتيح من إعدادات GitHub Secrets (أمان عالي)
TOKEN = os.getenv("8433924343:AAEzACCdtfJK_lwof5vbCbCGAavxi_w5iV0")
API_KEY = os.getenv("5a983de3d79043e9bfb2ec2e8618f905")

FOREX_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'GBP/JPY', 'EUR/JPY', 
    'AUD/JPY', 'USD/CAD', 'EUR/GBP', 'GBP/AUD', 
    'CAD/JPY', 'CHF/JPY', 'EUR/CAD', 'GBP/CAD'
]

bot = telebot.TeleBot(TOKEN)
td = TDClient(apikey=API_KEY)

def check_market_news():
    now = datetime.utcnow() + timedelta(hours=3)
    # تنبيه آلي في أوقات الأخبار والسيولة (لندن ونيويورك)
    if (10 <= now.hour <= 12) or (15 <= now.hour <= 17):
        return "⚠️ انصح بعدم التداول الآن: يوجد أخبار قوية وتذبذب عالي في السوق."
    return None

def analyze_logic(symbols, count=1):
    all_results = []
    for s in symbols:
        try:
            ts = td.time_series(symbol=s, interval="5min", outputsize=20)
            df = ts.as_pandas().sort_index(ascending=True)
            if df.empty: continue
            
            recent_15 = df.iloc[-15:]
            last_4 = df.iloc[-4:]
            
            # حساب الزخم (آخر 15)
            green = len(recent_15[recent_15['close'] > recent_15['open']])
            red = len(recent_15[recent_15['close'] < recent_15['open']])
            trend = "BUY" if green > red else "SELL"
            dom_ratio = (max(green, red) / 15) * 100

            # قياس الارتدادات (آخر 4)
            total_bodies = abs(last_4['close'] - last_4['open']).sum()
            total_range = (last_4['high'] - last_4['low']).sum()
            body_health = (total_bodies / total_range * 100) if total_range > 0 else 0
            
            score = int((dom_ratio * 0.5) + (body_health * 0.5))
            
            all_results.append({
                "pair": s, "trend": trend, "score": score, 
                "price": df.iloc[-1]['close'], "emoji": "🟢" if trend == "BUY" else "🔴"
            })
        except: continue
    return sorted(all_results, key=lambda x: x['score'], reverse=True)[:count]

@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_forex(message):
    num = int(message.text)
    signals = analyze_logic(FOREX_PAIRS, num)
    send_signals(message.chat.id, signals)

@bot.message_handler(func=lambda message: message.text.lower() == 'gold')
def handle_gold(message):
    signals = analyze_logic(['GOLD'], 1)
    send_signals(message.chat.id, signals)

def send_signals(chat_id, signals):
    if not signals:
        bot.send_message(chat_id, "❌ لم يتم العثور على إشارات قوية الآن.")
        return
    
    riyadh_time = datetime.utcnow() + timedelta(hours=3)
    news_note = check_market_news()

    for s in signals:
        label = "ممتازة" if s['score'] >= 85 else "جيدة جداً" if s['score'] >= 75 else "جيدة"
        header = "أفضل إشارة متوفرة حاليا من بين 13 زوج فوركس:" if s['pair'] != 'GOLD' else "تحليل خاص لمعدن الذهب:"
        
        response = (
            f"{header}\n"
            f"------------------------------------\n"
            f"{s['emoji']} {s['pair']}\n"
            f"📈 {s['trend']}\n"
            f"💰 {s['price']:.5f}\n"
            f"قوة الإشارة: {label} {s['score']}%\n"
            f"⏱️ الوقت: 3 دقائق\n"
            f"📅 {riyadh_time.strftime('%Y-%m-%d | %I:%M:%S %p')}\n"
            f"---------------------------------------\n"
        )
        if news_note:
            response += f"{news_note}\n---------------------------------------\n"
        response += "GOOD LUCK AHMED 👍"
        bot.send_message(chat_id, response)

if __name__ == "__main__":
    bot.infinity_polling()
    
