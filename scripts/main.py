import bot_core


if __name__ == "__main__":
    print("Bot started")

    bot_core.excecutor.start_polling(bot_core.dp)
