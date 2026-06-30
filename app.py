import os
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = '*'

from flask import Flask, request, Response
import telebot
import sqlite3
import datetime
import requests
from config import Config

app = Flask(__name__)
bot = telebot.TeleBot('8845368973:AAEIZCziKUe-EzmOBCcxgHQwT7GyyC2oE94', parse_mode="HTML")

@app.route('/sub')
def subscription():
    user_id = request.args.get('id')
    if not user_id: return "ID is missing", 400
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "database.db"))
    user = conn.execute("SELECT vpn_expiry, is_blocked FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not user or user[1] == 1: return "Access denied", 403
    try:
        r = requests.get(Config.ORIGINAL_GIST_LINK, timeout=5)
        configs_text = r.text
    except:
        configs_text = "Error loading servers"
    expire_timestamp = 0
    if user[0]:
        try:
            expiry_date = datetime.datetime.strptime(user[0], "%Y-%m-%d")
            expire_timestamp = int(expiry_date.timestamp())
        except: pass
    resp = Response(configs_text, mimetype='text/plain')
    resp.headers['Subscription-Userinfo'] = f"expire={expire_timestamp}"
    return resp

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Բարի գալուստ Veda VPN! Ընտրեք լեզուն...")
    except Exception as e:
        print(f"Պատասխան ուղարկել չհաջողվեց: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    return '!', 403
