import urllib.request
import json
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 1. KONFIGURĀCIJA UN INTERFEISS
# ==========================================
bota_parole = "8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM"
context = ssl._create_unverified_context()

VALODU_FAILS = "lietotaju_valodas.json"

# Fona serveris priekš Render.com (uztur botu tiešsaistē)
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
# 2. TULKOJUMI UN FAILU APSTRĀDE
# ==========================================
def ieladet_valodas():
    try:
        with open(VALODU_FAILS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def saglabat_valodas(dati):
    try:
        with open(VALODU_FAILS, 'w', encoding='utf-8') as f:
            json.dump(dati, f, indent=4, ensure_ascii=False)
    except:
        pass

lietotaju_valodas = ieladet_valodas()

tulkojumi = {
    'lv': {'help': "👋 Sveiks! Izmanto izvēlni, lai pārbaudītu cenas vai saņemtu analīzi.", 'err': "⚠️ API kļūda, mēģini vēlreiz.", 'fb_ok': "✅ Paldies par atsauksmi!", 'del_all': "🗑️ Visi alerti izdzēsti.", 'anal': "📰 *Tirgus Analīze:* Finanšu tirgi šobrīd konsolidējas.", 'al_none': "🔔 *Mani Alerti:* Pašlaik nav aktīvu alertu."},
    'en': {'help': "👋 Welcome! Use the menu to check prices or view analysis.", 'err': "⚠️ API error, please try again.", 'fb_ok': "✅ Thanks for your feedback!", 'del_all': "🗑️ All alerts deleted.", 'anal': "📰 *Market Analysis:* Financial markets are currently consolidating.", 'al_none': "🔔 *My Alerts:* No active alerts at the moment."},
    'ru': {'help': "👋 Привет! Используйте меню для проверки цен или анализа.", 'err': "⚠️ Ошибка API, попробуйте еще раз.", 'fb_ok': "✅ Спасибо за отзыв!", 'del_all': "🗑️ Все алерты удалены.", 'anal': "📰 *Анализ Рынка:* Финансовые рынки консолидируются.", 'al_none': "🔔 *Мои Алерты:* Нет активных алертов."},
    'de': {'help': "👋 Hallo! Verwenden Sie das Menü, um Preise und Analysen zu prüfen.", 'err': "⚠️ API-Fehler.", 'fb_ok': "✅ Danke für Ihr Feedback!", 'del_all': "🗑️ Alle Alerts gelöscht.", 'anal': "📰 *Marktanalyse:* Die Märkte konsolidieren sich.", 'al_none': "🔔 *Meine Alerts:* Keine aktiven Alerts."},
    'fr': {'help': "👋 Bonjour! Utilisez le menu pour vérifier les prix ou l'analyse.", 'err': "⚠️ Erreur API.", 'fb_ok': "✅ Merci pour votre retour!", 'del_all': "🗑️ Toutes les alertes supprimées.", 'anal': "📰 *Analyse du Marché:* Les marchés financiers se consolident.", 'al_none': "🔔 *Mes Alertes:* Aucune alerte active."},
    'es': {'help': "👋 ¡Hola! Use el menú para consultar precios o análisis.", 'err': "⚠️ Error de API.", 'fb_ok': "✅ ¡Gracias por sus comentarios!", 'del_all': "🗑️ Todas las alertas eliminadas.", 'anal': "📰 *Análisis de Mercado:* Los mercados se están consolidando.", 'al_none': "🔔 *Mis Alertas:* No hay alertas activas."},
    'it': {'help': "👋 Ciao! Usa il menu per verificare i prezzi o l'analisi.", 'err': "⚠️ Errore API.", 'fb_ok': "✅ Grazie per il tuo feedback!", 'del_all': "🗑️ Allerte eliminate.", 'anal': "📰 *Analisi di Mercato:* I mercati si stanno consolidando.", 'al_none': "🔔 *Le Mie Allerte:* Nessuna allerta attiva."},
    'pl': {'help': "👋 Witaj! Użyj menu, aby sprawdzić ceny lub analizy.", 'err': "⚠️ Błąd API.", 'fb_ok': "✅ Dziękujemy za opinię!", 'del_all': "🗑️ Wszystkie alerty usunięte.", 'anal': "📰 *Analiza Rynku:* Rynki finansowe konsolidują się.", 'al_none': "🔔 *Moje Alerty:* Brak aktywnych alertów."},
    'zh': {'help': "👋 您好！请使用菜单查看价格或市场分析。", 'err': "⚠️ API错误，请重试。", 'fb_ok': "✅ 谢谢您的反馈！", 'del_all': "🗑️ 所有警报已删除。", 'anal': "📰 *市场分析:* 金融市场目前正在盘整。", 'al_none': "🔔 *我的警报:* 目前没有活跃的警报。"},
    'hi': {'help': "👋 नमस्ते! कीमतों या विश्लेषण की जांच के लिए मेनू का उपयोग करें।", 'err': "⚠️ एपीआई त्रुटि, फिर से प्रयास करें।", 'fb_ok': "✅ आपकी प्रतिक्रिया के लिए धन्यवाद!", 'del_all': "🗑️ सभी अलर्ट हटा दिए गए।", 'anal': "📰 *बाजार विश्लेषण:* वित्तीय बाजार वर्तमान में मजबूत हो रहे हैं।", 'al_none': "🔔 *मेरे अलर्ट:* इस समय कोई सक्रिय अलर्ट नहीं है।"}
}

# ==========================================
# 3. PALĪGFUNKCIJAS (SŪTĪŠANA UN API)
# ==========================================
def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if pogas:
            data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bota_parole}/sendMessage",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, context=context, timeout=10)
    except:
        pass

def dabut_galveno_menu(lang):
    # Pielāgo pogu tekstus divām pamata valodām, pārējām izmanto universālu / angļu formu
    if lang == 'lv':
        return {
            "keyboard": [
                [{"text": "₿ Kripto Cenas"}, {"text": "💰 Metālu Cenas"}],
                [{"text": "📰 Tirgus Analīze"}, {"text": "🔔 Mani Alerti"}],
                [{"text": "✍️ Atsauksmes / Ieteikumi"}, {"text": "🗑️ Izdzēst Alertus"}],
                [{"text": "🌐 Mainīt Valodu"}]
            ], "resize_keyboard": True
        }
    return {
        "keyboard": [
            [{"text": "₿ Crypto Prices"}, {"text": "💰 Metal Prices"}],
            [{"text": "📰 Market Analysis"}, {"text": "🔔 My Alerts"}],
            [{"text": "✍️ Feedback / Suggestions"}, {"text": "🗑️ Delete Alerts"}],
            [{"text": "🌐 Change Language"}]
        ], "resize_keyboard": True
    }

def dabut_cenas():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,kinesis-silver&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except:
        return None

def suti_valodu_izvelei(chat_id):
    pogas = {"inline_keyboard": [
        [{"text": "Latviešu 🇱🇻", "callback_data": "lang_lv"}, {"text": "English 🇬🇧", "callback_data": "lang_en"}],
        [{"text": "Русский 🇷🇺", "callback_data": "lang_ru"}, {"text": "Deutsch 🇩🇪", "callback_data": "lang_de"}],
        [{"text": "Français 🇫🇷", "callback_data": "lang_fr"}, {"text": "Español 🇪🇸", "callback_data": "lang_es"}],
        [{"text": "Italiano 🇮🇹", "callback_data": "lang_it"}, {"text": "Polski 🇵🇱", "callback_data": "lang_pl"}],
        [{"text": "简体中文 🇨🇳", "callback_data": "lang_zh"}, {"text": "हिन्दी 🇮🇳", "callback_data": "lang_hi"}]
    ]}
    suti_zinu(chat_id, "Izvēlies valodu / Select language:", pogas)

# ==========================================
# 4. GALVENAIS DARBĪBAS CIKLS
# ==========================================
last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r:
            atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                
                # 1. Inline pogu klikšķi (Valodas izvēle)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    if cb["data"].startswith("lang_"):
                        izveleta = cb["data"].split("_")[1]
                        lietotaju_valodas[str(chat_id)] = izveleta
                        saglabat_valodas(lietotaju_valodas)
                        t = tulkojumi.get(izveleta, tulkojumi['lv'])
                        suti_zinu(chat_id, t['help'], dabut_galveno_menu(izveleta))
                    continue

                # 2. Parastās ziņas un izvēlnes pogas
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    txt = msg.get("text", "").lower().strip()
                    if not txt:
                        continue
                    
                    lang = lietotaju_valodas.get(str(chat_id), 'lv')
                    t = tulkojumi.get(lang, tulkojumi['lv'])

                    # Komandu atpazīšana (Neatkarīgi no izvēlētās valodas)
                    if "start" in txt or "valodu" in txt or "language" in txt or "язык" in txt:
                        suti_valodu_izvelei(chat_id)

                    elif "kripto" in txt or "crypto" in txt or "крипто" in txt:
                        c = dabut_cenas()
                        if c:
                            btc = c.get('bitcoin', {}).get('usd', 'N/A')
                            eth = c.get('ethereum', {}).get('usd', 'N/A')
                            sol = c.get('solana', {}).get('usd', 'N/A')
                            msg_txt = f"🪙 *Kripto Cenas (USD):*\n\n₿ *BTC:* `${btc}`\n♦️ *ETH:* `${eth}`\n☀️ *SOL:* `${sol}`"
                            suti_zinu(chat_id, msg_txt, dabut_galveno_menu(lang))
                        else:
                            suti_zinu(chat_id, t['err'], dabut_galveno_menu(lang))

                    elif "metāl" in txt or "metal" in txt or "металл" in txt:
                        c = dabut_cenas()
                        if c:
                            gold = c.get('pax-gold', {}).get('usd', 'N/A')
                            silver = c.get('kinesis-silver', {}).get('usd', 'N/A')
                            msg_txt = f"💰 *Metālu Cenas (USD):*\n\n💰 *Zelts (PAXG):* `${gold}`\n🥈 *Sudrabs:* `${silver}`"
                            suti_zinu(chat_id, msg_txt, dabut_galveno_menu(lang))
                        else:
                            suti_zinu(chat_id, t['err'], dabut_galveno_menu(lang))

                    elif "analīz" in txt or "analys" in txt or "анализ" in txt:
                        suti_zinu(chat_id, t['anal'], dabut_galveno_menu(lang))

                    elif "alert" in txt or "алерт" in txt:
                        suti_zinu(chat_id, t['al_none'], dabut_galveno_menu(lang))

                    elif "feedback" in txt or "atsauk" in txt or "отзыв" in txt:
                        suti_zinu(chat_id, t['fb_ok'], dabut_galveno_menu(lang))

                    elif "izdzēs" in txt or "delete" in txt or "удалить" in txt:
                        suti_zinu(chat_id, t['del_all'], dabut_galveno_menu(lang))
                        
        time.sleep(1)
    except Exception as e:
        time.sleep(5)
