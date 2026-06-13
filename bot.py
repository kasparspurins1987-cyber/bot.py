import urllib.request
import json
import ssl
import time
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from supabase import create_client, Client

# ==========================================
# 1. KONFIGURĀCIJA UN DATUBĀZE
# ==========================================
bota_parole = "8871535091:AAEEvCj2X1bJ-GzmRpUpUndvEZ7NrEiPYNo" 

# Nolasa atslēgas no Render Environment
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("Brīdinājums: Supabase atslēgas nav atrastas!")

context = ssl._create_unverified_context()

PEDEJAS_CENAS = None; PEDEJA_ATJAUNOSANA = 0
FNG_CACHE = None; FNG_TIME = 0
NEWS_CACHE = None; NEWS_TIME = 0

# Fona serveris, lai Render neizslēdzas
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Active")

def run_server():
    try: HTTPServer(('0.0.0.0', 10000), SimpleHandler).serve_forever()
    except: pass
threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. TULKOJUMI (10 VALODAS)
# ==========================================
langs = {
    'lv': {'menu': ["₿ Kripto", "💰 Metāli", "📊 Indeksi & Forex", "🛢️ Nafta", "🧭 Fear & Greed", "🔥 Likvidācijas", "🤖 AI Noskaņojums", "📰 Jaunumi", "💼 Portfelis", "💱 Konvertors", "🔔 Brīdinājumi", "⚙️ Iestatījumi"], 'txt': "👋 Sveiks! Izmanto izvēlni zemāk."},
    'en': {'menu': ["₿ Crypto", "💰 Metals", "📊 Indices & Forex", "🛢️ Oil", "🧭 Fear & Greed", "🔥 Liquidations", "🤖 AI Sentiment", "📰 News", "💼 Portfolio", "💱 Converter", "🔔 Warnings", "⚙️ Settings"], 'txt': "👋 Hello! Use the menu below."},
    'ru': {'menu': ["₿ Крипто", "💰 Металлы", "📊 Индексы и Forex", "🛢️ Нефть", "🧭 Страх и Жадность", "🔥 Ликвидации", "🤖 AI Настроение", "📰 Новости", "💼 Портфель", "💱 Конвертер", "🔔 Предупреждения", "⚙️ Настройки"], 'txt': "👋 Привет! Используйте меню."},
    'de': {'menu': ["₿ Krypto", "💰 Metalle", "📊 Indizes & Forex", "🛢️ Öl", "🧭 Fear & Greed", "🔥 Liquidationen", "🤖 AI Stimmung", "📰 Nachrichten", "💼 Portfolio", "💱 Konverter", "🔔 Warnungen", "⚙️ Einstellungen"], 'txt': "👋 Hallo! Nutze das Menü."},
    'fr': {'menu': ["₿ Crypto", "💰 Métaux", "📊 Indices & Forex", "🛢️ Pétrole", "🧭 Fear & Greed", "🔥 Liquidations", "🤖 Sentiment AI", "📰 Actualités", "💼 Portefeuille", "💱 Convertisseur", "🔔 Alertes", "⚙️ Paramètres"], 'txt': "👋 Bonjour! Utilisez le menu."},
    'es': {'menu': ["₿ Cripto", "💰 Metales", "📊 Índices & Forex", "🛢️ Petróleo", "🧭 Fear & Greed", "🔥 Liquidaciones", "🤖 Sentimiento AI", "📰 Noticias", "💼 Portafolio", "💱 Convertidor", "🔔 Alertas", "⚙️ Ajustes"], 'txt': "👋 ¡Hola! Usa el menú."},
    'it': {'menu': ["₿ Cripto", "💰 Metalli", "📊 Indici & Forex", "🛢️ Petrolio", "🧭 Fear & Greed", "🔥 Liquidazioni", "🤖 Sentiment AI", "📰 Notizie", "💼 Portafoglio", "💱 Convertitore", "🔔 Avvisi", "⚙️ Impostazioni"], 'txt': "👋 Ciao! Usa il menu."},
    'pl': {'menu': ["₿ Krypto", "💰 Metale", "📊 Indeksy & Forex", "🛢️ Ropa", "🧭 Fear & Greed", "🔥 Likwidacje", "🤖 AI Nastroje", "📰 Wiadomości", "💼 Portfel", "💱 Konwerter", "🔔 Ostrzeżenia", "⚙️ Ustawienia"], 'txt': "👋 Cześć! Użyj menu."},
    'zh': {'menu': ["₿ 加密货币", "💰 金属", "📊 指数与外汇", "🛢️ 石油", "🧭 恐惧与贪婪", "🔥 清算", "🤖 AI 情绪", "📰 新闻", "💼 投资组合", "💱 转换器", "🔔 警报", "⚙️ 设置"], 'txt': "👋 您好！使用菜单。"},
    'hi': {'menu': ["₿ क्रिप्टो", "💰 धातु", "📊 सूचकांक और विदेशी मुद्रा", "🛢️ तेल", "🧭 डर और लालच", "🔥 लिक्विडेशन", "🤖 AI भावना", "📰 समाचार", "💼 पोर्टफोलियो", "💱 कनवर्टर", "🔔 चेतावनी", "⚙️ सेटिंग्स"], 'txt': "👋 नमस्ते! मेनू का उपयोग करें।"}
}

def dabut_menu(lang_code):
    l = langs.get(lang_code, langs['en']) # Angļu valoda kā rezerve
    m = l['menu']
    return {"keyboard": [[{"text": m[0]}, {"text": m[1]}], [{"text": m[2]}, {"text": m[3]}], [{"text": m[4]}, {"text": m[5]}], [{"text": m[6]}, {"text": m[7]}], [{"text": m[8]}, {"text": m[9]}], [{"text": m[10]}, {"text": m[11]}]], "resize_keyboard": True}

# ==========================================
# 3. SUPABASE UN API FUNKCIJAS
# ==========================================
def get_user(chat_id):
    cid = str(chat_id)
    if not supabase: return {"chat_id": cid, "language": "lv", "auto_pazi": True, "portfolio": {}, "alerts": {}}
    try:
        res = supabase.table("lietotaji").select("*").eq("chat_id", cid).execute()
        if res.data: return res.data[0]
        new_u = {"chat_id": cid, "language": "lv", "auto_pazi": True, "portfolio": {}, "alerts": {}}
        supabase.table("lietotaji").insert(new_u).execute()
        return new_u
    except: return {"chat_id": cid, "language": "lv", "auto_pazi": True, "portfolio": {}, "alerts": {}}

def update_user(chat_id, data):
    if not supabase: return
    try: supabase.table("lietotaji").update(data).eq("chat_id", str(chat_id)).execute()
    except: pass

def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except: pass

def dabut_cenas():
    global PEDEJAS_CENAS, PEDEJA_ATJAUNOSANA
    if PEDEJAS_CENAS and (time.time() - PEDEJA_ATJAUNOSANA < 60): return PEDEJAS_CENAS
    try:
        req = urllib.request.Request("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,kinesis-silver&vs_currencies=usd", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r: 
            dati = json.loads(r.read().decode('utf-8'))
            PEDEJAS_CENAS = dati; PEDEJA_ATJAUNOSANA = time.time(); return dati
    except: return PEDEJAS_CENAS

def dabut_fng():
    global FNG_CACHE, FNG_TIME
    if FNG_CACHE and (time.time() - FNG_TIME < 3600): return FNG_CACHE
    try:
        req = urllib.request.Request("https://api.alternative.me/fng/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
            FNG_CACHE = (int(d['data'][0]['value']), d['data'][0]['value_classification'])
            FNG_TIME = time.time(); return FNG_CACHE
    except: return None

def dabut_jaunumus():
    global NEWS_CACHE, NEWS_TIME
    if NEWS_CACHE and (time.time() - NEWS_TIME < 1800): return NEWS_CACHE
    try:
        req = urllib.request.Request("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
            msg = "📰 *Karstākie Tirgus Jaunumi:*\n\n"
            for item in d['Data'][:3]:
                clean_title = item['title'].replace('[', '(').replace(']', ')').replace('*', '').replace('_', '').replace('`', '')
                msg += f"🔸 [{clean_title}]({item['url']})\n\n"
            NEWS_CACHE = msg; NEWS_TIME = time.time(); return NEWS_CACHE
    except: return "⚠️ Neizdevās ielādēt jaunumus."

# ==========================================
# 4. FONA MONITORINGS (Alerti)
# ==========================================
def alert_monitor():
    while True:
        time.sleep(60)
        if not supabase: continue
        c = dabut_cenas()
        if not c: continue
        try:
            res = supabase.table("lietotaji").select("*").execute()
            for user in res.data:
                if user.get('auto_pazi') and user.get('alerts'):
                    alerts_to_remove = []
                    for asset, target in user['alerts'].items():
                        curr = c.get(asset, {}).get('usd', 0)
                        if curr > 0 and curr >= target:
                            suti_zinu(user['chat_id'], f"🚨 **AUTO-PAZIŅOJUMS!** 🚨\n\n🎯 Tavs mērķis sasniegts!\n📈 {asset.upper()} cena šobrīd ir **{curr}$**")
                            alerts_to_remove.append(asset)
                    
                    if alerts_to_remove:
                        new_alerts = user['alerts'].copy()
                        for a in alerts_to_remove: del new_alerts[a]
                        update_user(user['chat_id'], {"alerts": new_alerts})
        except: pass

threading.Thread(target=alert_monitor, daemon=True).start()

# ==========================================
# 5. GALVENAIS CIKLS
# ==========================================
last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                
                # Pogu nospiešana čatā (Iestatījumi, Valodas)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    dati = cb["data"]
                    user = get_user(chat_id)
                    
                    if dati.startswith("lang_"):
                        lang = dati.split("_")[1]
                        update_user(chat_id, {"language": lang})
                        suti_zinu(chat_id, "✅ Valoda iestatīta!", dabut_menu(lang))
                    elif dati == "toggle_auto":
                        new_status = not user.get('auto_pazi', True)
                        update_user(chat_id, {"auto_pazi": new_status})
                        status_txt = "IESLĒGTI ✅" if new_status else "IZSLĒGTI ❌"
                        suti_zinu(chat_id, f"🔔 Auto-Paziņojumi tagad ir: **{status_txt}**", dabut_menu(user['language']))
                    continue

                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    txt = msg.get("text", "").lower().strip()
                    user = get_user(chat_id)
                    lang = user.get('language', 'lv')
                    
                    # 1. Konvertors (Piemēram: 0.5 btc)
                    if len(txt.replace(',', '.').split()) == 2 and txt.replace(',', '.').split()[0].replace('.', '', 1).isdigit() and txt.split()[1] in ['btc', 'eth', 'sol', 'zelts', 'sudrabs']:
                        amt, coin = float(txt.replace(',', '.').split()[0]), txt.split()[1]
                        c = dabut_cenas()
                        mapa = {'btc':'bitcoin', 'eth':'ethereum', 'sol':'solana', 'zelts':'pax-gold', 'sudrabs':'kinesis-silver'}
                        if c and coin in mapa:
                            val = amt * c.get(mapa[coin], {}).get('usd', 0)
                            suti_zinu(chat_id, f"💱 `{amt} {coin.upper()}` = **{val:.2f} $** (USD)", dabut_menu(lang))
                        else:
                            suti_zinu(chat_id, "⚠️ API kļūda, mēģini vēlāk.", dabut_menu(lang))
                            
                    # 2. Portfeļa labošana (Piemēram: +btc 0.5)
                    elif txt.startswith('+') or txt.startswith('-'):
                        try:
                            parts = txt.replace(',', '.').split()
                            op, asset, amt = parts[0][0], parts[0][1:].lower(), float(parts[1])
                            if asset in ['btc', 'eth', 'sol']:
                                current_port = user.get('portfolio', {})
                                current_port[asset] = max(0.0, current_port.get(asset, 0) + (amt if op == '+' else -amt))
                                update_user(chat_id, {"portfolio": current_port})
                                suti_zinu(chat_id, "✅ Portfelis atjaunināts! Spied '💼 Portfelis'.", dabut_menu(lang))
                            else:
                                suti_zinu(chat_id, "❌ Nezināms aktīvs (izmanto btc, eth, sol).", dabut_menu(lang))
                        except: suti_zinu(chat_id, "❌ Kļūda formātā. Raksti: `+btc 0.5`", dabut_menu(lang))
                        
                    # 3. Alerta uzstādīšana (Piemēram: alert btc 70000)
                    elif txt.startswith('alert'):
                        parts = txt.split()
                        if len(parts) == 3 and parts[1] in ['btc', 'eth', 'sol']:
                            current_alerts = user.get('alerts', {})
                            current_alerts[parts[1]] = float(parts[2])
                            update_user(chat_id, {"alerts": current_alerts})
                            suti_zinu(chat_id, f"✅ Brīdinājums iestatīts! Paziņošu, kad {parts[1].upper()} sasniegs {parts[2]}$", dabut_menu(lang))
                        else:
                            suti_zinu(chat_id, "❌ Formāts: `alert btc 70000`", dabut_menu(lang))

                    # 4. Izvēlnes pogas (Pieskaņotas visām valodām)
                    elif any(x in txt for x in ["kripto", "crypto", "крипто", "krypto", "cripto", "加密货币", "क्रिप्टो"]):
                        c = dabut_cenas()
                        if c: suti_zinu(chat_id, f"🪙 ₿ BTC: {c.get('bitcoin', {}).get('usd', 'N/A')}$\n♦️ ETH: {c.get('ethereum', {}).get('usd', 'N/A')}$\n☀️ SOL: {c.get('solana', {}).get('usd', 'N/A')}$", dabut_menu(lang))
                        else: suti_zinu(chat_id, "⚠️ API kļūda.", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["metāl", "metal", "метал", "métaux", "metali", "金属", "धातु"]):
                        c = dabut_cenas()
                        if c: suti_zinu(chat_id, f"💰 Zelts: {c.get('pax-gold', {}).get('usd', 'N/A')}$\n🥈 Sudrabs: {c.get('kinesis-silver', {}).get('usd', 'N/A')}$", dabut_menu(lang))
                        else: suti_zinu(chat_id, "⚠️ API kļūda.", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["indeks", "index", "индекс", "indici"]):
                        suti_zinu(chat_id, "📊 *Indeksi un Forex:*\n👉 [S&P 500 Grafiks](https://www.tradingview.com/chart/?symbol=SP:SPX)\n👉 [EUR/USD Grafiks](https://www.tradingview.com/chart/?symbol=FX:EURUSD)", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["nafta", "oil", "нефть", "öl", "pétrole", "petróleo", "petrolio", "ropa", "石油", "तेल"]):
                        suti_zinu(chat_id, "🛢️ *Nafta (WTI):*\n👉 [Skatīt TradingView](https://www.tradingview.com/chart/?symbol=TVC:USOIL)", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["fear", "greed", "страх", "жадность", "peur", "miedo", "paura", "strach", "恐惧", "डर"]):
                        fng = dabut_fng()
                        if fng: suti_zinu(chat_id, f"🧭 F&G Indekss: {fng[0]}/100 ({fng[1]})", dabut_menu(lang))
                        else: suti_zinu(chat_id, "⚠️ Dati nav pieejami.", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["likvid", "liquid", "ликвид", "清算", "लिक्विडेशन"]):
                        suti_zinu(chat_id, "🔥 *Likvidācijas (24h):*\n📉 Shorts: ~420M$\n📈 Longs: ~310M$", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["ai", "noskaņ", "sentiment", "настроение", "stimmung", "nastroje", "情绪", "भावना"]):
                        fng = dabut_fng()
                        if fng:
                            val = fng[0]
                            verdict = "Pārkarsis tirgus (Greed)." if val > 75 else ("Bailes (Fear). Potenciāla pirkšanas zona!" if val < 25 else "Neitrāls tirgus.")
                            suti_zinu(chat_id, f"🤖 *AI Tirgus Noskaņojums:*\n\n📊 Indekss: {val}/100\n💡 Analīze: {verdict}", dabut_menu(lang))
                        else: suti_zinu(chat_id, "🤖 AI: Dati nav pieejami.", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["jaunum", "news", "новост", "nachrichten", "actualit", "noticias", "notizie", "wiadomo", "新闻", "समाचार"]):
                        suti_zinu(chat_id, dabut_jaunumus(), dabut_menu(lang))
                        
                    elif any(x in txt for x in ["portfel", "portfolio", "портфел", "portafoglio", "投资组合", "पोर्टफोलियो"]):
                        port = user.get('portfolio', {})
                        if not port or sum(port.values()) == 0:
                            suti_zinu(chat_id, "💼 *Tavs Portfelis ir tukšs.*\nLai pievienotu, raksti botam:\n`+btc 0.5`", dabut_menu(lang))
                        else:
                            c = dabut_cenas()
                            msg = "💼 *Tavs Portfelis:*\n\n"
                            total = 0.0
                            for asset, amt in port.items():
                                if amt > 0:
                                    val = amt * c.get(asset, {}).get('usd', 0) if c else 0
                                    total += val
                                    msg += f"• {asset.upper()}: `{amt}` (~ {val:.2f}$)\n"
                            suti_zinu(chat_id, msg + f"\n💵 *Kopā:* `{total:.2f}$`", dabut_menu(lang))
                            
                    elif any(x in txt for x in ["konvert", "convert", "конвертер", "转换器", "कनवर्टर"]):
                        suti_zinu(chat_id, "💱 *Konvertors*\nIeraksti daudzumu un monētu, lai uzzinātu vērtību USD.\n👉 *Piemērs:* `0.05 btc`", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["brīdin", "alert", "предупрежд", "warnung", "avvisi", "ostrzeż", "警报", "चेतावनी"]):
                        alerts = user.get('alerts', {})
                        if alerts:
                            msg = "🔔 *Tavi aktīvie brīdinājumi:*\n"
                            for a, v in alerts.items(): msg += f"• {a.upper()} mērķis: {v}$\n"
                            suti_zinu(chat_id, msg, dabut_menu(lang))
                        else:
                            suti_zinu(chat_id, "🔔 *Nav brīdinājumu.*\nLai iestatītu, raksti: `alert btc 75000`", dabut_menu(lang))
                            
                    elif any(x in txt for x in ["iestat", "setting", "настройк", "einstellung", "paramètre", "ajuste", "impostazion", "ustawieni", "设置", "सेटिंग्स"]):
                        status = "IESLĒGTI ✅" if user.get('auto_pazi', True) else "IZSLĒGTI ❌"
                        pogas = {"inline_keyboard": [
                            [{"text": "🔔 Pārslēgt Auto-Paziņojumus", "callback_data": "toggle_auto"}],
                            [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}, {"text": "🇷🇺 RU", "callback_data": "lang_ru"}]
                        ]}
                        suti_zinu(chat_id, f"⚙️ *Tavi Iestatījumi:*\n\n💬 Valoda: {lang.upper()}\n🔔 Auto-Paziņojumi: {status}", pogas)
                        
                    elif "start" in txt or "valod" in txt or "lang" in txt or "язык" in txt:
                        pogas = {"inline_keyboard": [
                            [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}, {"text": "🇷🇺 RU", "callback_data": "lang_ru"}],
                            [{"text": "🇩🇪 DE", "callback_data": "lang_de"}, {"text": "🇫🇷 FR", "callback_data": "lang_fr"}, {"text": "🇪🇸 ES", "callback_data": "lang_es"}],
                            [{"text": "🇮🇹 IT", "callback_data": "lang_it"}, {"text": "🇵🇱 PL", "callback_data": "lang_pl"}, {"text": "🇨🇳 ZH", "callback_data": "lang_zh"}]
                        ]}
                        suti_zinu(chat_id, "Izvēlies valodu / Select language / Выберите язык:", pogas)
                    
                    else:
                        suti_zinu(chat_id, langs.get(lang, langs['en'])['txt'], dabut_menu(lang))
                        
        time.sleep(1)
    except Exception as e: 
        print(f"Kļūda: {e}")
        time.sleep(5)
