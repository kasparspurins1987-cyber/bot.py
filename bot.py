
import urllib.request
import json
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. KONFIGURĀCIJA
bota_parole = "8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM"
context = ssl._create_unverified_context()

# 2. RENDER.COM SERVERIS
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Bots ir aktivs".encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# 3. DATU UN TULKOJUMU IELĀDE
VALODU_FAILS, ALERTI_FAILS, ATSAUKSMJU_FAILS = "lietotaju_valodas.json", "lietotaju_alerti.json", "atsauksmes.json"

def ieladet_failu(f_nos):
    try:
        with open(f_nos, 'r') as f: return json.load(f)
    except: return [] if "atsauksmes" in f_nos else {}

def saglabat_failu(f_nos, dati):
    try:
        with open(f_nos, 'w') as f: json.dump(dati, f, indent=4)
    except: pass

lietotaju_valodas = ieladet_failu(VALODU_FAILS)
lietotaju_alerti = ieladet_failu(ALERTI_FAILS)
atsauksmes_saraksts = ieladet_failu(ATSAUKSMJU_FAILS)

PRODUKTI = {
    'btc': {'id': 'bitcoin', 'name': 'Bitcoin (BTC)', 'emoji': '₿', 'tv': 'https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT'},
    'eth': {'id': 'ethereum', 'name': 'Ethereum (ETH)', 'emoji': '♦️', 'tv': 'https://www.tradingview.com/chart/?symbol=BINANCE%3AETHUSDT'},
    'sol': {'id': 'solana', 'name': 'Solana (SOL)', 'emoji': '☀️', 'tv': 'https://www.tradingview.com/chart/?symbol=BINANCE%3ASOLUSDT'},
    'zelts': {'id': 'pax-gold', 'name': 'Zelts (PAXG)', 'emoji': '💰', 'tv': 'https://www.tradingview.com/chart/?symbol=TVC%3AGOLD'},
    'sudrabs': {'id': 'tether-silver', 'name': 'Sudrabs (SILVER)', 'emoji': '🥈', 'tv': 'https://www.tradingview.com/chart/?symbol=TVC%3ASILVER'}
}

tulkojumi = {
    'lv': {'help': "👋 Sveiks! Izmanto izvēlni.", 'err': "⚠️ Kļūda.", 'news': "📰 Analīze:", 'bull': "📈 Trends: Augšupejošs.", 'alert_set': "🔔 Uzstādīts:", 'fb_ok': "✅ Paldies!"},
    'en': {'help': "👋 Welcome! Use menu.", 'err': "⚠️ Error.", 'news': "📰 Analysis:", 'bull': "📈 Trend: Bullish.", 'alert_set': "🔔 Set:", 'fb_ok': "✅ Thanks!"},
    'ru': {'help': "👋 Привет!", 'err': "⚠️ Ошибка.", 'news': "📰 Анализ:", 'bull': "📈 Тренд: Бычий.", 'alert_set': "🔔 Установлен:", 'fb_ok': "✅ Спасибо!"},
    'de': {'help': "👋 Hallo!", 'err': "⚠️ Fehler.", 'news': "📰 Marktanalyse:", 'bull': "📈 Trend: Bullish.", 'alert_set': "🔔 Eingestellt:", 'fb_ok': "✅ Danke!"},
    'fr': {'help': "👋 Bonjour!", 'err': "⚠️ Erreur.", 'news': "📰 Analyse:", 'bull': "📈 Tendance: Haussière.", 'alert_set': "🔔 Configurée:", 'fb_ok': "✅ Merci!"},
    'es': {'help': "👋 ¡Hola!", 'err': "⚠️ Error.", 'news': "📰 Análisis:", 'bull': "📈 Tendencia: Alcista.", 'alert_set': "🔔 Configurada:", 'fb_ok': "✅ ¡Gracias!"},
    'it': {'help': "👋 Ciao!", 'err': "⚠️ Errore.", 'news': "📰 Analisi:", 'bull': "📈 Trend: Rialzista.", 'alert_set': "🔔 Impostato:", 'fb_ok': "✅ Grazie!"},
    'pl': {'help': "👋 Witaj!", 'err': "⚠️ Błąd.", 'news': "📰 Analiza:", 'bull': "📈 Trend: Wzrostowy.", 'alert_set': "🔔 Ustawiony:", 'fb_ok': "✅ Dziękujemy!"},
    'zh': {'help': "👋 您好！", 'err': "⚠️ 错误。", 'news': "📰 市场分析:", 'bull': "📈 趋势：看涨。", 'alert_set': "🔔 设置为:", 'fb_ok': "✅ 谢谢！"},
    'hi': {'help': "👋 नमस्ते!", 'err': "⚠️ त्रुटि。", 'news': "📰 बाजार विश्लेषण:", 'bull': "📈 रुझान: तेजी।", 'alert_set': "🔔 अलर्ट सेट:", 'fb_ok': "✅ धन्यवाद!"}
}

# 4. GALVENAIS CIKLS
def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except: pass

last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r:
            atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    txt = update["message"].get("text", "").lower()
                    
                    if "start" in txt: suti_zinu(chat_id, "Sveiks! Izvēlies valodu.", {"inline_keyboard": [[{"text": "🇱🇻", "callback_data": "lang_lv"}, {"text": "🇬🇧", "callback_data": "lang_en"}]]})
                    elif "feedback" in txt:
                        atsauksmes_saraksts.append({"user": chat_id, "text": txt})
                        saglabat_failu(ATSAUKSMJU_FAILS, atsauksmes_saraksts)
                        suti_zinu(chat_id, "✅ Paldies!")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(5)

