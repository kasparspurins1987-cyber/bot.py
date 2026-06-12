import telebot
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Tavs tokens
TOKEN = '8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM'
bot = telebot.TeleBot(TOKEN)

# HTTP serveris, lai Render neizslēgtu botu dēļ neaktivitātes
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Bots ir aktivs".encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# Palaižam serveri paralēli botam
threading.Thread(target=run_server, daemon=True).start()

# Šeit sākas tavs bota loģikas kods
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Sveiks! Bots ir veiksmīgi palaists uz Render.com")
import urllib.request
import json
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. BOTU KONFIGURĀCIJA UN DROŠĪBA
bota_parole = "8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM"
context = ssl._create_unverified_context()

# --- RENDER.COM SERVERIS (Pievienots, lai bots darbojas 24/7) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Bots ir aktivs".encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
# -----------------------------------------------------------

VALODU_FAILS = "lietotaju_valodas.json"
ALERTI_FAILS = "lietotaju_alerti.json"
ATSAUKSMJU_FAILS = "atsauksmes.json"

def ieladet_failu(faila_nosaukums):
    try:
        with open(faila_nosaukums, 'r') as f:
            dati = json.load(f)
            return dati if isinstance(dati, (dict, list)) else {}
    except:
        return [] if "atsauksmes" in faila_nosaukums else {}

def saglabat_failu(faila_nosaukums, dati):
    try:
        with open(faila_nosaukums, 'w') as f:
            json.dump(dati, f, indent=4)
    except:
        pass

lietotaju_valodas = ieladet_failu(VALODU_FAILS)
lietotaju_alerti = ieladet_failu(ALERTI_FAILS)
atsauksmes_saraksts = ieladet_failu(ATSAUKSMJU_FAILS)
if not isinstance(atsauksmes_saraksts, list): atsauksmes_saraksts = []

PRODUKTI = {
    'btc': {'id': 'bitcoin', 'name': 'Bitcoin (BTC)', 'emoji': '₿', 'tv': 'https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT'},
    'eth': {'id': 'ethereum', 'name': 'Ethereum (ETH)', 'emoji': '♦️', 'tv': 'https://www.tradingview.com/chart/?symbol=BINANCE%3AETHUSDT'},
    'sol': {'id': 'solana', 'name': 'Solana (SOL)', 'emoji': '☀️', 'tv': 'https://www.tradingview.com/chart/?symbol=BINANCE%3ASOLUSDT'},
    'zelts': {'id': 'pax-gold', 'name': 'Zelts (PAXG)', 'emoji': '💰', 'tv': 'https://www.tradingview.com/chart/?symbol=TVC%3AGOLD'},
    'sudrabs': {'id': 'tether-silver', 'name': 'Sudrabs (SILVER)', 'emoji': '🥈', 'tv': 'https://www.tradingview.com/chart/?symbol=TVC%3ASILVER'}
}

tulkojumi = {
    'lv': {'help': "👋 Sveiks! Izmanto apakšējo izvēlni, lai uzzinātu cenas.\n\n🔔 *Kā uzstādīt alertu?*\nIeraksti: `alert btc 65000`", 'err': "⚠️ Kļūda saņemot datus no tirgus API.", 'news': "📰 *Lokālā AI Tirgus Analīze:*", 'bull': "📈 *Trends: Augšupejošs.*", 'news_txt': "Finanšu tirgi konsolidējas.", 'alert_set': "🔔 Alert uzstādīts uz", 'alert_del': "🗑️ Visi tavi alerti ir izdzēsti.", 'no_alerts': "🔔 Tev šobrīd nav aktīvu alertu.", 'your_alerts': "📋 *Tavi aktīvie alerti:*\n", 'fb_info': "✍️ *Atsauksmju pastkaste*\n\nUzraksti savu sūdzību, ieteikumu vai ideju, sākot ziņu ar vārdu `feedback`.", 'fb_ok': "✅ Paldies!"},
    'en': {'help': "👋 Welcome! Use the menu below to check prices.\n\n🔔 *How to set an alert?*\nType: `alert btc 65000`", 'err': "⚠️ Error getting data.", 'news': "📰 *Local AI Market Analysis:*", 'bull': "📈 *Trend: Bullish.*", 'news_txt': "Financial markets are consolidating.", 'alert_set': "🔔 Alert set for", 'alert_del': "All your alerts have been deleted.", 'no_alerts': "🔔 No active alerts.", 'your_alerts': "📋 *Your active alerts:*\n", 'fb_info': "✍️ *Feedback Mailbox*", 'fb_ok': "✅ Thank you!"},
    'ru': {'help': "👋 Привет! Используйте меню ниже.", 'err': "⚠️ Ошибка API.", 'news': "📰 *Анализ рынка:*", 'news_txt': "Рынки консолидируются.", 'bull': "📈 *Тренд: Бычий.*", 'alert_set': "🔔 Алерт установлен на", 'alert_del': "🗑️ Все алерты удалены.", 'no_alerts': "🔔 Нет алертов.", 'your_alerts': "📋 *Ваши алерты:*\n", 'fb_info': "Напишите `feedback ваш текст`", 'fb_ok': "✅ Спасибо!"},
    'de': {'help': "👋 Hallo! Nutzen Sie das Menü unten.", 'err': "⚠️ API-Fehler.", 'news': "📰 *Marktanalyse:*", 'news_txt': "Märkte konsolidieren sich.", 'bull': "📈 *Trend: Bullish.*", 'alert_set': "🔔 Alert eingestellt für", 'alert_del': "🗑️ Alle Alerts gelöscht.", 'no_alerts': "🔔 Keine aktiven Alerts.", 'your_alerts': "📋 *Ihre Alerts:*\n", 'fb_info': "Schreiben Sie `feedback ihr text`", 'fb_ok': "✅ Danke!"},
    'fr': {'help': "👋 Bonjour! Utilisez le menu ci-dessous.", 'err': "⚠️ Erreur API.", 'news': "📰 *Analyse du marché:*", 'news_txt': "Les marchés se consolident.", 'bull': "📈 *Tendance: Haussière.*", 'alert_set': "🔔 Alerte configurée pour", 'alert_del': "🗑️ Toutes les alertes supprimées.", 'no_alerts': "🔔 Aucune alerte active.", 'your_alerts': "📋 *Vos alertes:*\n", 'fb_info': "Écrivez `feedback votre texte`", 'fb_ok': "✅ Merci!"},
    'es': {'help': "👋 ¡Hola! Use el menú de abajo.", 'err': "⚠️ Error de API.", 'news': "📰 *Análisis de Mercado:*", 'news_txt': "Los mercados se consolidan.", 'bull': "📈 *Tendencia: Alcista.*", 'alert_set': "🔔 Alerta configurada para", 'alert_del': "🗑️ Alertas eliminadas.", 'no_alerts': "🔔 No tienes alertas activas.", 'your_alerts': "📋 *Tus alertas:*\n", 'fb_info': "Escribe `feedback tu texto`", 'fb_ok': "✅ ¡Gracias!"},
    'it': {'help': "👋 Ciao! Usa il menu qui sotto.", 'err': "⚠️ Errore API.", 'news': "📰 *Analisi di Mercato:*", 'news_txt': "I mercati si consolidano.", 'bull': "📈 *Trend: Rialzista.*", 'alert_set': "🔔 Alert impostato per", 'alert_del': "🗑️ Tutti gli alert cancellati.", 'no_alerts': "🔔 Nessun alert attivo.", 'your_alerts': "📋 *I tuoi alert:*\n", 'fb_info': "Scrivi `feedback tuo testo`", 'fb_ok': "✅ Grazie!"},
    'pl': {'help': "👋 Witaj! Użyj menu poniżej.", 'err': "⚠️ Błąd API.", 'news': "📰 *Analiza Rynku:*", 'news_txt': "Rynki konsolidują się.", 'bull': "📈 *Trend: Wzrostowy.*", 'alert_set': "🔔 Alert ustawiony na", 'alert_del': "🗑️ Wszystkie alerty usunięte.", 'no_alerts': "🔔 Brak aktywnych alertów.", 'your_alerts': "📋 *Twoje alerty:*\n", 'fb_info': "Napisz `feedback twój tekst`", 'fb_ok': "✅ Dziękujemy!"},
    'zh': {'help': "👋 您好！请使用下面的菜单查看价格。", 'err': "⚠️ 错误。", 'news': "📰 *市场分析:*", 'news_txt': "市场正在巩固。", 'bull': "📈 *趋势：看涨。*", 'alert_set': "🔔 提醒已设置为", 'alert_del': "🗑️ 所有提醒已删除。", 'no_alerts': "🔔 您目前没有活跃的提醒。", 'your_alerts': "📋 *您的活跃提醒：*\n", 'fb_info': "请写下 `feedback 您的内容`", 'fb_ok': "✅ 谢谢您的反馈！"},
    'hi': {'help': "👋 नमस्ते! कीमतों की जांच करने के लिए नीचे दिए गए मेनू का उपयोग करें।", 'err': "⚠️ त्रुटि।", 'news': "📰 *बाजार विश्लेषण:*", 'news_txt': "बाजार मजबूत हो रहे हैं।", 'bull': "📈 *रुझान: तेजी।*", 'alert_set': "🔔 अलर्ट सेट किया गया", 'alert_del': "🗑️ आपके सभी अलर्ट हटा दिए गए हैं।", 'no_alerts': "🔔 आपके पास अभी कोई सक्रिय अलर्ट नहीं है।", 'your_alerts': "📋 *आपके सक्रिय अलर्ट:*\n", 'fb_info': "`feedback अपना संदेश` लिखें", 'fb_ok': "✅ धन्यवाद!"}
}
def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bota_parole}/sendMessage",
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, context=context, timeout=10)
    except:
        pass

def dabut_galveno_menu(lang):
    if lang == 'en':
        return {
            "keyboard": [
                [{"text": "₿ Crypto Prices"}, {"text": "💰 Metal Prices"}],
                [{"text": "📰 Market Analysis"}, {"text": "🔔 My Alerts"}],
                [{"text": "✍️ Feedback / Suggestions"}, {"text": "🗑️ Delete Alerts"}],
                [{"text": "🌐 Change Language"}]
            ], "resize_keyboard": True
        }
    return {
        "keyboard": [
            [{"text": "₿ Kripto Cenas"}, {"text": "💰 Metālu Cenas"}],
            [{"text": "📰 Tirgus Analīze"}, {"text": "🔔 Mani Alerti"}],
            [{"text": "✍️ Atsauksmes / Ieteikumi"}, {"text": "🗑️ Izdzēst Alertus"}],
            [{"text": "🌐 Mainīt Valodu"}]
        ], "resize_keyboard": True
    }

def dabut_cenas_coingecko():
    try:
        ids = ",".join([prod['id'] for prod in PRODUKTI.values()])
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=8) as r:
            return json.loads(r.read().decode('utf-8'))
    except:
        return None

last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as response:
            atbilde = json.loads(response.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                
                # Callback (valodu izvēle)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    if cb["data"].startswith("lang_"):
                        izveleta = cb["data"].split("_")[1]
                        lietotaju_valodas[str(chat_id)] = izveleta
                        saglabat_failu(VALODU_FAILS, lietotaju_valodas)
                        t = tulkojumi.get(izveleta, tulkojumi['lv'])
                        suti_zinu(chat_id, t['help'], dabut_galveno_menu(izveleta))
                    continue

                msg = update.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                if not chat_id or "text" not in msg: continue
                
                teksts = msg.get("text", "")
                teksts_low = teksts.lower().replace("/", "").strip()
                lang = lietotaju_valodas.get(str(chat_id), 'lv')
                t = tulkojumi.get(lang, tulkojumi['lv'])

                if "start" in teksts_low or "mainīt valodu" in teksts_low or "change language" in teksts_low:
                    pogas = {"inline_keyboard": [
                        [{"text": "Latviešu 🇱🇻", "callback_data": "lang_lv"}, {"text": "English 🇬🇧", "callback_data": "lang_en"}],
                        [{"text": "Русский 🇷🇺", "callback_data": "lang_ru"}, {"text": "Deutsch 🇩🇪", "callback_data": "lang_de"}],
                        [{"text": "Français 🇫🇷", "callback_data": "lang_fr"}, {"text": "Español 🇪🇸", "callback_data": "lang_es"}],
                        [{"text": "Italiano 🇮🇹", "callback_data": "lang_it"}, {"text": "Polski 🇵🇱", "callback_data": "lang_pl"}],
                        [{"text": "简体中文 🇨🇳", "callback_data": "lang_zh"}, {"text": "हिन्दी 🇮🇳", "callback_data": "lang_hi"}]
                    ]}
                    suti_zinu(chat_id, "Izvēlies valodu / Select language:", pogas)

                elif "kripto" in teksts_low or "crypto" in teksts_low:
                    cenas = dabut_cenas_coingecko()
                    if cenas:
                        atbilde_txt = "🪙 *Kriptovalūtas:*\n\n"
                        for k in ['btc', 'eth', 'sol']:
                            inf = PRODUKTI[k]
                            if inf['id'] in cenas:
                                atbilde_txt += f"{inf['emoji']} {inf['name']}: `${cenas[inf['id']]['usd']:.2f}`\n"
                        suti_zinu(chat_id, atbilde_txt, dabut_galveno_menu(lang))
                
                elif "metāl" in teksts_low or "metal" in teksts_low:
                    cenas = dabut_cenas_coingecko()
                    if cenas:
                        atbilde_txt = "💰 *Metāli:*\n\n"
                        for k in ['zelts', 'sudrabs']:
                            inf = PRODUKTI[k]
                            if inf['id'] in cenas:
                                atbilde_txt += f"{inf['emoji']} {inf['name']}: `${cenas[inf['id']]['usd']:.2f}`\n"
                        suti_zinu(chat_id, atbilde_txt, dabut_galveno_menu(lang))

                elif teksts_low.startswith("feedback"):
                    ats = teksts[8:].strip()
                    if ats:
                        atsauksmes_saraksts.append({"user": chat_id, "text": ats})
                        saglabat_failu(ATSAUKSMJU_FAILS, atsauksmes_saraksts)
                        suti_zinu(chat_id, t['fb_ok'], dabut_galveno_menu(lang))
    time.sleep(1)
    except:
        time.sleep(5)
print("Bots darbojas!")
bot.polling(none_stop=True)


