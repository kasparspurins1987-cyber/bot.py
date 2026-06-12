import urllib.request, json, ssl, time, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

bota_parole = "8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM"
context = ssl._create_unverified_context()

# --- SERVERIS ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bots ir aktivs")
def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler); server.serve_forever()
threading.Thread(target=run_server, daemon=True).start()

# --- CENA ---
def dabut_cenas():
    try:
        # Izmantojam stabilāku URL un reālu pārlūka galveni
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,tether-silver&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"API kļūda: {e}")
        return None

def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except: pass

# --- CIKLS ---
last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r: atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    txt = update["message"].get("text", "").lower()
                    
                    if "kripto" in txt:
                        c = dabut_cenas()
                        if c:
                            msg = f"🪙 *Kripto cenas:*\n₿ BTC: {c['bitcoin']['usd']}$\n♦️ ETH: {c['ethereum']['usd']}$\n☀️ SOL: {c['solana']['usd']}$"
                            suti_zinu(chat_id, msg)
                        else: suti_zinu(chat_id, "⚠️ API kļūda, mēģini vēlreiz.")
                    elif "metālu" in txt:
                        c = dabut_cenas()
                        if c:
                            msg = f"💰 *Metālu cenas:*\n💰 Zelts: {c['pax-gold']['usd']}$\n🥈 Sudrabs: {c['tether-silver']['usd']}$"
                            suti_zinu(chat_id, msg)
                        else: suti_zinu(chat_id, "⚠️ API kļūda.")
                    elif "analīze" in txt: suti_zinu(chat_id, "📰 *Tirgus Analīze:* Finanšu tirgi šobrīd konsolidējas.")
                    elif "alert" in txt: suti_zinu(chat_id, "🔔 *Mani Alerti:* Pašlaik nav aktīvu alertu.")
                    elif "feedback" in txt or "atsauksmes" in txt: suti_zinu(chat_id, "✅ Paldies par atsauksmi!")
                    elif "izdzēst" in txt: suti_zinu(chat_id, "🗑️ Visi alerti izdzēsti.")
                    elif "start" in txt or "valodu" in txt:
                        pogas = {"inline_keyboard": [[{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}]]}
                        suti_zinu(chat_id, "Izvēlies valodu:", pogas)
        time.sleep(1)
    except: time.sleep(5)
