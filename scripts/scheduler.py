import pandas as pd


class Lesson:
    def __init__(self, name:str, time:str, place:str, teacher:str, group:str, weeks:str):
        self.name = str(name)
        self.time = str(time)
        self.place = str(place)
        self.teacher = str(teacher)
        self.group = str(group)

        if weeks is None:
            self.weeks = None

        elif '.' in weeks:
            self.weeks = [-1]

        elif '-' in weeks:
            self.weeks = [i for i in range(int(weeks.split('-')[0]), int(weeks.split('-')[1]) + 1)]

        elif ',' in weeks:
            w = list(weeks.split(','))
            while '' in w:
                w.remove('')
            self.weeks = [int(i) for i in map(int, w)]

        else:
            self.weeks = [int(weeks)]


# Stores all lessons of the day
class Day:
    def __init__(self, name):
        self.name = name
        self.lessons_list = []


class Schedule:
    schedule = []

    # Returns schedule for user based on set of parameters
    @classmethod
    def get_schedule(cls, user_english:str, user_programm:str, user_ukr:str, user_matan:str, user_discret:str, user_alebra:str, current_week:str):
        result = '' # stores schedule for specified params
        user_groups_list = [user_english, user_programm, user_ukr, user_matan, user_discret, user_alebra]
        short_names_list = ["анг", "мов", "укр", "мат", "дис", "алг"]

        for day in cls.schedule:
            ll = day.lessons_list
            result += f"● {day.name}\n"

            for lesson in ll:
                # check if lesson is a lecture or if it is for the current week
                if lesson.name is None or lesson.weeks is None:
                    continue
                if int(current_week) not in lesson.weeks:
                    continue
                if type(lesson.group) is not int:
                    if "лекц" in lesson.group.lower():
                        result += cls.__generate_row(lesson)
                        continue

                # check if user is in lessons group
                if user_groups_list[short_names_list.index(lesson.name.lower()[:3])] in lesson.group:
                    result += cls.__generate_row(lesson)
                    continue

            result += '\n'

        result += f"\nРезультат за тижнем {current_week}\n"
        return result

    @staticmethod
    def __generate_row(lesson):
        return f"• {lesson.time}\t{lesson.name}\t\t{lesson.place}\t{lesson.teacher}\t{lesson.group}\n"


df = pd.read_excel("./schedules/CS_schedule.xlsx")
week_id = [] # mapping day names to their starting row indexes

# get indexes of the start of each day
for i in range(len(df)):
    if not pd.isna(df.iloc[i, 0]):
        if df.iloc[i, 0] in ["Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "Субота"]:
            week_id.append(i)

# split dataframe into days
week_schedule = []
for i in range(len(week_id) - 1):
    day_schedule = df.iloc[week_id[i]:week_id[i + 1]]
    week_schedule.append(day_schedule)

schedule = [Day(["Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "Субота"][i]) for i in range(5)] # list of all lessons in the week by days
for i in range(len(week_schedule)): # iterate through days
    current_day = week_schedule[i]

    last_time_index = 0 # to assign time to lessons where its missing
    for j in range(len(current_day)): # iterate through lessons in the day and make object for each lesson
        if not pd.isna(current_day.iloc[j, 1]):
            last_time_index = j

            if not pd.isna(current_day.iloc[j, 2]):
                lesson_name = current_day.iloc[j, 2].split(", ")[0].strip() if ", " in current_day.iloc[j, 2] else current_day.iloc[j, 2]
                lesson_teacher = current_day.iloc[j, 2].split(",")[-1].strip() if ", " in current_day.iloc[j, 2] else ""
                lesson_time = current_day.iloc[j, 1]
                lesson_place = current_day.iloc[j, 5]
                lesson_group = current_day.iloc[j, 3]
                lesson_weeks = current_day.iloc[j, 4]
            else:
                lesson_name = None
                lesson_teacher = None
                lesson_time = current_day.iloc[j, 1]
                lesson_place = None
                lesson_group = None
                lesson_weeks = None

            lesson = Lesson(lesson_name, lesson_time, lesson_place, lesson_teacher, lesson_group, lesson_weeks)
        else:
            if not pd.isna(current_day.iloc[j, 2]):
                lesson_name = current_day.iloc[j, 2].split(", ")[0].strip() if ", " in current_day.iloc[j, 2] else current_day.iloc[j, 2]
                lesson_teacher = current_day.iloc[j, 2].split(",")[-1].strip() if ", " in current_day.iloc[j, 2] else ""
                lesson_time = current_day.iloc[last_time_index, 1]
                lesson_place = current_day.iloc[j, 5]
                lesson_group = current_day.iloc[j, 3]
                lesson_weeks = current_day.iloc[j, 4]
            else:
                lesson_name = None
                lesson_teacher = None
                lesson_time = current_day.iloc[j, 1]
                lesson_place = None
                lesson_group = None
                lesson_weeks = None

            lesson = Lesson(lesson_name, lesson_time, lesson_place, lesson_teacher, lesson_group, lesson_weeks)
        schedule[i].lessons_list.append(lesson)


Schedule.schedule = schedule
