import os
import time
import bs4
import requests
from dotenv import load_dotenv

import discord


class MyClient(discord.Client):

    async def on_ready(self):
        try:
            print(f"We have logged in as {self.user.name}")
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
            await self.send_msg(message, self.user_input_example())
        name = ""
        birthday = ""
        if msg_content.startswith("$my_user_info"):
            name, birthday = msg_content[1:].split("-")
            await self.send_msg(message, self.schedule_input_example())

        if msg_content.startswith("$my_schedule_info"):
            file = requests.get(message.attachments[0].url)
            soup = bs4.BeautifulSoup(file.text, "html.parser")
            schedule = self.get_schedule(soup)
            user = User(name, birthday, Schedule(
                schedule[0],
                schedule[1],
                schedule[2],
                schedule[3],
                schedule[4],
                schedule[5],
            ))

    #         TODO: pickle data and store data in database then add method to check if today is someone's birthday
    #          and if it is then send message with birthday gif and add method to send a zen quote
    #         TODO: then add method to print all user's data to discord then find way to schedule the daily messages
    #          then add method for someone to add wish for a plan today and let every user vote on it

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


class Schedule:
    def __init__(self, sunday, monday, tuesday, wednesday,
                 thursday, friday):
        self.sunday = sunday
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday


class User:
    def __init__(self, name, birthday, schedule: Schedule = None):
        self.name = name
        self.birthday = birthday
        self.schedule = schedule


if __name__ == '__main__':
    load_dotenv()
    client = MyClient()
    client.run(os.getenv("TOKEN"))
