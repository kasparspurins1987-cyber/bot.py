import urllib.request
import urllib.parse
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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

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
    return {"keyboard": [
        [{"text": m[0]}, {"text": m[1]}], [{"text": m[2]}, {"text": m[3]}],
        [{"text": m[4]}, {"text": m[5]}], [{"text": m[6]}, {"text": m[7]}],
        [{"text": m[8]}, {"text": m[9]}], [{"text": m[10]}, {"text": m[11]}],
        [{"text": m[12]}, {"text": m[13]}]
    ], "resize_keyboard": True}

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
                p = u.get('portfolio', {})
                p['usd'] = 10000.0; p['last_bonus'] = 0; p['streak'] = 0
                update_user(cid, {"portfolio": p}); u['portfolio'] = p
            return u
        supabase.table("lietotaji").insert(default_u).execute()
        return default_u
    except: return default_u

def update_user(chat_id, data):
    if not supabase: return
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
                clean_title = item['title'].replace('*', '').replace('_', '').replace('`', '').replace('[', '').replace(']', '')
                msg += f"🔸 *{clean_title}*\n👉 {item['url']}\n\n"
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
crypto_map = {'btc': 'bitcoin', 'eth': 'ethereum', 'sol': 'solana'}

valodu_pogas = [
    [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}],
    [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇩🇪 DE", "callback_data": "lang_de"}],
    [{"text": "🇫🇷 FR", "callback_data": "lang_fr"}, {"text": "🇪🇸 ES", "callback_data": "lang_es"}],
    [{"text": "🇮🇹 IT", "callback_data": "lang_it"}, {"text": "🇵🇱 PL", "callback_data": "lang_pl"}],
    [{"text": "🇨🇳 ZH", "callback_data": "lang_zh"}, {"text": "🇮🇳 HI", "callback_data": "lang_hi"}]
]

while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                
                # CALLBACK KVERIJI
                if "callback_query" in update:
                    cb = update["callback_query"]; chat_id = cb["message"]["chat"]["id"]; dati = cb["data"]; user = get_user(chat_id)
                    if dati.startswith("lang_"):
                        lang = dati.split("_")[1]; update_user(chat_id, {"language": lang})
                        suti_zinu(chat_id, "✅ Valoda iestatīta!", dabut_menu(lang))
                    elif dati == "toggle_auto":
                        new_status = not user.get('auto_pazi', True); update_user(chat_id, {"auto_pazi": new_status})
                        status_txt = "IESLĒGTI ✅" if new_status else "IZSLĒGTI ❌"
                        suti_zinu(chat_id, f"🔔 Auto-Paziņojumi tagad ir: **{status_txt}**", dabut_menu(user['language']))
                    continue

                # TEKSTA ZIŅAS
                if "message" in update:
                    msg = update["message"]; chat_id = msg["chat"]["id"]; txt = msg.get("text", "").lower().strip()
                    user = get_user(chat_id); lang = user.get('language', 'lv')
                    
                    # 1. Konvertors
                    if len(txt.replace(',', '.').split()) == 2 and txt.replace(',', '.').split()[0].replace('.', '', 1).isdigit() and txt.split()[1] in ['btc', 'eth', 'sol']:
                        amt, coin = float(txt.replace(',', '.').split()[0]), txt.split()[1]
                        c = dabut_cenas()
                        if c and coin in crypto_map:
                            val = amt * c.get(crypto_map[coin], {}).get('usd', 0)
                            suti_zinu(chat_id, f"💱 `{amt} {coin.upper()}` = **{val:.2f} $**", dabut_menu(lang))
                            
                    # 2. Pirkt
                    elif txt.startswith("buy ") or txt.startswith("pirkt "):
                        try:
                            parts = txt.replace(',', '.').split(); amt = float(parts[1]); coin = parts[2].lower()
                            if coin in crypto_map:
                                c = dabut_cenas(); price = c.get(crypto_map[coin], {}).get('usd', 0)
                                if price > 0:
                                    cost = amt * price; port = user.get('portfolio', {}); usd_balance = port.get('usd', 10000.0)
                                    if usd_balance >= cost:
                                        port['usd'] = usd_balance - cost; port[coin] = port.get(coin, 0.0) + amt
                                        update_user(chat_id, {"portfolio": port})
                                        suti_zinu(chat_id, f"✅ Nopirkts **{amt} {coin.upper()}** par **{cost:.2f} $**!", dabut_menu(lang))
                                    else: suti_zinu(chat_id, f"❌ Nepietiek USD! (Ir {usd_balance:.2f} $)", dabut_menu(lang))
                            else: suti_zinu(chat_id, "❌ Tikai btc, eth, sol.", dabut_menu(lang))
                        except: suti_zinu(chat_id, "❌ Kļūda. Raksti: `buy 0.1 btc`", dabut_menu(lang))

                    # 3. Pārdot
                    elif txt.startswith("sell ") or txt.startswith("pardot ") or txt.startswith("pārdot "):
                        try:
                            parts = txt.replace(',', '.').split(); amt = float(parts[1]); coin = parts[2].lower()
                            if coin in crypto_map:
                                c = dabut_cenas(); price = c.get(crypto_map[coin], {}).get('usd', 0)
                                port = user.get('portfolio', {}); coin_balance = port.get(coin, 0.0)
                                if coin_balance >= amt and price > 0:
                                    revenue = amt * price; port['usd'] = port.get('usd', 10000.0) + revenue; port[coin] = coin_balance - amt
                                    update_user(chat_id, {"portfolio": port})
                                    suti_zinu(chat_id, f"✅ Pārdots **{amt} {coin.upper()}** par **{revenue:.2f} $**!", dabut_menu(lang))
                                else: suti_zinu(chat_id, f"❌ Tev nav tik daudz {coin.upper()}!", dabut_menu(lang))
                            else: suti_zinu(chat_id, "❌ Tikai btc, eth, sol.", dabut_menu(lang))
                        except: suti_zinu(chat_id, "❌ Kļūda. Raksti: `sell 0.1 btc`", dabut_menu(lang))

                    # 4. Alerta uzstādīšana
                    elif txt.startswith('alert'):
                        parts = txt.split()
                        if len(parts) == 3 and parts[1] in ['btc', 'eth', 'sol']:
                            user['alerts'][parts[1]] = float(parts[2]); update_user(chat_id, {"alerts": user['alerts']})
                            suti_zinu(chat_id, f"✅ Brīdinājums: {parts[1].upper()} pie {parts[2]}$", dabut_menu(lang))
                        else: suti_zinu(chat_id, "❌ Raksti: `alert btc 70000`", dabut_menu(lang))

                    # 5. AI Čats
                    elif txt.startswith("ai "):
                        jautajums = txt[3:]
                        suti_zinu(chat_id, f"🧠 *AI Atbilde:*\n\nŠobrīd esmu 'Demo' režīmā. Rīt mēs pieslēgsim manu īsto intelektu, lai es varētu tev izsmeļoši atbildēt uz jautājumu: _{jautajums}_!", dabut_menu(lang))

                    # POGAS
                    elif any(x in txt for x in ["kripto", "crypto", "крипто"]):
                        c = dabut_cenas()
                        if c: suti_zinu(chat_id, f"🪙 ₿ BTC: {c.get('bitcoin', {}).get('usd', 'N/A')}$\n♦️ ETH: {c.get('ethereum', {}).get('usd', 'N/A')}$\n☀️ SOL: {c.get('solana', {}).get('usd', 'N/A')}$", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["metāl", "metal", "метал"]):
                        c = dabut_cenas()
                        if c: suti_zinu(chat_id, f"💰 Zelts: {c.get('pax-gold', {}).get('usd', 'N/A')}$\n🥈 Sudrabs: {c.get('kinesis-silver', {}).get('usd', 'N/A')}$", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["indeks", "index", "индекс"]):
                        suti_zinu(chat_id, "📊 *Indeksi un Forex:*\n👉 [S&P 500](https://www.tradingview.com/chart/?symbol=SP:SPX)\n👉 [EUR/USD](https://www.tradingview.com/chart/?symbol=FX:EURUSD)", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["nafta", "oil", "нефть"]):
                        suti_zinu(chat_id, "🛢️ *Nafta (WTI):*\n👉 [Skatīt TradingView](https://www.tradingview.com/chart/?symbol=TVC:USOIL)", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["fear", "greed", "страх"]):
                        fng = dabut_fng()
                        if fng: suti_zinu(chat_id, f"🧭 F&G Indekss: {fng[0]}/100 ({fng[1]})", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["jaunum", "news", "новост"]):
                        suti_zinu(chat_id, dabut_jaunumus(), dabut_menu(lang))
                        
                    elif any(x in txt for x in ["ai čats", "ai chat", "ai чат"]):
                        suti_zinu(chat_id, "💬 *AI Čats*\n\nLai parunātu ar mani, vienkārši sāc savu ziņu ar vārdu 'ai '.\n👉 *Piemērs:* `ai kas ir bitcoin?`", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["bonuss", "bonus", "бонус"]):
                        port = user.get('portfolio', {}); last_bonus = port.get('last_bonus', 0); now = time.time()
                        if now - last_bonus > 86400: # 24h pagājušas
                            streak = port.get('streak', 0) + 1
                            port['usd'] = port.get('usd', 10000.0) + (100 * streak)
                            port['last_bonus'] = now; port['streak'] = streak
                            update_user(chat_id, {"portfolio": port})
                            suti_zinu(chat_id, f"🎁 *Dienas Bonuss Saņemts!*\n\nTavai bilancei pievienoti **{100 * streak} $**.\n🔥 Streak: {streak} dienas!", dabut_menu(lang))
                        else:
                            atlicis = int((86400 - (now - last_bonus)) / 3600)
                            suti_zinu(chat_id, f"⏳ *Bonuss nav pieejams.*\nNāc atpakaļ pēc {atlicis} stundām!", dabut_menu(lang))

                    elif any(x in txt for x in ["līder", "leader", "лидер"]):
                        if supabase:
                            res = supabase.table("lietotaji").select("chat_id, portfolio").execute()
                            c = dabut_cenas(); top = []
                            for u in res.data:
                                port = u.get('portfolio', {}); total = port.get('usd', 10000.0)
                                for asset, amt in port.items():
                                    if asset not in ['usd', 'last_bonus', 'streak'] and amt > 0:
                                        total += amt * c.get(crypto_map.get(asset, asset), {}).get('usd', 0) if c else 0
                                top.append((u['chat_id'], total))
                            top.sort(key=lambda x: x[1], reverse=True)
                            msg = "🏆 *Globālais Top 10:*\n\n"
                            for i, (uid, tot) in enumerate(top[:10]):
                                ikona = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else "👤"
                                is_me = "(Tu)" if str(uid) == str(chat_id) else ""
                                msg += f"{ikona} ID {str(uid)[:5]}... {is_me}: `{tot:.2f} $`\n"
                            suti_zinu(chat_id, msg, dabut_menu(lang))

                    elif any(x in txt for x in ["portfel", "portfolio", "портфел"]):
                        port = user.get('portfolio', {}); c = dabut_cenas()
                        usd_balance = port.get('usd', 10000.0); total_crypto_value = 0.0; has_crypto = False
                        msg = f"💼 *Tavs Portfelis:*\n\n💵 USD: `{usd_balance:.2f} $`\n*Aktīvi:*\n"
                        
                        labels = ['USD']; data = [usd_balance]
                        
                        for asset, amt in port.items():
                            if asset not in ['usd', 'last_bonus', 'streak'] and amt > 0:
                                val = amt * c.get(crypto_map.get(asset, asset), {}).get('usd', 0) if c else 0
                                total_crypto_value += val; has_crypto = True
                                msg += f"• {asset.upper()}: `{amt}` (~ {val:.2f} $)\n"
                                labels.append(asset.upper()); data.append(val)
                        
                        if not has_crypto: msg += "_Nav monētu._\n"
                        msg += f"\n💰 *Kopā:* `{usd_balance + total_crypto_value:.2f} $`\n\n🎮 Raksti: `buy 0.1 btc` vai `sell 0.5 eth`"
                        
                        # Ģenerē attēlu grafiku tikai tad, ja ir ko rādīt
                        chart_url = None
                        try:
                            chart_c = '{"type":"pie","data":{"labels":[' + ','.join([f'"{l}"' for l in labels]) + '],"datasets":[{"data":[' + ','.join(map(str, data)) + ']}]}}'
                            chart_url = "https://quickchart.io/chart?c=" + urllib.parse.quote(chart_c)
                        except: pass
                        
                        suti_zinu(chat_id, msg, dabut_menu(lang), photo_url=chart_url)
                            
                    elif any(x in txt for x in ["konvert", "convert", "конвертер"]):
                        suti_zinu(chat_id, "💱 Ieraksti: `0.05 btc`", dabut_menu(lang))
                        
                    elif any(x in txt for x in ["brīdin", "alert", "предупрежд"]):
                        alerts = user.get('alerts', {})
                        if alerts:
                            msg = "🔔 *Aktīvie:*\n" + "".join([f"• {a.upper()}: {v}$\n" for a,v in alerts.items()])
                            suti_zinu(chat_id, msg, dabut_menu(lang))
                        else: suti_zinu(chat_id, "🔔 Raksti: `alert btc 75000`", dabut_menu(lang))
                            
                    elif any(x in txt for x in ["iestat", "setting", "настройк"]):
                        status = "IESLĒGTI ✅" if user.get('auto_pazi', True) else "IZSLĒGTI ❌"
                        suti_zinu(chat_id, f"⚙️ *Iestatījumi:*\n🔔 Auto-Paziņojumi: {status}", {"inline_keyboard": [[{"text": "🔔 Pārslēgt Auto-Paziņojumus", "callback_data": "toggle_auto"}]]})
                        
                    elif "start" in txt or "valod" in txt or "lang" in txt or "язык" in txt:
                        suti_zinu(chat_id, "Izvēlies valodu / Select language / Выберите язык:", {"inline_keyboard": valodu_pogas})
                    else:
                        suti_zinu(chat_id, langs.get(lang, langs['en'])['txt'], dabut_menu(lang))
                        
        time.sleep(1)
    except Exception as e: print("Main loop kļūda:", e); time.sleep(5)
-- 1. Izdzēšam veco, salauzto tabulu
DROP TABLE IF EXISTS lietotaji;

-- 2. Izveidojam jaunu, perfektu tabulu ar visām vajadzīgajām kolonnām
CREATE TABLE lietotaji (
    id SERIAL PRIMARY KEY,
    chat_id TEXT UNIQUE,
    language TEXT DEFAULT 'lv',
    auto_pazi BOOLEAN DEFAULT TRUE,
    portfolio JSONB DEFAULT '{}'::jsonb,
    alerts JSONB DEFAULT '{}'::jsonb
);
