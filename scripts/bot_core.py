import telebot
from scheduler import Schedule
import datetime
import json
from json import JSONDecodeError
from telebot import types


TOKEN = ""
with open("./TOKEN.txt", "r") as file:
    TOKEN = file.read()

bot = telebot.TeleBot(token=TOKEN)


# Global variables
ENG_BIAS = 8  # Англ groups are shifted by 8 in the schedule


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


    # Creating inline markup menu
    rmk = telebot.types.InlineKeyboardMarkup(row_width=2)
    set_groups_btn = telebot.types.InlineKeyboardButton(text='🖊️ Set Groups', callback_data='set_groups')
    get_groups_btn = telebot.types.InlineKeyboardButton(text='📋 Get Groups', callback_data='get_groups')
    get_schedule = telebot.types.InlineKeyboardButton(text="🗓️ Get Schedule", callback_data='schedule')
    get_date = telebot.types.InlineKeyboardButton(text="📅 Get Date", callback_data='date')

    rmk.add(set_groups_btn, get_groups_btn).add(get_schedule).add(get_date)


    bot.send_message(msg.chat.id, "Hello! This is a schedule bot for CS department of NaUKMA.\n"
                                  "To set your groups permanently, use command Set Groups\n"
                                  "Example: 50 3 7 2 2 2\n"
                                  "where:\n"
                                  "<англ> - your English group (e.g. 67)(Do NOT type A in the beginning)\n"
                                  "<прогр> - your Programming group (e.g. 3)\n"
                                  "<укр> - your Ukrainian group (e.g. 7)\n"
                                  "<матан> - your Math Analysis group (e.g. 2)\n"
                                  "<дискретка> - your Discrete Math group (e.g. 2)\n"
                                  "<алгебра> - your Algebra group (e.g. 2)\n\n"
                                  "To get your groups, use the command Get Groups\n\n"
                                  "To get your schedule for this week, use the command Get Schedule\n\n"
                                  "To get current date and week number, use the command Get Date\n\n", reply_markup=rmk)


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


# Get user groups from table
@bot.callback_query_handler(func=lambda call: call.data == 'get_groups')
def get_groups(callback: types.CallbackQuery):
    global ENG_BIAS

    with open("./users_info.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["chat_id"] == callback.message.chat.id:
            if user["groups_list"] is None:
                bot.send_message(callback.message.chat.id, "Your groups are not set. Please set them using /set_groups command.")
                return
            user_groups = user["groups_list"].split()
            user_groups[0] = str(int(user_groups[0]) - ENG_BIAS)  # Поправка на збитий розклад Англ
            bot.send_message(callback.message.chat.id, f"Your groups are: {" ".join(user_groups)}")
            return

    bot.send_message(callback.message.chat.id, "You are not registered. Please use /start command to register.")
    

# Set user groups
@bot.callback_query_handler(func=lambda call: call.data == 'set_groups')
def set_groups(callback: types.CallbackQuery):
    bot.send_message(callback.message.chat.id, "Please enter your groups in the following format:\n"
                                      "<англ> <прогр> <укр> <матан> <дискретка> <алгебра>")

    bot.register_next_step_handler(callback.message, enter_groups)


def enter_groups(msg):
    global ENG_BIAS

    args = msg.text.split()
    if len(args) != 6:
        bot.send_message(msg.chat.id, "Invalid number of arguments. Please try again using /set_groups command.")
        return
    
    bot.send_message(msg.chat.id, f"Your groups have been set to: Англ: {args[0]}\n"
                                    f"Мови програмування: {args[1]}\n"
                                    f"Українська мова: {args[2]}\n"
                                    f"Матан: {args[3]}\n"
                                    f"Дискретна математика: {args[4]}\n"
                                    f"Алгебра і геометрія: {args[5]}\n")

    args[0] = str(int(args[0]) + ENG_BIAS)  # Англ
    args = ' '.join(args)

    set_user_groups(msg, args)


# Return full schedule
@bot.callback_query_handler(func=lambda call: call.data == 'schedule')
def schedule(callback: types.CallbackQuery):
    try:
        with open("./users_info.json", "r") as file:
            users = json.load(file)

        for user in users:
            if user["chat_id"] == callback.message.chat.id:
                if user["groups_list"] is None:
                    raise ValueError("Your groups are not set. Please set them using /set_groups command.")
                args = user["groups_list"].split()
                if len(args) != 6:
                    raise ValueError("Your groups are not set correctly. Please set them again using /set_groups command.")
                schedule = Schedule.get_schedule(*args, current_week=get_current_week())
                bot.send_message(callback.message.chat.id, schedule)
                return
            
    except ValueError as ve:
        bot.send_message(callback.message.chat.id, f"Error: {str(ve)}")


# Return date
@bot.callback_query_handler(func=lambda call: call.data == 'date')
def get_date(callback: types.CallbackQuery):
    bot.send_message(callback.message.chat.id, f"Today is {datetime.date.today()}\n\nWeek number is {get_current_week()}")
