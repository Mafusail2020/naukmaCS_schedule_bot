import telebot
from scheduler import Schedule
import datetime
import json
from json import JSONDecodeError


TOKEN = ""
with open("./TOKEN.txt", "r") as file:
    TOKEN = file.read()

bot = telebot.TeleBot(token=TOKEN)


def get_current_week():
    """ Returns current week number based on current date """
    start_date = datetime.datetime(2025, 9, 1)  # First day of the first semester
    current_date = datetime.datetime.now()  # Current date
    delta_weeks = (current_date - start_date + datetime.timedelta(days=2)).days // 7
    return delta_weeks + 1


def is_user_registered(msg):
    """ Checks if user is already registered in users_info.json"""

    with open("./users_info.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["chat_id"] == msg.chat.id:
            return True
    return False


def check_if_admin(chat_id):
    """ Checks if user is admin

    Args:
        chat_id (int): chat ID of the user

    Returns:
        bool: True if user is admin, False otherwise, defaults to False
    """
    with open("./users_info.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["chat_id"] == chat_id:
            return user.get("is_admin", False)
    return False
    


def add_user(msg):
    """ Adds user to the users_info.json file

    Args:
        msg (telebot.types.Message): message from user
    """
    user_data = {
        "chat_id": msg.chat.id,
        "name": f"{msg.from_user.first_name} {msg.from_user.last_name}",
        "groups_list": None,
        "language": "uk"
    }

    with open("./users_info.json", "r") as file:
        users = json.load(file)

    try:
        users.append(user_data)
    except Exception as e:
        users = [user_data]
    with open("./users_info.json", "w") as file:
        json.dump(users, file)
    pass


def set_user_groups(msg, groups_list):
    """ Sets user's groups_list in users_info.json file

    Args:
        msg (telebot.types.Message): message from user
        groups_list (str): string containing user's groups separated by spaces
    """

    with open("./users_info.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["chat_id"] == msg.chat.id:
            user["groups_list"] = groups_list
            break

    with open("./users_info.json", "w") as file:
        json.dump(users, file)


@bot.message_handler(commands=['start', 'help'])
def start(msg):
    if not is_user_registered(msg):
        add_user(msg)
        bot.send_message(msg.chat.id, "Вас зареєстровано! Тепер ви можете встановити свої групи за допомогою команди /set_groups.")


    bot.send_message(msg.chat.id, "Привіт! Це бот з розкладом для ФІ КМА.\n"
                                  "Щоб зберегти свої групи, скористайтесь командою\n"
                                  "/set_groups <англ> <прогр> <укр> <матан> <дискретка> <алгебра>\n"
                                  "де:\n"
                                  "<англ> — ваша група з англійської (напр. 67) (НЕ додавайте літеру A)\n"
                                  "<прогр> — ваша група з програмування (напр. 3)\n"
                                  "<укр> — ваша група з української мови (напр. 7)\n"
                                  "<матан> — ваша група з матаналізу (напр. 2)\n"
                                  "<дискретка> — ваша група з дискретної математики (напр. 2)\n"
                                  "<алгебра> — ваша група з алгебри і геометрії (напр. 2)\n\n"
                                  "Щоб переглянути свої групи, скористайтесь командою:\n"
                                  "/get_groups\n\n"
                                  "Щоб отримати свій розклад, скористайтесь командою:\n"
                                  "/schedule\n\n"
                                  "Щоб дізнатись поточну дату та номер тижня, скористайтесь командою:\n"
                                  "/date\n\n")


@bot.message_handler(commands=['remove_user'])
def remove_user(msg):
    """ Removes user from the users_info.json file by name

    Args:
        msg (telebot.types.Message): message from user
    """

    name = msg.text.split(maxsplit=1)[1]

    with open("./users_info.json", "r") as file:
        users = json.load(file)

    previous_len = len(users)

    users = [user for user in users if user["name"] != name]

    if len(users) == previous_len:
        bot.send_message(msg.chat.id, f"Користувача '{name}' не знайдено.")
        return

    if not check_if_admin(msg.chat.id):
        bot.send_message(msg.chat.id, "У вас немає прав для використання цієї команди.")
        return


    with open("./users_info.json", "w") as file:
        json.dump(users, file)
    bot.send_message(msg.chat.id, f"Користувача '{name}' видалено.")


@bot.message_handler(commands=["get_groups"])
def get_groups(msg):
    with open("./users_info.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["chat_id"] == msg.chat.id:
            if user["groups_list"] is None:
                bot.send_message(msg.chat.id, "Ваші групи не вказані. Будь ласка, вкажіть їх за допомогою команди /set_groups.")
                return
            bot.send_message(msg.chat.id, f"Ваші групи: {user['groups_list']}")
            return

    bot.send_message(msg.chat.id, "Ви не зареєстровані. Будь ласка, скористайтесь командою /start для реєстрації.")
    

@bot.message_handler(commands=['set_groups'])
def set_groups(msg):
    bot.send_message(msg.chat.id, "Будь ласка, введіть свої групи у форматі:\n"
                                      "<англ> <прогр> <укр> <матан> <дискретка> <алгебра>")

    bot.register_next_step_handler(msg, enter_groups)


def enter_groups(msg):
    args = msg.text.split()
    if len(args) != 6:
        bot.send_message(msg.chat.id, "Неправильна кількість аргументів. Спробуйте ще раз за допомогою команди /set_groups.")
        return

    set_user_groups(msg, msg.text)
    bot.send_message(msg.chat.id, f"Ваші групи збережено як: Англ: {args[0]}\n"
                                    f"Мови програмування: {args[1]}\n"
                                    f"Українська мова: {args[2]}\n"
                                    f"Матан: {args[3]}\n"
                                    f"Дискретна математика: {args[4]}\n"
                                    f"Алгебра і геометрія: {args[5]}\n")
    

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("set_groups_"):
        groups_list = call.data.split("set_groups_")[1]
        set_user_groups(call.message, groups_list)
        bot.send_message(call.message.chat.id, f"Ваші групи збережено як: {groups_list}")

@bot.message_handler(commands=['schedule'])
def schedule(msg):
    try:
        with open("./users_info.json", "r") as file:
            users = json.load(file)

        for user in users:
            if user["chat_id"] == msg.chat.id:
                if user["groups_list"] is None:
                    raise ValueError("Ваші групи не вказані. Будь ласка, вкажіть їх за допомогою команди /set_groups.")
                args = user["groups_list"].split()
                if len(args) != 6:
                    raise ValueError("Ваші групи вказані некоректно. Будь ласка, вкажіть їх знову за допомогою команди /set_groups.")
                schedule = Schedule.get_schedule(*args, current_week=get_current_week())
                bot.send_message(msg.chat.id, schedule)
                return
            
    except ValueError as ve:
        bot.send_message(msg.chat.id, f"Помилка: {str(ve)}")


@bot.message_handler(["date"])
def get_date(msg):
    bot.send_message(msg.chat.id, f"Сьогодні {datetime.date.today()}\n\nНомер тижня: {get_current_week()}")
