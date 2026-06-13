import urllib.request
import json
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 1. KONFIGURĀCIJA
# ==========================================
bota_parole = "8871535091:AAEEvCj2X1bJ-GzmRpUpUndvEZ7NrEiPYNo" 
context = ssl._create_unverified_context()

# Fona serveris (Render.com)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Active")

def run_server():
    try:
        server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
        server.serve_forever()
    except: pass

threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. TULKOJUMI (10 VALODAS)
# ==========================================
tulkojumi = {
    'lv': {'help': "👋 Sveiks! Izmanto izvēlni.", 'err': "⚠️ API kļūda, mēģini vēlreiz."},
    'en': {'help': "👋 Hello! Use the menu.", 'err': "⚠️ API error, try again."},
    'ru': {'help': "👋 Привет! Используйте меню.", 'err': "⚠️ Ошибка API, попробуйте снова."},
    'de': {'help': "👋 Hallo! Nutze das Menü.", 'err': "⚠️ API-Fehler, versuche es erneut."},
    'fr': {'help': "👋 Bonjour! Utilisez le menu.", 'err': "⚠️ Erreur API, réessayez."},
    'es': {'help': "👋 ¡Hola! Usa el menú.", 'err': "⚠️ Error de API, inténtalo de nuevo."},
    'it': {'help': "👋 Ciao! Usa il menu.", 'err': "⚠️ Errore API, riprova."},
    'pl': {'help': "👋 Cześć! Użyj menu.", 'err': "⚠️ Błąd API, spróbuj ponownie."},
    'zh': {'help': "👋 您好！使用菜单。", 'err': "⚠️ API 错误，请重试。"},
    'hi': {'help': "👋 नमस्ते! मेनू का उपयोग करें。", 'err': "⚠️ एपीआई त्रुटि, पुनः प्रयास करें।"}
}

# ==========================================
# 3. PALĪGFUNKCIJAS
# ==========================================
def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if pogas: 
            data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except Exception as e: 
        print(f"Kļūda sūtot: {e}")

def dabut_galveno_menu():
    return {"keyboard": [
        [{"text": "₿ Kripto"}, {"text": "💰 Metāli"}],
        [{"text": "📊 Indeksi & Forex"}, {"text": "🛢️ Nafta"}],
        [{"text": "🧭 Fear & Greed"}, {"text": "🔥 Likvidācijas"}],
        [{"text": "🤖 AI Noskaņojums"}, {"text": "📰 Jaunumi"}],
        [{"text": "💼 Portfelis"}, {"text": "🔔 Alerti"}],
        [{"text": "✍️ Atsauksmes"}, {"text": "🌐 Valoda"}]
    ], "resize_keyboard": True}

# ==========================================
# 4. TIRGUS DATI
# ==========================================
def dabut_cenas():
    try:
        req = urllib.request.Request("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,kinesis-silver&vs_currencies=usd", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r: 
            return json.loads(r.read().decode('utf-8'))
    except: 
        return None

# ==========================================
# 5. GALVENAIS CIKLS
# ==========================================
last_update_id = 0
lietotaju_valodas = {}

while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: 
            atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                
                # Apstrādājam pogu spiedienus
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    lang = cb["data"].split("_")[1]
                    lietotaju_valodas[str(chat_id)] = lang
                    suti_zinu(chat_id, f"Valoda iestatīta / Language set: {lang.upper()}", dabut_galveno_menu())
                    continue

                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    txt = msg.get("text", "").lower()
                    
                    lang = lietotaju_valodas.get(str(chat_id), 'lv')
                    t = tulkojumi.get(lang, tulkojumi['lv'])
                    
                    if "valod" in txt or "language" in txt or "start" in txt:
                        pogas = {"inline_keyboard": [
                            [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}],
                            [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇩🇪 DE", "callback_data": "lang_de"}],
                            [{"text": "🇫🇷 FR", "callback_data": "lang_fr"}, {"text": "🇪🇸 ES", "callback_data": "lang_es"}],
                            [{"text": "🇮🇹 IT", "callback_data": "lang_it"}, {"text": "🇵🇱 PL", "callback_data": "lang_pl"}],
                            [{"text": "🇨🇳 ZH", "callback_data": "lang_zh"}, {"text": "🇮🇳 HI", "callback_data": "lang_hi"}]
                        ]}
                        suti_zinu(chat_id, "Izvēlies valodu / Select language:", pogas)
                    
                    elif "kripto" in txt:
                        c = dabut_cenas()
                        if c: 
                            btc = c.get('bitcoin', {}).get('usd', 'N/A')
                            eth = c.get('ethereum', {}).get('usd', 'N/A')
                            sol = c.get('solana', {}).get('usd', 'N/A')
                            suti_zinu(chat_id, f"₿ BTC: {btc}$\n♦️ ETH: {eth}$\n☀️ SOL: {sol}$", dabut_galveno_menu())
                        else: 
                            suti_zinu(chat_id, t['err'], dabut_galveno_menu())
                    
                    elif "metāl" in txt:
                        c = dabut_cenas()
                        if c: 
                            zelts = c.get('pax-gold', {}).get('usd', 'N/A')
                            sudrabs = c.get('kinesis-silver', {}).get('usd', 'N/A')
                            suti_zinu(chat_id, f"💰 Zelts: {zelts}$\n🥈 Sudrabs: {sudrabs}$", dabut_galveno_menu())
                        else: 
                            suti_zinu(chat_id, t['err'], dabut_galveno_menu())
                    
                    elif "nafta" in txt:
                        suti_zinu(chat_id, "🛢️ Nafta (WTI): [Skatīt](https://www.tradingview.com/chart/?symbol=TVC:USOIL)", dabut_galveno_menu())
                        
                    elif "indeks" in txt or "forex" in txt:
                        suti_zinu(chat_id, "📊 Indeksi: [S&P 500](https://www.tradingview.com/chart/?symbol=SP:SPX)\n💱 Forex: [EUR/USD](https://www.tradingview.com/chart/?symbol=FX:EURUSD)", dabut_galveno_menu())
                        
                    elif "fear" in txt or "greed" in txt:
                        suti_zinu(chat_id, "🧭 F&G Indekss: 13 (Extreme Fear)", dabut_galveno_menu())
                        
                    elif "likvid" in txt:
                        suti_zinu(chat_id, "🔥 Likvidācijas (24h):\n📉 Shorts: ~420M$\n📈 Longs: ~310M$", dabut_galveno_menu())
                        
                    elif "ai" in txt or "noskaņ" in txt:
                        suti_zinu(chat_id, "🤖 AI Noskaņojums: Tirgus konsolidējas.", dabut_galveno_menu())
                        
                    elif "jaunum" in txt:
                        suti_zinu(chat_id, "📰 Jaunumi: Lasi jaunāko informāciju tirgū.", dabut_galveno_menu())
                        
                    elif "portfel" in txt:
                        suti_zinu(chat_id, "💼 Tavs portfelis ir tukšs.", dabut_galveno_menu())
                        
                    else:
                        suti_zinu(chat_id, t['help'], dabut_galveno_menu())
                        
        time.sleep(1)
    except Exception as e: 
        print(f"Kļūda ciklā: {e}")
        time.sleep(5)
