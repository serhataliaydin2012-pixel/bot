from flask import Flask
from threading import Thread

app = Flask('')

# Botun durumunu tutacak değişken
bot_status = "Başlatılıyor..."

@app.route('/')
def home():
    return f"<h1>Bot Paneli</h1><p>Bot Durumu: <b>{bot_status}</b></p>"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()