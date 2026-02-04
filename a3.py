import requests
import re
import json
import os
import time
import threading
import telebot
from telebot import TeleBot, types
from colorama import Fore, init

# Initialize Colors
init(autoreset=True)
G = Fore.GREEN
W = Fore.WHITE
R = Fore.RED
Y = Fore.YELLOW
C = Fore.CYAN

# --- CONFIGURATION ---
CONFIG_FILE = "config.json"

BIRD_LOGO = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣠⣼⠂⠀⠀⠀⠀⠙⣦⢀⠀⠀⠀⠀⠀⢶⣤⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣿⣿⣿⣿⣿⣿⣿⣿⠷⢦⠀⣹⣶⣿⣦⣿⡘⣇⠀⠀⠀⢰⠾⣿⣿⣿⣟⣻⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⢺⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⢟⣥⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⢻⣿⣿⡏⢹⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣮⣝⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢛⣿⣿⣿⡇⠀⠀⠀⠀⠛⣿⣿⣷⡀⠘⢿⣧⣻⡷⠀⠀⠀⠀⠀⠀⣿⣿⣿⣟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣝⢧⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣾⣿⠟⣡⣾⣿⣿⣧⣿⡿⣋⣴⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⢻⣿⣿⣿⣶⡄⠙⠛⠁⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣷⣝⢻⣿⣟⣿⣿⣷⣮⡙⢿⣽⣆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡿⢋⣴⣿⣿⣿⣿⣿⣼⣯⣾⣿⣿⡿⣻⣿⣿⣿⣦⠀⠀⠀⠀⢀⣹⣿⣿⣿⣿⣶⣤⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⠻⣿⣿⣿⣮⣿⣿⣿⣿⣿⣿⣦⡙⢿⣇⠀⠀⠀⠀
⠀⠀⠀⣠⡏⣰⣿⣿⡿⢿⣿⣿⣿⣿⣿⣿⡿⢋⣼⣿⣿⣿⣿⣿⣷⡤⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⢠⣾⣿⣿⣿⣿⣿⣷⡜⢿⣿⣿⣿⣿⣿⣿⡿⠿⣿⣿⣦⡙⣦⠀⠀⠀
⠀⠀⣰⢿⣿⣿⠟⠋⣠⣾⣿⣿⣿⣿⣿⠛⢡⣾⡿⢻⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠻⣿⡟⣿⣿⣿⠻⢿⣿⣿⣿⣿⣿⣿⣿⣟⠻⣿⣆⠙⢿⣿⣿⣿⣿⣿⣦⡈⠻⣿⣿⣟⣧⠀⠀
⠀⣰⢣⣿⡿⠃⣠⡾⠟⠁⠀⣸⣿⡟⠁⢀⣿⠋⢠⣿⡏⣿⣿⣿⣿⣿⢿⠁⢀⣠⣴⢿⣷⣿⣿⣿⠀⠀⠽⢻⣿⣿⣿⣿⡼⣿⡇⠈⢿⡆⠀⠻⣿⣧⠀⠈⠙⢿⣆⠈⠻⣿⣎⢧⠀
⠀⢣⣿⠟⢀⡼⠋⠀⠀⢀⣴⠿⠋⠀⠀⣾⡟⠀⢸⣿⠙⣿⠃⠘⢿⡟⠀⣰⢻⠟⠻⣿⣿⣿⣿⣿⣀⠀⠀⠘⣿⠋⠀⣿⡇⣿⡇⠀⠸⣿⡄⠀⠈⠻⣷⣄⠀⠀⠙⢷⡀⠙⣿⣆⠁
⢀⣿⡏⠀⡞⠁⢀⡠⠞⠋⠁⠀⠀⠀⠈⠉⠀⠀⠀⠿⠀⠈⠀⠀⠀⠀⠀⣿⣿⣰⣾⣿⣿⣿⣿⣿⣿⣤⠀⠀⠀⠀⠀⠉⠀⠸⠃⠀⠀⠈⠋⠀⠀⠀⠀⠙⠳⢤⣀⠀⠹⡄⠘⣿⡄
⣸⡟⠀⣰⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⠿⠿⠟⠁⠀⠹⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣧⠀⢹⣷
⣿⠃⢠⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⣤⣀⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⡇⠀⣿
⣿⠀⢸⠅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠋⠉⢻⣧⢀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⢸
⡇⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣧⡀⠀⠀⣿⣾⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⢸
⢸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠿⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾
"""

NAME_LOGO = r"""
 _____   _   _  __  _____           _  __
|_   _| (_) | |/ / |_   _|   ___   | |/ /
  | |   | | | ' /    | |    / _ \  | ' / 
  | |   | | | . \    | |   | (_) | | . \ 
  |_|   |_| |_|\_\   |_|    \___/  |_|\_\
"""

# --- UTILS ---
def save_config(token):
    with open(CONFIG_FILE, "w") as f: json.dump({"token": token}, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except: return None
    return None

def get_all_info(username):
    t = int(time.time() * 1000)
    url = f"https://www.tiktok.com/@{username}?_t={t}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    try:
        r = requests.get(url, headers=headers, timeout=12)
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', r.text)
        if match:
            data = json.loads(match.group(1))
            user_detail = data.get('__DEFAULT_SCOPE__', {}).get('webapp.user-detail', {})
            info = user_detail.get('userInfo', {})
            if info:
                u, s = info['user'], info['stats']
                items = user_detail.get('itemList', [])
                last_v = items[0]['id'] if items else "none"
                return {
                    'un': u.get('uniqueId'), 'nn': u.get('nickname'),
                    'ver': "✅ موثق" if u.get('verified') else "❌ غير موثق",
                    'followers': int(s.get('followerCount', 0)),
                    'following': int(s.get('followingCount', 0)),
                    'likes': int(s.get('heartCount', 0)),
                    'id': u.get('id'), 'av': u.get('avatarLarger'),
                    'vid_url': last_v, 'bio': u.get('signature', 'لا يوجد بايو')
                }
    except: return None
    return None

# --- BOT ENGINE ---
def run_bot(token):
    bot = telebot.TeleBot(token)
    
    user_state = {}
    monitoring = {}

    def get_main_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(types.KeyboardButton("🔍 سحب معلومات شاملة"), types.KeyboardButton("📡 تشغيل الرادار"))
        markup.add(types.KeyboardButton("🛑 إيقاف الرادار"))
        return markup

    @bot.message_handler(commands=['start'])
    def welcome(message):
        bot.send_message(message.chat.id, "🌟 <b>أهلاً بك في رادار تيك توك الاحترافي</b>\n\nأرسل يوزر الحساب المستهدف الآن (بدون @):", parse_mode="HTML")

    @bot.message_handler(func=lambda m: m.text == "🔍 سحب معلومات شاملة")
    def info_btn(message):
        user = user_state.get(message.chat.id)
        if not user: return bot.reply_to(message, "❌ الرجاء إرسال اليوزر أولاً")
        bot.send_chat_action(message.chat.id, 'typing')
        data = get_all_info(user)
        if data:
            cap = (f"👤 <b>الاسم:</b> <code>{data['nn']}</code>\n"
                   f"🆔 <b>اليوزر:</b> <code>@{data['un']}</code>\n"
                   f"🛡️ <b>التوثيق:</b> {data['ver']}\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"👥 <b>المتابعين:</b> <code>{data['followers']}</code>\n"
                   f"📉 <b>يتابع:</b> <code>{data['following']}</code>\n"
                   f"❤️ <b>اللايكات:</b> <code>{data['likes']}</code>\n"
                   f"🔢 <b>الآيدي:</b> <code>{data['id']}</code>\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"📝 <b>البايو:</b>\n<pre>{data['bio']}</pre>")
            bot.send_photo(message.chat.id, data['av'], caption=cap, parse_mode="HTML")
        else: bot.reply_to(message, "❌ فشل السحب. الحساب قد يكون خاصاً.")

    @bot.message_handler(func=lambda m: m.text == "📡 تشغيل الرادار")
    def track_btn(message):
        user = user_state.get(message.chat.id)
        if not user: return bot.reply_to(message, "❌ الرجاء إرسال اليوزر أولاً")
        mon_key = f"{message.chat.id}_{user}"
        if mon_key in monitoring: return bot.reply_to(message, "⚠️ الرادار يعمل بالفعل.")
        monitoring[mon_key] = True
        bot.send_message(message.chat.id, f"📡 تم تفعيل الرادار لـ @{user}...")
        threading.Thread(target=watch_task, args=(bot, message.chat.id, user, mon_key, monitoring), daemon=True).start()

    @bot.message_handler(func=lambda m: m.text == "🛑 إيقاف الرادار")
    def stop_btn(message):
        user = user_state.get(message.chat.id)
        mon_key = f"{message.chat.id}_{user}"
        if mon_key in monitoring:
            del monitoring[mon_key]
            bot.reply_to(message, f"🛑 تم إيقاف الرادار لـ @{user}")
        else: bot.reply_to(message, "❌ الرادار غير نشط.")

    @bot.message_handler(func=lambda m: True)
    def handle_msg(message):
        user = message.text.replace('@', '').strip()
        user_state[message.chat.id] = user
        bot.send_message(message.chat.id, f"📍 تم تحديد الهدف: <code>@{user}</code>", reply_markup=get_main_keyboard(), parse_mode="HTML")

    def watch_task(bot, chat_id, user, mon_key, monitor_dict):
        initial = get_all_info(user)
        if not initial: return
        l_f, l_l, l_v = initial['followers'], initial['likes'], initial['vid_url']
        while mon_key in monitor_dict:
            try:
                time.sleep(10)
                now = get_all_info(user)
                if now:
                    updates = []
                    if now['followers'] != l_f:
                        diff = now['followers'] - l_f
                        updates.append(f"{'📈 زاد' if diff > 0 else '📉 نقص'} متابعين: <code>{abs(diff)}</code> (الإجمالي: <code>{now['followers']}</code>)")
                        l_f = now['followers']
                    if now['likes'] != l_l:
                        diff = now['likes'] - l_l
                        updates.append(f"{'❤️ زادت' if diff > 0 else '💔 نقصت'} لايكات: <code>{abs(diff)}</code> (الإجمالي: <code>{now['likes']}</code>)")
                        l_l = now['likes']
                    if now['vid_url'] != l_v:
                        updates.append(f"🎬 <b>تم نشر فيديو جديد الآن!</b>")
                        l_v = now['vid_url']
                    if updates:
                        bot.send_message(chat_id, f"⚡ <b>تحديث الرادار (@{user}):</b>\n" + "\n".join(updates), parse_mode="HTML")
            except: pass

    print(f"{G}[+] Bot is active on Telegram. Run /start in your bot.{W}")
    bot.infinity_polling()

# --- CLI INTERFACE ---
os.system('clear')
print(f"{G}{BIRD_LOGO}")
print(f"{C}{NAME_LOGO}")
print(f"\n{W}--- [ Mohamed the Legend ] ---")

config = load_config()
if config:
    # Colored Token Highlight (Yellow)
    masked_token = f"{Y}{config['token'][:10]}****{W}"
    print(f"{G}[!] Saved session found: {masked_token}")
    print(f"{C}[1] Continue with saved session")
    print(f"{C}[2] Use a new token")
    choice = input(f"\n{G}Selection: {W}")
    if choice == '1':
        run_bot(config['token'])
    else:
        new_t = input(f"{G}Enter New Bot Token: {W}")
        save_config(new_t)
        run_bot(new_t)
else:
    print(f"{R}[!] No saved sessions found.")
    new_t = input(f"{G}Please enter your Telegram Bot Token: {W}")
    save_config(new_t)
    run_bot(new_t)
