import urllib.request
import json
import ssl
import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# BOT KONFIGURĀCIJA
bota_parole = "8871535091:AAEmR6qWY-zcI5iLmli_5dJoIPuVugRt_kM"
context = ssl._create_unverified_context()

# WEB SERVERIS (Render.com prasība, lai bots neatslēdzas)
def run_web_server():
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bots ir aktīvs")
    
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Cenas iegūšana (API)
def dabut_cenas():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,pax-gold,tether-silver&vs_currencies=usd"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=context, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except:
        return None

# GALVENAIS CIKLS
if __name__ == "__main__":
    # Startējam web serveri fonā
    threading.Thread(target=run_web_server, daemon=True).start()
    print("Bots un Web serveris darbojas!")
    
    last_update_id = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{bota_parole}/getUpdates?offset={last_update_id + 1}&timeout=30"
            with urllib.request.urlopen(url, context=context, timeout=40) as response:
                atbilde = json.loads(response.read().decode('utf-8'))
            
            if atbilde.get("result"):
                for update in atbilde["result"]:
                    last_update_id = update["update_id"]
                    # Šeit vari pievienot savu loģiku
                    print("Ziņa saņemta!")
            
            time.sleep(5)
        except Exception as e:
            print(f"Kļūda: {e}")
            time.sleep(10)
