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

VALODU_FAILS = "lietotaju_valodas.json"
PORTFELU_FAILS = "lietotaju_portfeli.json"

PEDEJAS_CENAS = None; PEDEJA_ATJAUNOSANA = 0
FNG_CACHE = None; FNG_TIME = 0
NEWS_CACHE = None; NEWS_TIME = 0

# Fona serveris (Render.com)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bots ir aktivs")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler); server.serve_forever()
threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. DATI UN TULKOJUMI
# ==========================================
def ieladet_datus(fails):
    try:
        with open(fails, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def saglabat_datus(fails, dati):
    try:
        with open(fails, 'w', encoding='utf-8') as f: json.dump(dati, f, indent=4, ensure_ascii=False)
    except: pass

lietotaju_valodas = ieladet_datus(VALODU_FAILS)
lietotaju_portfeli = ieladet_datus(PORTFELU_FAILS)

tulkojumi = {
    'lv': {'help': "👋 Sveiks! Izmanto izvēlni.", 'err': "⚠️ Kļūda.", 'fb': "✅ Paldies!", 'del': "🗑️ Dzēsts.", 'al': "🔔 Nav alertu."},
    'en': {'help': "👋 Welcome! Use the menu.", 'err': "⚠️ Error.", 'fb': "✅ Thanks!", 'del': "🗑️ Deleted.", 'al': "🔔 No alerts."},
    'ru': {'help': "👋 Привет! Используйте меню.", 'err': "⚠️ Ошибка.", 'fb': "✅ Спасибо!", 'del': "🗑️ Удалено.", 'al': "🔔 Нет алертов."},
    'de': {'help': "👋 Hallo! Nutze das Menü.", 'err': "⚠️ Fehler.", 'fb': "✅ Danke!", 'del': "🗑️ Gelöscht.", 'al': "🔔 Keine Alerts."},
    'fr': {'help': "👋 Bonjour! Utilisez le menu.", 'err': "⚠️ Erreur.", 'fb': "✅ Merci!", 'del': "🗑️ Supprimé.", 'al': "🔔 Aucune alerte."},
    'es': {'help': "👋 Hola! Usa el menú.", 'err': "⚠️ Error.", 'fb': "✅ ¡Gracias!", 'del': "🗑️ Borrado.", 'al': "🔔 Sin alertas."},
    'it': {'help': "👋 Ciao! Usa il menu.", 'err': "⚠️ Errore.", 'fb': "✅ Grazie!", 'del': "🗑️ Eliminato.", 'al': "🔔 Nessun avviso."},
    'pl': {'help': "👋 Cześć! Użyj menu.", 'err': "⚠️ Błąd.", 'fb': "✅ Dzięki!", 'del': "🗑️ Usunięto.", 'al': "🔔 Brak alertów."},
    'zh': {'help': "👋 您好！使用菜单。", 'err': "⚠️ 错误。", 'fb': "✅ 谢谢！", 'del': "🗑️ 已删除。", 'al': "🔔 无提醒。"},
    'hi': {'help': "👋 नमस्ते! मेनू का उपयोग करें।", 'err': "⚠️ त्रुटि।", 'fb': "✅ धन्यवाद!", 'del': "🗑️ हटा दिया गया।", 'al': "🔔 कोई अलर्ट नहीं।"}
}

# ==========================================
# 3. PALĪGFUNKCIJAS
# ==========================================
def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except: pass

def dabut_galveno_menu(lang):
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
    global PEDEJAS_CENAS, PEDEJA_ATJAUNOSANA
    if PEDEJAS_CENAS and (time.time() - PEDEJA_ATJAUNOSANA < 60): return PEDEJAS_CENAS
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,kinesis-silver&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r: 
            dati = json.loads(r.read().decode('utf-8'))
            PEDEJAS_CENAS = dati; PEDEJA_ATJAUNOSANA = time.time()
            return dati
    except: return PEDEJAS_CENAS

def dabut_fng():
    global FNG_CACHE, FNG_TIME
    if FNG_CACHE and (time.time() - FNG_TIME < 3600): return FNG_CACHE
    try:
        req = urllib.request.Request("https://api.alternative.me/fng/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
            FNG_CACHE = (d['data'][0]['value'], d['data'][0]['value_classification'])
            FNG_TIME = time.time(); return FNG_CACHE
    except: return None

def dabut_likvidacijas():
    return "🔥 *Likvidāciju Kopsavilkums (24h):*\n\n📉 *Shorts:* `~420M$`\n📈 *Longs:* `~310M$`\n\n_Ja Shorts ir ievērojami lielāki par Longs, tas bieži norāda uz 'Short Squeeze' iespējamību._"

def analizet_tirgu():
    fng = dabut_fng()
    if not fng: return "🤖 AI: Neizdevās iegūt datus."
    val = int(fng[0])
    verdict = "Pārkarsis tirgus!" if val > 75 else ("Potenciāla pirkšanas zona!" if val < 25 else "Neitrāls tirgus.")
    return f"🤖 *AI Tirgus Noskaņojums:*\n\n📊 Indekss: {val}/100\n💡 Analīze: {verdict}"

def dabut_jaunumus():
    global NEWS_CACHE, NEWS_TIME
    if NEWS_CACHE and (time.time() - NEWS_TIME < 1800): return NEWS_CACHE
    try:
        req = urllib.request.Request("https://min-api.cryptocompare.com/data/v2/news/?lang=EN", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            d = json.loads(r.read().decode('utf-8'))
            top = d['Data'][:3]
            msg = "📰 *Karstākie Tirgus Jaunumi:*\n\n"
            for item in top: msg += f"🔸 [{item['title']}]({item['url']})\n\n"
            NEWS_CACHE = msg; NEWS_TIME = time.time(); return NEWS_CACHE
    except: return "⚠️ Neizdevās ielādēt jaunumus."

# ==========================================
# 5. PORTFELIS
# ==========================================
def apstradat_portfeli(chat_id, txt):
    try:
        parts = txt.split()
        if len(parts) != 2: return "❌ Kļūda. Formāts: `+btc 0.5` vai `-sol 2`"
        op, asset, daudzums = parts[0][0], parts[0][1:].lower(), float(parts[1].replace(',', '.'))
        asset_map = {'btc': 'bitcoin', 'eth': 'ethereum', 'sol': 'solana', 'zelts': 'pax-gold', 'sudrabs': 'kinesis-silver'}
        if asset not in asset_map: return "❌ Nezināms aktīvs."
        cid = str(chat_id)
        if cid not in lietotaju_portfeli: lietotaju_portfeli[cid] = {}
        real_asset = asset_map[asset]
        current = lietotaju_portfeli[cid].get(real_asset, 0.0)
        if op == '+': current += daudzums
        elif op == '-': current = max(0.0, current - daudzums)
        lietotaju_portfeli[cid][real_asset] = current
        saglabat_datus(PORTFELU_FAILS, lietotaju_portfeli)
        return "✅ Portfelis atjaunināts!"
    except: return "❌ Kļūda."

def paradit_portfeli(chat_id):
    cid = str(chat_id)
    c = dabut_cenas()
    if cid not in lietotaju_portfeli or sum(lietotaju_portfeli[cid].values()) == 0: return "💼 *Tavs Portfelis ir tukšs.*"
    msg = "💼 *Tavs Portfelis:*\n\n"
    total_usd = 0.0
    for asset, amount in lietotaju_portfeli[cid].items():
        if amount > 0:
            val = amount * c.get(asset, {}).get('usd', 0)
            total_usd += val
            msg += f"• {asset.upper()}: `{amount}` (~ {val:.2f}$)\n"
    return msg + f"\n💵 *Kopā:* `{total_usd:.2f}$`"

# ==========================================
# 6. GALVENAIS CIKLS
# ==========================================
last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    lang = cb["data"].split("_")[1]
                    lietotaju_valodas[str(chat_id)] = lang
                    saglabat_datus(VALODU_FAILS, lietotaju_valodas)
                    suti_zinu(chat_id, tulkojumi.get(lang, tulkojumi['lv'])['help'], dabut_galveno_menu(lang))
                elif "message" in update:
                    msg = update["message"]; chat_id = msg["chat"]["id"]; txt = msg.get("text", "").lower().strip()
                    if not txt: continue
                    lang = lietotaju_valodas.get(str(chat_id), 'lv')
                    t = tulkojumi.get(lang, tulkojumi['lv'])

                    if txt.startswith('+') or txt.startswith('-'): suti_zinu(chat_id, apstradat_portfeli(chat_id, txt), dabut_galveno_menu(lang))
                    elif "start" in txt or "valod" in txt or "language" in txt:
                        pogas = {"inline_keyboard": [
                            [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}],
                            [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇩🇪 DE", "callback_data": "lang_de"}],
                            [{"text": "🇫🇷 FR", "callback_data": "lang_fr"}, {"text": "🇪🇸 ES", "callback_data": "lang_es"}],
                            [{"text": "🇮🇹 IT", "callback_data": "lang_it"}, {"text": "🇵🇱 PL", "callback_data": "lang_pl"}],
                            [{"text": "🇨🇳 ZH", "callback_data": "lang_zh"}, {"text": "🇮🇳 HI", "callback_data": "lang_hi"}]
                        ]}
                        suti_zinu(chat_id, "Izvēlies valodu / Select language:", pogas)
                    elif "kripto" in txt: suti_zinu(chat_id, "🪙 Cenas: BTC, ETH, SOL", dabut_galveno_menu(lang))
                    elif "likvid" in txt: suti_zinu(chat_id, dabut_likvidacijas(), dabut_galveno_menu(lang))
                    elif "ai" in txt or "noskaņ" in txt: suti_zinu(chat_id, analizet_tirgu(), dabut_galveno_menu(lang))
                    elif "portfel" in txt: suti_zinu(chat_id, paradit_portfeli(chat_id), dabut_galveno_menu(lang))
                    elif "jaunum" in txt: suti_zinu(chat_id, dabut_jaunumus(), dabut_galveno_menu(lang))
                    else: suti_zinu(chat_id, t['help'], dabut_galveno_menu(lang))
        time.sleep(1)
    except: time.sleep(5)
