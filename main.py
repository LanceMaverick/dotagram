import sys
import asyncio
import telepot
from telepot.async.delegate import per_chat_id, create_open

# from . import bot as oldbot

from eventbot import EventBot


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(EventBot, timeout=10)),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
