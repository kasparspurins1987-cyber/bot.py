import urllib.request
import json
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 1. KONFIGURĀCIJA UN JAUNĀ ATSLĒGA
# ==========================================
bota_parole = "8871535091:AAEEvCj2X1bJ-GzmRpUpUndvEZ7NrEiPYNo" 
context = ssl._create_unverified_context()

VALODU_FAILS = "lietotaju_valodas.json"

# Fona serveris priekš Render.com (lai uzturētu botu 24/7 tiešsaistē)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bots ir aktivs un darbojas 24/7")

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. TULKOJUMI UN VALODAS
# ==========================================
def ieladet_valodas():
    try:
        with open(VALODU_FAILS, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def saglabat_valodas(dati):
    try:
        with open(VALODU_FAILS, 'w', encoding='utf-8') as f: json.dump(dati, f, indent=4, ensure_ascii=False)
    except: pass

lietotaju_valodas = ieladet_valodas()

tulkojumi = {
    'lv': {'help': "👋 Sveiks! Izmanto izvēlni, lai pārbaudītu cenas vai skatītos grafikus.", 'err': "⚠️ API kļūda, mēģini vēlreiz.", 'fb': "✅ Paldies par atsauksmi!", 'del': "🗑️ Visi alerti izdzēsti.", 'anal': "📰 *Tirgus Analīze:* Finanšu tirgi šobrīd konsolidējas.", 'al': "🔔 *Mani Alerti:* Pašlaik nav aktīvu alertu."},
    'en': {'help': "👋 Welcome! Use the menu to check prices or view charts.", 'err': "⚠️ API error, please try again.", 'fb': "✅ Thanks for your feedback!", 'del': "🗑️ All alerts deleted.", 'anal': "📰 *Market Analysis:* Financial markets are currently consolidating.", 'al': "🔔 *My Alerts:* No active alerts."},
    'ru': {'help': "👋 Привет! Используйте меню для проверки цен и графиков.", 'err': "⚠️ Ошибка API, попробуйте еще раз.", 'fb': "✅ Спасибо за отзыв!", 'del': "🗑️ Все алерты удалены.", 'anal': "📰 *Анализ Рынка:* Финансовые рынки консолидируются.", 'al': "🔔 *Мои Алерты:* Нет активных алертов."},
    'de': {'help': "👋 Hallo! Verwenden Sie das Menü, um Preise und Charts zu prüfen.", 'err': "⚠️ API-Fehler.", 'fb': "✅ Danke für Ihr Feedback!", 'del': "🗑️ Alle Alerts gelöscht.", 'anal': "📰 *Marktanalyse:* Die Märkte konsolidieren sich.", 'al': "🔔 *Meine Alerts:* Keine aktiven Alerts."},
    'fr': {'help': "👋 Bonjour! Utilisez le menu pour vérifier les prix ou les graphiques.", 'err': "⚠️ Erreur API.", 'fb': "✅ Merci pour votre retour!", 'del': "🗑️ Toutes les alertes supprimées.", 'anal': "📰 *Analyse du Marché:* Les marchés se consolident.", 'al': "🔔 *Mes Alertes:* Aucune alerte active."},
    'es': {'help': "👋 ¡Hola! Use el menú para consultar precios o gráficos.", 'err': "⚠️ Error de API.", 'fb': "✅ ¡Gracias por sus comentarios!", 'del': "🗑️ Todas las alertas eliminadas.", 'anal': "📰 *Análisis de Mercado:* Los mercados se están consolidando.", 'al': "🔔 *Mis Alertas:* No hay alertas activas."},
    'it': {'help': "👋 Ciao! Usa il menu per verificare i prezzi o i grafici.", 'err': "⚠️ Errore API.", 'fb': "✅ Grazie per il tuo feedback!", 'del': "🗑️ Allerte eliminate.", 'anal': "📰 *Analisi di Mercado:* I mercati si stanno consolidando.", 'al': "🔔 *Le Mie Allerte:* Nessuna allerta attiva."},
    'pl': {'help': "👋 Witaj! Użyj menu, aby sprawdzić ceny lub wykresy.", 'err': "⚠️ Błąd API.", 'fb': "✅ Dziękujemy za opinię!", 'del': "🗑️ Wszystkie alerty usunięte.", 'anal': "📰 *Analiza Rynku:* Rynki finansowe konsolidują się.", 'al': "🔔 *Moje Alerty:* Brak aktywnych alertów."},
    'zh': {'help': "👋 您好！请使用菜单查看价格或图表。", 'err': "⚠️ API错误，请重试。", 'fb': "✅ 谢谢您的反馈！", 'del': "🗑️ 所有警报已删除。", 'anal': "📰 *市场分析:* 金融市场目前正在盘整。", 'al': "🔔 *我的警报:* 目前没有活跃的警报。"},
    'hi': {'help': "👋 नमस्ते! कीमतों या चार्ट की जांच के लिए मेनू का उपयोग करें।", 'err': "⚠️ एपीआई त्रुटि, फिर से प्रयास करें।", 'fb': "✅ आपकी प्रतिक्रिया के लिए धन्यवाद!", 'del': "🗑️ सभी अलर्ट हटा दिए गए।", 'anal': "📰 *बाजार विश्लेषण:* वित्तीय बाजार वर्तमान में मजबूत हो रहे हैं।", 'al': "🔔 *मेरे अलर्ट:* इस समय कोई सक्रिय अलर्ट नहीं है।"}
}

# ==========================================
# 3. PALĪGFUNKCIJAS (SŪTĪŠANA UN API)
# ==========================================
def suti_zinu(chat_id, text, pogas=None, disable_preview=True):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": disable_preview}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except: pass

def dabut_galveno_menu(lang):
    if lang == 'lv':
        return {"keyboard": [[{"text": "₿ Kripto"}, {"text": "💰 Metāli"}, {"text": "🛢️ Nafta"}], [{"text": "📰 Analīze"}, {"text": "🔔 Alerti"}], [{"text": "✍️ Atsauksmes"}, {"text": "🗑️ Dzēst"}], [{"text": "🌐 Mainīt Valodu"}]], "resize_keyboard": True}
    return {"keyboard": [[{"text": "₿ Crypto"}, {"text": "💰 Metals"}, {"text": "🛢️ Oil"}], [{"text": "📰 Analysis"}, {"text": "🔔 Alerts"}], [{"text": "✍️ Feedback"}, {"text": "🗑️ Delete"}], [{"text": "🌐 Language"}]], "resize_keyboard": True}

def dabut_cenas():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,kinesis-silver&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r: return json.loads(r.read().decode('utf-8'))
    except: return None

def suti_valodu_izvelei(chat_id):
    pogas = {"inline_keyboard": [
        [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}],
        [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇩🇪 DE", "callback_data": "lang_de"}],
        [{"text": "🇫🇷 FR", "callback_data": "lang_fr"}, {"text": "🇪🇸 ES", "callback_data": "lang_es"}],
        [{"text": "🇮🇹 IT", "callback_data": "lang_it"}, {"text": "🇵🇱 PL", "callback_data": "lang_pl"}],
        [{"text": "🇨🇳 ZH", "callback_data": "lang_zh"}, {"text": "🇮🇳 HI", "callback_data": "lang_hi"}]
    ]}
    suti_zinu(chat_id, "Izvēlies valodu / Select language:", pogas)

# ==========================================
# 4. GALVENAIS DARBĪBAS CIKLS
# ==========================================
last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                
                # Valodas izvēles pogas (Inline)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    if cb["data"].startswith("lang_"):
                        lang = cb["data"].split("_")[1]
                        lietotaju_valodas[str(chat_id)] = lang
                        saglabat_valodas(lietotaju_valodas)
                        t = tulkojumi.get(lang, tulkojumi['lv'])
                        suti_zinu(chat_id, t['help'], dabut_galveno_menu(lang))
                    continue

                # Teksta komandas
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    txt = msg.get("text", "").lower().strip()
                    if not txt: continue
                    
                    lang = lietotaju_valodas.get(str(chat_id), 'lv')
                    t = tulkojumi.get(lang, tulkojumi['lv'])

                    if "start" in txt or "valodu" in txt or "language" in txt:
                        suti_valodu_izvelei(chat_id)

                    elif "kripto" in txt or "crypto" in txt or "крипто" in txt:
                        c = dabut_cenas()
                        if c:
                            btc, eth, sol = c.get('bitcoin', {}).get('usd', 'N/A'), c.get('ethereum', {}).get('usd', 'N/A'), c.get('solana', {}).get('usd', 'N/A')
                            msg_txt = f"🪙 *Kripto Cenas & Grafiki:*\n\n₿ *BTC:* `${btc}` [📈 Atvērt Grafiku](https://www.tradingview.com/chart/?symbol=BINANCE:BTCUSDT)\n♦️ *ETH:* `${eth}` [📈 Atvērt Grafiku](https://www.tradingview.com/chart/?symbol=BINANCE:ETHUSDT)\n☀️ *SOL:* `${sol}` [📈 Atvērt Grafiku](https://www.tradingview.com/chart/?symbol=BINANCE:SOLUSDT)"
                            suti_zinu(chat_id, msg_txt, dabut_galveno_menu(lang))
                        else: suti_zinu(chat_id, t['err'], dabut_galveno_menu(lang))

                    elif "metāl" in txt or "metal" in txt or "метал" in txt:
                        c = dabut_cenas()
                        if c:
                            gold, silver = c.get('pax-gold', {}).get('usd', 'N/A'), c.get('kinesis-silver', {}).get('usd', 'N/A')
                            msg_txt = f"💰 *Metālu Cenas & Grafiki:*\n\n💰 *Zelts:* `${gold}` [📈 Atvērt Grafiku](https://www.tradingview.com/chart/?symbol=TVC:GOLD)\n🥈 *Sudrabs:* `${silver}` [📈 Atvērt Grafiku](https://www.tradingview.com/chart/?symbol=TVC:SILVER)"
                            suti_zinu(chat_id, msg_txt, dabut_galveno_menu(lang))
                        else: suti_zinu(chat_id, t['err'], dabut_galveno_menu(lang))

                    elif "nafta" in txt or "oil" in txt or "нефть" in txt:
                        msg_txt = "🛢️ *Naftas Tirgus (WTI Crude Oil):*\n\nLai reāllaikā sekotu līdzi naftas cenām un tirgus tendencēm, izmanto TradingView tiešraidi:\n\n👉 [📈 Atvērt Naftas Grafiku](https://www.tradingview.com/chart/?symbol=TVC:USOIL)"
                        suti_zinu(chat_id, msg_txt, dabut_galveno_menu(lang))

                    elif "analīz" in txt or "analys" in txt or "анализ" in txt: suti_zinu(chat_id, t['anal'], dabut_galveno_menu(lang))
                    elif "alert" in txt or "алерт" in txt: suti_zinu(chat_id, t['al'], dabut_galveno_menu(lang))
                    elif "feedback" in txt or "atsauk" in txt or "отзыв" in txt: suti_zinu(chat_id, t['fb'], dabut_galveno_menu(lang))
                    elif "izdzēs" in txt or "delete" in txt or "dzēst" in txt: suti_zinu(chat_id, t['del'], dabut_galveno_menu(lang))
                        
        time.sleep(1)
    except Exception as e: time.sleep(5)
