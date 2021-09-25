import asyncio
import audioop
import os

from discord.ext import commands
import datetime
from dotenv import load_dotenv


async def timer(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel(888477277644550147)  # replace with channel ID that you want to send to
    msg_sent = False
    await channel.send('Its 6 am')
    while True:
        if datetime.time().hour == 6 and datetime.time().minute == 0:
            if not msg_sent:
                await channel.send('Its 6 am')
                msg_sent = True
        else:
            msg_sent = False
    await asyncio.sleep(2)


async def sta():
    bot = commands.Bot(command_prefix='!')

    load_dotenv()
    bot.loop.create_task(timer(bot))
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    await sta()
