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

# Šeit vari likt pārējo savu kodu (kripto cenas utt.)
# Pārliecinies, ka visos print vai tekstos izmanto .encode('utf-8') vai izvairies no garumzīmēm

print("Bots darbojas!")
bot.polling(none_stop=True)


