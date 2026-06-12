import urllib.request
import json
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

bota_parole = "8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM"
context = ssl._create_unverified_context()

# --- SERVERIS ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Bots ir aktivs".encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- DATI ---
PRODUKTI = {
    'btc': {'id': 'bitcoin', 'name': 'Bitcoin (BTC)', 'emoji': '₿'},
    'eth': {'id': 'ethereum', 'name': 'Ethereum (ETH)', 'emoji': '♦️'},
    'sol': {'id': 'solana', 'name': 'Solana (SOL)', 'emoji': '☀️'},
    'zelts': {'id': 'pax-gold', 'name': 'Zelts (PAXG)', 'emoji': '💰'},
    'sudrabs': {'id': 'tether-silver', 'name': 'Sudrabs (SILVER)', 'emoji': '🥈'}
}

# --- FUNKCIJAS ---
def suti_zinu(chat_id, text, pogas=None):
    try:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if pogas: data["reply_markup"] = json.dumps(pogas)
        req = urllib.request.Request(f"https://api.telegram.org/bot{bota_parole}/sendMessage", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, context=context, timeout=10)
    except: pass

def dabut_cenas():
    try:
        ids = ",".join([p['id'] for p in PRODUKTI.values()])
        req = urllib.request.Request(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=8) as r: return json.loads(r.read().decode('utf-8'))
    except: return None

# --- CIKLS ---
last_update_id = 0
while True:
    try:
        url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=10"
        with urllib.request.urlopen(url, context=context, timeout=20) as r:
            atbilde = json.loads(r.read().decode('utf-8'))
        
        if atbilde.get("result"):
            for update in atbilde["result"]:
                last_update_id = update["update_id"]
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    txt = update["message"].get("text", "").lower().replace("/", "")
                    
                    if "start" in txt:
                        pogas = {"inline_keyboard": [
                            [{"text": "🇱🇻 LV", "callback_data": "lang_lv"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}],
                            [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇩🇪 DE", "callback_data": "lang_de"}]
                        ]}
                        suti_zinu(chat_id, "Izvēlies valodu:", pogas)
                    
                    elif "kripto" in txt or "crypto" in txt:
                        cenas = dabut_cenas()
                        if cenas:
                            msg = "🪙 *Cenas:*\n"
                            for k in ['btc', 'eth', 'sol']:
                                if PRODUKTI[k]['id'] in cenas: msg += f"{PRODUKTI[k]['emoji']} {PRODUKTI[k]['name']}: {cenas[PRODUKTI[k]['id']]['usd']}$\n"
                            suti_zinu(chat_id, msg)
                            
                    elif "feedback" in txt:
                        suti_zinu(chat_id, "✅ Atsauksme saņemta.")
                        
        time.sleep(1)
    except Exception as e:
        print(f"Kļūda: {e}")
        time.sleep(5)
