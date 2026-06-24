import urllib.request
import urllib.parse
import json
import ssl
import time
import threading
import os
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from supabase import create_client, Client

# ==========================================
# 1. KONFIGURĀCIJA UN DATUBĀZE
# ==========================================
bota_parole = "8871535091:AAEEvCj2X1bJ-GzmRpUpUndvEZ7NrEiPYNo" 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
context = ssl._create_unverified_context()

PEDEJAS_CENAS = None; PEDEJA_ATJAUNOSANA = 0
FNG_CACHE = None; FNG_TIME = 0
NEWS_CACHE = None; NEWS_TIME = 0

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Active")

def run_server():
    try: HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
    except: pass
threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. TULKOJUMI UN IZVĒLNE
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
# 3. SUPABASE UN API FUNKCIJAS
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
        if photo_url:
            url = f"https://api.telegram.org/bot{bota_parole}/sendPhoto"
            data = {"chat_id": chat_id, "photo": photo_url, "caption": text, "parse_mode": "Markdown"}
        else:
            url = f"https://api.telegram.org/bot{bota_parole}/sendMessage"
            data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
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
    global NEWS_CACHE, NEWS_TIME
    if NEWS_CACHE and (time.time() - NEWS_TIME < 1800): return NEWS_CACHE
    try:
        req = urllib.request.Request("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
            msg = "📰 *Karstākie Tirgus Jaunumi:*\n\n"
            for item in d['Data'][:3]:
                clean_title = item['title'].replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')
                msg += f"🔸 *{clean_title}*\n👉 {item['url']}\n\n"
            NEWS_CACHE = msg; NEWS_TIME = time.time(); return NEWS_CACHE
    except: return "⚠️ Neizdevās ielādēt jaunumus."

# ==========================================
# 4. FONA MONITORINGS UN CIKLS
# ==========================================
threading.Thread(target=lambda: [time.sleep(60) or None for _ in iter(int, 1)], daemon=True).start()

last_update_id = 0
crypto_map = {'btc': 'bitcoin', 'eth': 'ethereum', 'sol': 'solana'}

while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                if "message" in update:
                    msg = update["message"]; chat_id = msg["chat"]["id"]; txt = msg.get("text", "").lower().strip(); user = get_user(chat_id); lang = user.get('language', 'lv')
                    
                    # AI Roast funkcija
                    if any(x in txt for x in ["roast", "analize", "analīze"]):
                        port = user.get('portfolio', {}); monetas = {k: v for k, v in port.items() if k not in ['usd', 'last_bonus', 'streak', 'last_trivia']}
                        suti_zinu(chat_id, "🤖 *AI Analīze:* (Analizēju...)")
                        time.sleep(1)
                        if not monetas: suti_zinu(chat_id, "🛌 AI: Tavā portfelī tikai skaidra nauda. Garlaicīgi! 😴")
                        elif len(monetas) == 1: suti_zinu(chat_id, "🎢 AI: Tikai viena monēta? Klasisks kazino spēlmanis!")
                        else: suti_zinu(chat_id, "🍲 AI: Tavs portfelis izskatās pēc rasola. Diversifikācija ir laba, bet tas ir haoss!")
                    
                    # (Šeit turpini ar savu pārējo if/elif loģiku...)
                    elif "start" in txt: suti_zinu(chat_id, langs[lang]['txt'], dabut_menu(lang))
                    # ... (pārējās funkcijas) ...
    except: time.sleep(1)
