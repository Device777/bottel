import telebot
import requests
import datetime
import time

BOT_TOKEN = "8313539937:AAEfhvr3Sy7CZbFnz7JD6dfEbyBi08qXD4c"
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_USERNAME = "tools_channe"
AUTHORIZED_OWNERS = [5339705829]  # Replace with your ID

# === Data Stores ===
group_promotions = {}  # {group_id: promotion_text}
group_custom_usernames = {}  # {group_id: custom_username}
temp_admins = {}  # {group_id: {user_id: expiry_date}}
temp_group_limits = {}  # {group_id: {"limit": x, "expires": date}}

# === Utility Functions ===
def safe_reply(bot, message, text, parse_mode=None, reply_markup=None):
    try:
        return bot.reply_to(message, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except:
        try:
            return bot.send_message(message.chat.id, text, reply_to_message_id=message.id, parse_mode=parse_mode, reply_markup=reply_markup)
        except:
            return bot.send_message(message.chat.id, text, parse_mode=parse_mode, reply_markup=reply_markup)

def is_owner(user_id):
    return user_id in AUTHORIZED_OWNERS

def get_promotion_text(chat_id):
    return group_promotions.get(chat_id, "")

def get_custom_username(chat_id):
    return group_custom_usernames.get(chat_id, "@Daddy_chips")

def is_admin_in_group(group_id, user_id):
    return temp_admins.get(group_id, {}).get(user_id, datetime.date.min) >= datetime.datetime.now().date()

# === Verification ===
def check_user_joined(user_id):
    try:
        status = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=["verify"])
def manual_verify(message):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Join Channel ✅", url=f"https://t.me/{CHANNEL_USERNAME}")
    button2 = telebot.types.InlineKeyboardButton(text="Verify ✅", callback_data="run_verify")
    button3 = telebot.types.InlineKeyboardButton(text="Already Joined", callback_data="already_joined")
    markup.add(button1, button2, button3)
    safe_reply(bot, message, "🔒 Verification Needed\n\nTo use our bot, you must join our official channel.\n\n👉 [Join Now](https://t.me/Marco_lab)\nAfter joining, click the 'Verify' button below ⬇️.", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["run_verify", "already_joined"])
def verify_buttons(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if check_user_joined(user_id):
        bot.edit_message_text("✅ You are verified and can now use the bot. Send Again your LIKE command /like <region> uid 🫡", chat_id, call.message.message_id)
    else:
        bot.edit_message_text("❌ You must join the channel first.\nJoin: https://t.me/" + CHANNEL_USERNAME, chat_id, call.message.message_id)
    bot.answer_callback_query(call.id)

# === Commands ===
@bot.message_handler(commands=['like'])
def like_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    parts = message.text.split()
    if len(parts) != 3:
        safe_reply(bot, message, "ℹ️ Please provide a valid region and UID. Example: /like sg 10000001")
        return

    region, uid = parts[1], parts[2]
    processing_msg = safe_reply(bot, message, "🔄 Processing your request, please wait...")

    api_url = f"http://narayan-like-api-three.vercel.app/{uid}/{region}/narayan"
    try:
        api_response = requests.get(api_url)
        api_data = api_response.json()
    except Exception:
        bot.edit_message_text("An error occurred. Try again later.", chat_id, processing_msg.message_id)
        return

    if api_data.get("status") == 1:
        result_msg = f"""
🔹 <i>Player Nickname: {api_data['PlayerNickname']}</i>

🔸 <i>Likes at Start of Day: {api_data['LikesbeforeCommand']}</i>

🔸 <i>Likes Before Command: {api_data['LikesbeforeCommand']}</i>

🔸 <i>Likes After Command: {api_data['LikesafterCommand']}</i>

🔸 Likes Given By Bot: {api_data['LikesGivenByAPI']}
{get_promotion_text(chat_id)}
""".strip()

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(text="DM OWNER ☠️", url="https://t.me/Daddy_chips"),
            telebot.types.InlineKeyboardButton(text="Join Group ❤️‍🔥", url="https://t.me/ff_vip_likes")
        )
        bot.edit_message_text(result_msg, chat_id, processing_msg.message_id, parse_mode='HTML', reply_markup=markup)
    else:
        bot.edit_message_text("⚠️ UID has already received max likes for today. Try another UID 🥶", chat_id, processing_msg.message_id)

@bot.message_handler(commands=['check'])
def check_command(message):
    safe_reply(bot, message, "📊 This bot has no limits. Use /like as many times as you want! 😇")

@bot.message_handler(commands=['add'])
def add_vip(message):
    safe_reply(bot, message, "This command is disabled.")

@bot.message_handler(commands=['addgr'])
def add_group_limit(message):
    safe_reply(bot, message, "This command is disabled.")

@bot.message_handler(commands=['remain'])
def group_remain_status(message):
    safe_reply(bot, message, "This bot has no group limits.")

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    safe_reply(bot, message, "This command is disabled.")

@bot.message_handler(commands=['set'])
def set_custom_username(message):
    if not is_owner(message.from_user.id):
        safe_reply(bot, message, "You're not authorized to use this command 😅")
        return
    parts = message.text.split()
    if len(parts) != 2:
        safe_reply(bot, message, "Usage: /set @username 🤓")
        return
    group_custom_usernames[message.chat.id] = parts[1]
    safe_reply(bot, message, f"Custom username set to {parts[1]} for this group 😉")

@bot.message_handler(commands=['setpromotion'])
def set_promotion(message):
    if not is_owner(message.from_user.id):
        safe_reply(bot, message, "You are not authorized to set promotion 🤤")
        return
    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        safe_reply(bot, message, "Usage: /setpromotion your promotion text 🤑")
        return
    group_promotions[message.chat.id] = parts[1]
    safe_reply(bot, message, "Promotion text set for this group 😋")

@bot.message_handler(commands=['promotion'])
def promotion(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(text="DM Owner ☠️", url="https://t.me/Daddy_chips"),
        telebot.types.InlineKeyboardButton(text="Join Group 🔥", url="https://t.me/Daddy_chips")
    )
    safe_reply(bot, message, "📢 Here's our promotion:\n\n📩 Contact Owner or Join Group", reply_markup=markup)

# === Polling ===
while True:
    try:
        bot.polling(timeout=60, long_polling_timeout=45)
    except Exception as e:
        print("Polling failed, retrying in 10 seconds:", e)
        time.sleep(10)
