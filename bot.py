import telebot
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Pārliecinies, ka tev šeit ir pareizais bota token
TOKEN = 'TEV_JABUT_TAVAM_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# HTTP serveris, lai Render.com nedomātu, ka bots ir "miris"
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        # Šeit izmantojam .encode('utf-8'), lai nebūtu kļūdu ar latviešu burtiem
        self.wfile.write("Bots ir aktivs".encode('utf-8'))

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# Palaižam serveri paralēli botam
threading.Thread(target=run_server, daemon=True).start()

# Tālāk nāk tavs pārējais bota kods...
# (Pārliecinies, ka arī pārējās rindiņās, kur raksti tekstus, 
# izmanto normālus burtus vai .encode('utf-8'), ja tas ir baitu formāts)

bot.polling(none_stop=True)

