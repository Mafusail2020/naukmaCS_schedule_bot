import telebot


TOKEN = ""
with open("TOKEN.txt", "r") as file:
    TOKEN = file.read()
bot = telebot.TeleBot(token=TOKEN)


