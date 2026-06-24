import urllib.request, urllib.parse, json, ssl, time, threading, os
from http.server import BaseHTTPRequestHandler, HTTPServer
from supabase import create_client, Client

# ==========================================
# 1. KONFIGURĀCIJA
# ==========================================
bota_parole = "8871535091:AAEEvCj2X1bJ-GzmRpUpUndvEZ7NrEiPYNo" 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
context = ssl._create_unverified_context()

PEDEJAS_CENAS, PEDEJA_ATJAUNOSANA = None, 0
FNG_CACHE, FNG_TIME = None, 0
NEWS_CACHE, NEWS_TIME = None, 0

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Active")

def run_server():
    try: HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
    except: pass
threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. TULKOJUMI (VISAS 10 VALODAS)
# ==========================================
langs = {
    'lv': {'menu': ["₿ Kripto", "💰 Metāli", "📊 Indeksi", "🛢️ Nafta", "🧭 Fear & Greed", "📰 Jaunumi", "💼 Portfelis", "💱 Konvertors", "🏆 Līderi", "🎁 Bonuss", "💬 AI Čats", "🔔 Brīdinājumi", "⚙️ Iestatījumi", "🌐 Valoda"], 'txt': "👋 Sveiks!"},
    'en': {'menu': ["₿ Crypto", "💰 Metals", "📊 Indices", "🛢️ Oil", "🧭 Fear & Greed", "📰 News", "💼 Portfolio", "💱 Converter", "🏆 Leaders", "🎁 Bonus", "💬 AI Chat", "🔔 Alerts", "⚙️ Settings", "🌐 Language"], 'txt': "👋 Hello!"},
    'ru': {'menu': ["₿ Крипто", "💰 Металлы", "📊 Индексы", "🛢️ Нефть", "🧭 Страх/Жадность", "📰 Новости", "💼 Портфель", "💱 Конвертер", "🏆 Лидеры", "🎁 Бонус", "💬 AI Чат", "🔔 Оповещения", "⚙️ Настройки", "🌐 Язык"], 'txt': "👋 Привет!"},
    'de': {'menu': ["₿ Krypto", "💰 Metalle", "📊 Indizes", "🛢️ Öl", "🧭 Fear & Greed", "📰 News", "💼 Portfolio", "💱 Konverter", "🏆 Führer", "🎁 Bonus", "💬 AI Chat", "🔔 Warnungen", "⚙️ Einstellungen", "🌐 Sprache"], 'txt': "👋 Hallo!"},
    'fr': {'menu': ["₿ Crypto", "💰 Métaux", "📊 Indices", "🛢️ Pétrole", "🧭 Fear & Greed", "📰 Actualités", "💼 Portefeuille", "💱 Convertisseur", "🏆 Leaders", "🎁 Bonus", "💬 AI Chat", "🔔 Alertes", "⚙️ Paramètres", "🌐 Langue"], 'txt': "👋 Bonjour!"},
    'es': {'menu': ["₿ Cripto", "💰 Metales", "📊 Índices", "🛢️ Petróleo", "🧭 Fear & Greed", "📰 Noticias", "💼 Portafolio", "💱 Convertidor", "🏆 Líderes", "🎁 Bono", "💬 AI Chat", "🔔 Alertas", "⚙️ Ajustes", "🌐 Idioma"], 'txt': "👋 ¡Hola!"},
    'it': {'menu': ["₿ Cripto", "💰 Metalli", "📊 Indici", "🛢️ Petrolio", "🧭 Fear & Greed", "📰 Notizie", "💼 Portafoglio", "💱 Convertitore", "🏆 Leader", "🎁 Bonus", "💬 AI Chat", "🔔 Avvisi", "⚙️ Impostazioni", "🌐 Lingua"], 'txt': "👋 Ciao!"},
    'pl': {'menu': ["₿ Krypto", "💰 Metale", "📊 Indeksy", "🛢️ Ropa", "🧭 Fear & Greed", "📰 Wiadomości", "💼 Portfel", "💱 Konwerter", "🏆 Liderzy", "🎁 Bonus", "💬 AI Chat", "🔔 Ostrzeżenia", "⚙️ Ustawienia", "🌐 Język"], 'txt': "👋 Cześć!"},
    'zh': {'menu': ["₿ 加密货币", "💰 金属", "📊 指数", "🛢️ 石油", "🧭 恐惧与贪婪", "📰 新闻", "💼 投资组合", "💱 转换器", "🏆 领导者", "🎁 奖金", "💬 AI 聊天", "🔔 警报", "⚙️ 设置", "🌐 语言"], 'txt': "👋 您好！"},
    'hi': {'menu': ["₿ क्रिप्टो", "💰 धातु", "📊 सूचकांक", "🛢️ तेल", "🧭 डर और लालच", "📰 समाचार", "💼 पोर्टफोलियो", "💱 कनवर्टर", "🏆 नेता", "🎁 बोनस", "💬 AI चैट", "🔔 चेतावनी", "⚙️ सेटिंग्स", "🌐 भाषा"], 'txt': "👋 नमस्ते!"}
}

def dabut_menu(lang_code):
    m = langs.get(lang_code, langs['en'])['menu']
    return {"keyboard": [[{"text": m[0]}, {"text": m[1]}], [{"text": m[2]}, {"text": m[3]}], [{"text": m[4]}, {"text": m[5]}], [{"text": m[6]}, {"text": m[7]}], [{"text": m[8]}, {"text": m[9]}], [{"text": m[10]}, {"text": m[11]}], [{"text": m[12]}, {"text": m[13]}]], "resize_keyboard": True}

# ==========================================
# 3. FUNKCIJAS (GET_USER, UPDATE, SUTI_ZINU, CENAS, JAUNUMI, ALERT)
# ==========================================
def get_user(chat_id):
    cid = str(chat_id)
    default_u = {"chat_id": cid, "language": "lv", "auto_pazi": True, "portfolio": {"usd": 10000.0, "last_bonus": 0, "streak": 0}, "alerts": {}}
    if not supabase: return default_u
    try:
        res = supabase.table("lietotaji").select("*").eq("chat_id", cid).execute()
        if res.data: 
            u = res.data[0]
            if 'usd' not in u.get('portfolio', {}):
                p = u.get('portfolio', {}); p['usd'] = 10000.0; p['last_bonus'] = 0; p['streak'] = 0
                update_user(cid, {"portfolio": p}); u['portfolio'] = p
            return u
        supabase.table("lietotaji").insert(default_u).execute()
        return default_u
    except: return default_u

def update_user(chat_id, data):
    if supabase: 
        try: supabase.table("lietotaji").update(data).eq("chat_id", str(chat_id)).execute()
        except: pass

def suti_zinu(chat_id, text, pogas=None, photo_url=None):
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/{'sendPhoto' if photo_url else 'sendMessage'}"
        data = {"chat_id": chat_id, "parse_mode": "Markdown", "disable_web_page_preview": True}
        if photo_url: data["photo"] = photo_url; data["caption"] = text
        else: data["text"] = text
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=15)
    except Exception as e: print("Sūtīšanas kļūda:", e)

def dabut_cenas():
    global PEDEJAS_CENAS, PEDEJA_ATJAUNOSANA
    if PEDEJAS_CENAS and (time.time() - PEDEJA_ATJAUNOSANA < 60): return PEDEJAS_CENAS
    try:
        req = urllib.request.Request("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,kinesis-silver&vs_currencies=usd", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r: 
            dati = json.loads(r.read().decode('utf-8'))
            PEDEJAS_CENAS = dati; PEDEJA_ATJAUNOSANA = time.time(); return dati
    except: return PEDEJAS_CENAS

def dabut_jaunumus():
    try:
        req = urllib.request.Request("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
            msg = "📰 *Ziņas:*\n\n"
            for item in d['Data'][:3]: msg += f"🔸 *{item['title']}*\n👉 {item['url']}\n\n"
            return msg
    except: return "⚠️ Ziņas nav pieejamas."

# ==========================================
# 4. GALVENAIS CIKLS (AI ROAST + VISAS POGAS)
# ==========================================
last_update_id = 0
valodu_pogas = [[{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}], [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇩🇪 DE", "callback_data": "lang_de"}], [{"text": "🇫🇷 FR", "callback_data": "lang_fr"}, {"text": "🇪🇸 ES", "callback_data": "lang_es"}], [{"text": "🇮🇹 IT", "callback_data": "lang_it"}, {"text": "🇵🇱 PL", "callback_data": "lang_pl"}], [{"text": "🇨🇳 ZH", "callback_data": "lang_zh"}, {"text": "🇮🇳 HI", "callback_data": "lang_hi"}]]

while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                if "message" in update:
                    msg = update["message"]; chat_id = msg["chat"]["id"]; txt = msg.get("text", "").lower().strip(); user = get_user(chat_id); lang = user.get('language', 'lv')
                    
                    # AI ROAST
                    if "roast" in txt or "analiz" in txt:
                        suti_zinu(chat_id, "🤖 *AI Analīze:* (Analizēju...)")
                        time.sleep(1)
                        suti_zinu(chat_id, "🍲 AI: Tavs portfelis izskatās pēc rasola!")
                    # BONUSS (24h)
                    elif "bonuss" in txt or "bonus" in txt:
                        port = user.get('portfolio', {}); last = port.get('last_bonus', 0); now = time.time()
                        if now - last >= 86400:
                            streak = port.get('streak', 0) + 1; port['usd'] = port.get('usd', 10000) + (100 * streak); port['last_bonus'] = now; port['streak'] = streak
                            update_user(chat_id, {"portfolio": port}); suti_zinu(chat_id, f"🎁 Bonuss +{100*streak}$!")
                        else: suti_zinu(chat_id, f"⏳ Bonuss pēc {int((86400-(now-last))/3600)}h.")
                    # PORTFELIS, IESTATĪJUMI, NAFTA, INDEKSI, KRIPTO, JAUNUMI
                    elif "portfel" in txt: suti_zinu(chat_id, f"💼 Portfelis: {user.get('portfolio', {}).get('usd', 10000):.2f} $", dabut_menu(lang))
                    elif "iestat" in txt or "sett" in txt: suti_zinu(chat_id, "⚙️ Iestatījumi: Auto-paziņojumi ieslēgti.", {"inline_keyboard": [[{"text": "🔔 Pārslēgt", "callback_data": "toggle_auto"}]]})
                    elif "nafta" in txt: suti_zinu(chat_id, "🛢️ https://www.tradingview.com/chart/?symbol=TVC:USOIL")
                    elif "indeks" in txt: suti_zinu(chat_id, "📊 Indeksi: https://www.tradingview.com/chart/?symbol=SP:SPX")
                    elif "kripto" in txt: suti_zinu(chat_id, "🪙 BTC: " + str(dabut_cenas().get('bitcoin', {}).get('usd', 'N/A')) + " $")
                    elif "jaunum" in txt: suti_zinu(chat_id, dabut_jaunumus())
                    # START
                    elif "start" in txt or "valod" in txt: suti_zinu(chat_id, langs[lang]['txt'], {"inline_keyboard": valodu_pogas})
                    else: suti_zinu(chat_id, langs.get(lang, langs['en'])['txt'], dabut_menu(lang))
    except: time.sleep(1)
