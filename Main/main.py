import asyncio
import os
import time
import bs4
import requests
from dotenv import load_dotenv
import sqlite3
import discord
import pickle
import datetime
import json
from datetime import date
import calendar
from discord.ext import tasks, commands


class Schedule:
    def __init__(self, sunday, monday, tuesday, wednesday,
                 thursday, saturday):
        self.sunday = sunday
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.saturday = saturday
        self.all_days = [
            self.saturday,
            self.sunday,
            self.monday,
            self.tuesday,
            self.wednesday,
            self.thursday,
        ]


class User:
    def __init__(self, name, birthday, schedule: Schedule = None):
        self.name = name
        self.birthday = birthday
        self.schedule = schedule


class MyClient(discord.Client):
    current_name = ""
    current_birthday = ""
    channel = None

    async def on_ready(self):
        try:
            print(f"We have logged in as {self.user.name}")
            self.channel = discord.utils.get(self.get_all_channels(), name="general")

        except:
            await self.on_ready()

    async def on_message(self, message: discord.Message):
        msg_content = message.content
        if message.author == client.user:
            return
        if msg_content.startswith("$add_user_schedule"):
            await self.send_msg(message, "This is the schedule setup wizard!\n"
                                         "Please follow the instructions to\n"
                                         "ensure a successful setup. \n")
            time.sleep(1)
            await self.send_msg(message, self.user_input_example())
        if msg_content.startswith("$my_user_info"):
            self.current_name, self.current_birthday = msg_content[14:].split("-")
            await self.send_msg(message, self.schedule_input_example())

        if msg_content.startswith("$my_schedule_info"):
            file = requests.get(message.attachments[0].url)
            soup = bs4.BeautifulSoup(file.text, "html.parser")
            schedule = self.get_schedule(soup)
            user = User(self.current_name, self.current_birthday, Schedule(
                schedule[0],
                schedule[1],
                schedule[2],
                schedule[3],
                schedule[4],
                schedule[5],
            ))
            self.store_new_user(user)
            self.store_new_user_normal(user)

        if msg_content.startswith("$birthday"):
            birthdays = self.check_if_birthday()
            if birthdays:
                await self.send_msg(message, f"Happy Birthday {birthdays[0]}!")
            else:
                await self.send_msg(message, "No one's Birthday today...")

        if msg_content.startswith("$zen"):
            await self.send_msg(message, self.get_quote())

        if msg_content.startswith("$schedules"):
            users = self.retrieve_user_normal()
            user_schedules = self.retrieve_all_users()
            week_day = calendar.day_name[date.today().weekday()]
            for index, current_user in enumerate(users):
                await self.send_msg(message, f"{current_user[1]}:")
                await self.send_msg(message, self.make_schedule_pretty(user_schedules[index].schedule, week_day))

        if msg_content.startswith("$test"):
            self.check_if_birthday()
            self.retrieve_all_users()

    @tasks.loop(seconds=60)
    async def timer(self):

        try:
            users = self.retrieve_user_normal()
            user_schedules = self.retrieve_all_users()
            week_day = calendar.day_name[date.today().weekday()]
            await self.channel.send("\nGood Morning\n")
            await self.channel.send("-")
            if self.check_if_birthday():
                await self.channel.send(f"Happy Birthday to {self.check_if_birthday()[0]}:")
                await self.channel.send("-")
            await self.channel.send(f"\n{self.get_quote()}\n")
            await self.channel.send("-")

            for index, current_user in enumerate(users):
                await self.channel.send(f"\n{current_user[1]}:")
                await self.channel.send("-")
                await self.channel.send("\n" + self.make_schedule_pretty(user_schedules[index].schedule, week_day))
                await self.channel.send("-\n-")

        except:
            pass

    @staticmethod
    def make_schedule_pretty(schedule: Schedule, current_day: str):
        result = ""
        week_day = None
        for day in schedule.all_days:

            if day[0][0].casefold() == current_day.casefold():
                week_day = day
                break
        for i in range(5):
            try:
                result += f"{week_day[i][0]} | {week_day[i][1][0][0]} | {week_day[i][1][0][1]} | " \
                          f"{week_day[i][1][1][0]} | {week_day[i][1][1][1]} | {week_day[i][1][1][2]}\n\n"

            except:
                return "Today Is Free!"
        return result + "\n\n"

    @staticmethod
    def get_quote():
        response = requests.get("https://zenquotes.io/api/random")
        try:
            response.raise_for_status()
            json_data = json.loads(response.text)
            quote = json_data[0]["q"] + " -" + json_data[0]["a"]
            return quote
        except requests.exceptions.HTTPError:
            pass

    def store_new_user(self, user: User):
        pickled_user = pickle.dumps(user)
        connection = sqlite3.connect(
            r"C:\Users\iyade\PycharmProjects\Python-Personal-Projects\Whereabots\whereabots_users.db")
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO users (user) VALUES (?);""", (pickled_user,))
        connection.commit()
        connection.close()

    @staticmethod
    def store_new_user_normal(user: User):
        connection = sqlite3.connect(
            r"C:\Users\iyade\PycharmProjects\Python-Personal-Projects\Whereabots\normal_user_data.db")
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO user (name, birthday) VALUES (?, ?);""",
                       (user.name, user.birthday))
        connection.commit()
        connection.close()

    @staticmethod
    def retrieve_user_normal():
        results = list()
        connection = sqlite3.connect(
            r"C:\Users\iyade\PycharmProjects\Python-Personal-Projects\Whereabots\normal_user_data.db")
        cursor = connection.cursor()
        for row in cursor.execute("""SELECT * FROM user;"""):
            results.append(row)
        connection.commit()
        connection.close()
        return results

    @staticmethod
    def retrieve_all_users() -> list[User]:
        users = list()
        connection = sqlite3.connect(
            r"C:\Users\iyade\PycharmProjects\Python-Personal-Projects\Whereabots\whereabots_users.db")
        cursor = connection.cursor()
        for row in cursor.execute("""SELECT * FROM users;"""):
            unpickled_user = pickle.loads(row[1])
            users.append(unpickled_user)
        connection.commit()
        connection.close()
        return users

    def check_if_birthday(self):
        user_birthdays = list()
        current_day = datetime.datetime.today().day
        current_month = datetime.datetime.today().month
        for user in self.retrieve_user_normal():
            user_day, user_month = user[2][:5].split(".")
            if int(user_day) == int(current_day) and int(user_month) == int(current_month):
                user_birthdays.append(user[1])
        return user_birthdays

    @staticmethod
    async def send_msg(message, msg):
        await message.channel.send(msg)

    @staticmethod
    def user_input_example():
        return "$my_user_info Thomas Anderson-31.03.1999"

    @staticmethod
    def schedule_input_example():
        return "To enter your schedule into the system you must\n" \
               "first open the schedule on your portal, right click\n" \
               "on the page click on 'save as'.\n" \
               "After that just upload the file with the following command:\n" \
               "$my_schedule_info"

    @staticmethod
    def get_schedule(soup: bs4.BeautifulSoup):
        schedule_list = list(list())
        time_periods = list(tuple())
        subjects = list()
        rooms = list()
        descriptions = list()

        for i in range(6):
            schedule_list.append([])

        for subject in range(2, 32):
            try:
                subjects.append(soup.select(f"#Table{subject} > tbody > tr > td:nth-child(1) > "
                                            f"font")[
                                    0].getText())
                rooms.append(soup.select(f"#Table{subject} > tbody > tr > td:nth-child(2) > "
                                         f"font")[
                                 0].getText())
                descriptions.append(soup.select(f"#Table{subject} > tbody > tr > td:nth-child(3) > "
                                                f"font")[
                                        0].getText().split("\n")[0])
            except:
                subjects.append("Free")
                rooms.append("None")
                descriptions.append("None")

        for period in range(2, 7):
            current_period = \
                soup.select(f"#Table1 > tbody > tr:nth-child(1) > td:nth-child({period}) > "
                            f"div:nth-child("
                            f"1) > "
                            f"font")[0].getText()
            current_time_period = \
                soup.select(f"#Table1 > tbody > tr:nth-child(1) > td:nth-child({period}) > "
                            f"div:nth-child("
                            f"2) > "
                            f"font")[0].getText()
            time_periods.append((current_period, current_time_period))

        for i in range(1, 7):
            current_day = soup.select(f"#ContentPlaceHolder1_rw{i} > td:nth-child(1) > strong > font")[
                0].getText()
            for period in time_periods:
                schedule_list[i - 1].append([current_day, (period, ["Subject", "room", "description"])])

        start = 0
        end = 5
        for i in range(0, 6):
            current_period = 0
            for j in range(start, end):
                if current_period < 5:
                    schedule_list[i][current_period][1][1][0] = subjects[j]
                    schedule_list[i][current_period][1][1][1] = rooms[j]
                    schedule_list[i][current_period][1][1][2] = descriptions[j]
                    current_period += 1
            start += 5
            end += 5

        return schedule_list


if __name__ == '__main__':
    load_dotenv()
    client = MyClient()
    client.timer.start()
    client.run(os.getenv("TOKEN"))
