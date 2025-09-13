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
        bot.send_message(msg.chat.id, "You have been registered! Now you can set your groups using /set_groups command.")


    bot.send_message(msg.chat.id, "Hello! This is a schedule bot for CS department of NaUKMA.\n"
                                  "To set your groups permanently, use this command\n"
                                  "/set_groups <англ> <прогр> <укр> <матан> <дискретка> <алгебра>\n"
                                  "where:\n"
                                  "<англ> - your English group (e.g. 67)(Do NOT type A in the beginning)\n"
                                  "<прогр> - your Programming group (e.g. 3)\n"
                                  "<укр> - your Ukrainian group (e.g. 7)\n"
                                  "<матан> - your Math Analysis group (e.g. 2)\n"
                                  "<дискретка> - your Discrete Math group (e.g. 2)\n"
                                  "<алгебра> - your Algebra group (e.g. 2)\n\n"
                                  "To get your groups, use the command:\n"
                                  "/get_groups\n\n"
                                  "To get your schedule, use the command:\n"
                                  "/schedule\n\n"
                                  "To get current date and week number, use the command:\n"
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
        bot.send_message(msg.chat.id, f"User '{name}' not found.")
        return

    if not check_if_admin(msg.chat.id):
        bot.send_message(msg.chat.id, "You are not authorized to use this command.")
        return


    with open("./users_info.json", "w") as file:
        json.dump(users, file)
    bot.send_message(msg.chat.id, f"User '{name}' removed.")


@bot.message_handler(commands=["get_groups"])
def get_groups(msg):
    with open("./users_info.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["chat_id"] == msg.chat.id:
            if user["groups_list"] is None:
                bot.send_message(msg.chat.id, "Your groups are not set. Please set them using /set_groups command.")
                return
            bot.send_message(msg.chat.id, f"Your groups are: {user['groups_list']}")
            return

    bot.send_message(msg.chat.id, "You are not registered. Please use /start command to register.")
    

@bot.message_handler(commands=['set_groups'])
def set_groups(msg):
    bot.send_message(msg.chat.id, "Please enter your groups in the following format:\n"
                                      "<англ> <прогр> <укр> <матан> <дискретка> <алгебра>")

    bot.register_next_step_handler(msg, enter_groups)


def enter_groups(msg):
    args = msg.text.split()
    if len(args) != 6:
        bot.send_message(msg.chat.id, "Invalid number of arguments. Please try again using /set_groups command.")
        return

    set_user_groups(msg, msg.text)
    bot.send_message(msg.chat.id, f"Your groups have been set to: Англ: {args[0]}\n"
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
        bot.send_message(call.message.chat.id, f"Your groups have been set to: {groups_list}")

@bot.message_handler(commands=['schedule'])
def schedule(msg):
    try:
        with open("./users_info.json", "r") as file:
            users = json.load(file)

        for user in users:
            if user["chat_id"] == msg.chat.id:
                if user["groups_list"] is None:
                    raise ValueError("Your groups are not set. Please set them using /set_groups command.")
                args = user["groups_list"].split()
                if len(args) != 6:
                    raise ValueError("Your groups are not set correctly. Please set them again using /set_groups command.")
                schedule = Schedule.get_schedule(*args, current_week=get_current_week())
                bot.send_message(msg.chat.id, schedule)
                return
            
    except ValueError as ve:
        bot.send_message(msg.chat.id, f"Error: {str(ve)}")


@bot.message_handler(["date"])
def get_date(msg):
    bot.send_message(msg.chat.id, f"Today is {datetime.date.today()}\n\nWeek number is {get_current_week()}")
