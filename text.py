import telebot
import os
import time
import requests

# Pegando o token do ambiente (Replit -> Secrets)
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Dicionário para controle de limite de likes por usuário (você pode remover)
user_likes = {}

# ========================
# Função de like (padrão)
# ========================
@bot.message_handler(commands=['like'])
def send_like(message):
    try:
        user_id = message.from_user.id

        # ⚠️ REMOVE O LIMITE se quiser
        # if user_id in user_likes and user_likes[user_id] >= 50:
        #     bot.reply_to(message, "❌ Você atingiu o limite diário de likes.")
        #     return

        # Exemplo de uso: /like sg 1234567
        try:
            _, tipo, idalvo = message.text.split()
        except:
            bot.reply_to(message, "❌ Use o formato correto: `/like sg 1234567`", parse_mode='Markdown')
            return

        url = f"https://free-api-like-freefire.vercel.app/api?type={tipo}&id={idalvo}"
        r = requests.get(url)
        data = r.json()

        if data["success"]:
            # user_likes[user_id] = user_likes.get(user_id, 0) + 1  # Se quiser contar likes
            bot.reply_to(message, f"✅ Like enviado com sucesso!\n🎯 ID: {idalvo}\n📊 Status: {data['message']}")
        else:
            bot.reply_to(message, f"❌ Falha: {data['message']}")
    except Exception as e:
        bot.reply_to(message, f"Erro interno:\n{str(e)}")

# Comando opcional para verificar total de likes usados (se mantiver o limite)
@bot.message_handler(commands=['check'])
def check_likes(message):
    user_id = message.from_user.id
    total = user_likes.get(user_id, 0)
    bot.reply_to(message, f"📊 Você já usou {total} likes hoje.")

# Comando padrão de boas-vindas
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Bem-vindo!\nUse `/like sg 1234567` para enviar um like!", parse_mode='Markdown')

# Inicia o bot
print("🤖 Bot online!")
bot.polling()

