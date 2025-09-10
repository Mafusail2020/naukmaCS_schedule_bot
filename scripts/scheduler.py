import pandas as pd


class Lesson:
    def __init__(self, name, time, place, teacher, group, weeks, day):
        self.name = name
        self.time = time
        self.place = place
        self.teacher = teacher
        self.group = group
        self.weeks = weeks
        self.day = day


class Schedule:
    schedule = []

    @classmethod
    def get_schedule(cls):
        result = ''
        for day in cls.schedule:
            result += day[0].day + '\n'
            for lesson in day:
                result += f"{lesson.time}\t{lesson.name}\t\t{lesson.place}\t{lesson.teacher}\t{lesson.group}\t{lesson.weeks}\n"
            result += '\n'
        return result


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

schedule = [] # list of all lessons in the week by days
for i in range(len(week_schedule)): # iterate through days
    schedule.append([])
    current_day = week_schedule[i]

    last_time_index = 0 # to assign time to lessons where its missing
    for j in range(len(current_day)): # iterate through lessons in the day and make object for each lesson
        if not pd.isna(current_day.iloc[j, 1]):
            last_time_index = j

            if not pd.isna(current_day.iloc[j, 2]):
                lesson_name = current_day.iloc[j, 2].split(", ")[0].strip() if ", " in current_day.iloc[j, 2] else current_day.iloc[j, 2]
                lesson_teacher = current_day.iloc[j, 2].split(",")[-1].strip() if ", " in current_day.iloc[j, 2] else ""
            else:
                lesson_name = "-"
                lesson_teacher = "-"
            lesson_time = current_day.iloc[j, 1]
            lesson_place = current_day.iloc[j, 5]
            lesson_group = current_day.iloc[j, 3]
            lesson_weeks = current_day.iloc[j, 4]
            lesson_day = ["Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "Субота"][i]

            lesson = Lesson(lesson_name, lesson_time, lesson_place, lesson_teacher, lesson_group, lesson_weeks, lesson_day)
        else:
            if not pd.isna(current_day.iloc[j, 2]):
                lesson_name = current_day.iloc[j, 2].split(", ")[0].strip() if ", " in current_day.iloc[j, 2] else current_day.iloc[j, 2]
                lesson_teacher = current_day.iloc[j, 2].split(",")[-1].strip() if ", " in current_day.iloc[j, 2] else ""
            else:
                lesson_name = "-"
                lesson_teacher = "-"
            lesson_time = current_day.iloc[last_time_index, 1]
            lesson_place = current_day.iloc[j, 5]
            lesson_group = current_day.iloc[j, 3]
            lesson_weeks = current_day.iloc[j, 4]
            lesson_day = ["Понеділок", "Вівторок", "Середа", "Четвер", "П`ятниця", "Субота"][i]

            lesson = Lesson(lesson_name, lesson_time, lesson_place, lesson_teacher, lesson_group, lesson_weeks, lesson_day)
        schedule[i].append(lesson)


Schedule.schedule = schedule
print(Schedule().get_schedule())
