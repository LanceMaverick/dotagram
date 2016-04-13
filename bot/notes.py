import datetime 
import re
import logging
import pdb
import random
from beard_functions import *
from msg_texts import *
import bottools as btools
import dataset

token = os.environ.get('TG_BOT_TOKEN')
BASE_URL = 'https://api.telegram.org/bot%s' % token

class note:
    def __init__(self, bot, message, time):
        
        self.bot = bot
        self.creator=message.from_user
        self.message = message 
