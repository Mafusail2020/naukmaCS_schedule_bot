import pandas as pd


class Lesson:
    def __init__(self, name, time, place, teacher, group):
        self.name = name
        self.time = time
        self.place = place
        self.teacher = teacher
        self.group = group


df = pd.read_excel("./schedules/CS_schedule.xlsx")
week = {}

for i in range(len(df)):
    if not pd.isna(df.iloc[i, 0]):
        if df.iloc[i, 0] in ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота"]:
            week[df.iloc[i, 0]] = i
print(week)
