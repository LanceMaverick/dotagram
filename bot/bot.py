import events
import telegram
import re
import logging
import json
import random
import beard_functions as bf
import dota_functions as df
import adapt_functions as af
import bottools as btools
import pdb
from dota2py import api
import sys
from os.path import abspath, join, dirname
import os
import datetime
from datetime import date, timedelta
import msg_texts
import register as reg
from time import sleep

sys.path.append(abspath(join(abspath(dirname(__file__)), "..")))

steam_key = os.environ.get('DOTA2_API_KEY')
if not steam_key:
    raise NameError('Please set the DOTA2_API_KEY environment variable')
api.set_api_key(steam_key)
token = os.environ.get('TG_BOT_TOKEN')
BASE_URL = 'https://api.telegram.org/bot%s' % token
LAST_UPDATE_ID = None
try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2

def main():
    update_id = None
    motion_on = False
    global BASE_URL
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename='botlog.log')

#    logging.getLogger().addHandler(logging.StreamHandler())

    bot = telegram.Bot(token=os.environ.get('TG_BOT_TOKEN'))

    try:
        LAST_UPDATE_ID = bot.getUpdates()[-1].update_id
    except IndexError:
        LAST_UPDATE_ID = None

    #keywords
    stack_queries = ['5 stack','5stack','stacked']
    greetings = ['hello','hi','hey']
    goodbyes = ['goodbye','bye','laters','cya']
    thanks = ['thanks','cheers','nice one']
    gainz_words = ['gainz']
    dota_checked = False
    patch_check_time = datetime.datetime.now()
    tags = []

    #create Mycroft AI Adapt engine
    skb_intelligence  = af.skyAdapt()


    dotes = None
    bf.delDotaTable()
    #long polling skybeard bot
    while True: #dirty

        try:    #even dirtier, oh my!

            ############## TIME CHECKS ##############
            #########################################

            #checks if it's almost time for dota
            if (dotes and not dota_checked):
                dota_t_check = dotes.tcheck(message)
                logging.info("checked",update_id)
                if (dota_t_check):
                    dota_checked = True

            #checks for new dota patches
            if bf.expiry(patch_check_time,10):
                bf.postUpdate(bot,message)

            #deletes a dota event if it is 6 hours passed the event start time
            if dotes and bf.expiry(dotes.date_dota,360):
                dotes = None
                bf.delDotaTable()

            #Get updates from bot. 10s timeout on poll, update on new message
            for update in bot.getUpdates(offset=update_id, timeout=10):
                chat_id = update.message.chat_id
                message = update.message
                text = update.message.text #.encode('utf-8')
                user = update.message.from_user


                if bf.command('/myid',text):
                    bf.sendText(bot, chat_id, user.id)

                ############ MESSAGE HANDLING ############
                ##########################################

                #latest steam news post for game. Currently just Dota
                if(bf.command('/news',text)):
                    try:
                        title = text.split('/news ',1)[1]
                    except:
                        title = 'dota'

                    if title == 'dota':
                        bf.dotaNews(bot,message)
                    else:
                        bf.sendText(bot,chat_id,title+' is not a recognised steam game') #more steam games can be added

                #send help text
                if bf.command('/help',text):
                    bf.sendText(bot,chat_id,msg_texts.help())
                    bf.sendText(bot,chat_id,msg_texts.readme())

                #display database entries which user has permission to see
                if bf.command('/database',text):
                    reg.printCats(bot,message)

                #delete catabase entry
                if bf.command('/delete cat',text):
                    reg.deleteCat(bot,message)

                #banter command
                if bf.command('/echo',text):
                    bf.echocats(bot,message)

                #send top dota feeders table and graph
                if bf.command('/topfeeds',text):
                    if 'update' in text.lower():
                        update_feeds = True
                    else:
                        update_feeds = False
                    bf.feeding(bot,message,BASE_URL,update_feeds)

                #post last dota match details of user
                if bf.command('/lastmatch',text):
                    bf.last_match(bot,message)

                if bf.command('/matches',text):
                    bf.matches(bot,message)

                if bf.command('#m_',text):
                    bf.last_match(bot,message,text.split('#m_',1)[1])

                #create or modify time of dota event
                if bf.command('/dota',text):
                    dota_checked = False
                    time = events.get_time(bot,message)
                    if (dotes):
                        dotes.set_time(time)
                        bf.sendText(bot,chat_id,'Dota time modified')
                        dotes.time_info(message)
                    else:
                        shotguns = events.get_str_list(bot,message,'with')
                        dotes = events.dota(bot,message,time)
                        logging.info('multi-shotgun:',shotguns)
                        if shotguns:
                            for cat in shotguns:
                                dotes.shotgun(message,cat)

                #delete dota event
                if bf.command('/delete dota',text):
                    if (dotes):
                        bf.sendText(bot,chat_id,'Dota event deleted')
                        dotes = None
                        bf.delDotaTable()
                    else:
                        events.nodota(bot,message)

                #shotgun a place in dota
                if bf.command('shotgun!',text):
                    if (dotes):
                        dotes.shotgun(message)
                    else:
                        events.nodota(bot,message)

                #unshotgun your place in dota
                if bf.command('unshotgun!',text):
                    if (dotes):
                        dotes.unshotgun(message,'shotgun')
                    else:
                        events.nodota(bot,message)

                #ready up for dota
                if bf.command('unready!',text):
                    if (dotes):
                        dotes.unshotgun(message,'rdry')
                    else:
                        events.nodota(bot,message)
                #un-ready up for dota
                if bf.command('ready!',text):
                    if (dotes):
                        dotes.rdry_up(message)
                    else:
                        events.nodota(bot,message)

                #reply to thank you messages
                if bf.keywords(thanks,text.lower()) and  ('skybeard' in text.lower()):
                    bf.thank(bot,chat_id,message)

                #reply to greetings messages
                if bf.keywords(greetings,text.lower()) and  ('skybeard' in text.lower()):
                    bf.greet(bot,chat_id,message)

                #reply to farewell messages
                if (bf.keywords(goodbyes,text.lower())) and ('skybeard' in text.lower()):
                    bf.goodbye(bot,chat_id,message)

                #respond to queries on if dota is 5 stacked or not
                if (bf.keywords(stack_queries,text.lower())):
                    if (dotes):
                        dotes.stack(message)
                    else:
                        events.nodota(bot,message)

                #AI tests
                intents = af.intentChecker(skb_intelligence, 0.3, text)
                try:
                    for intent in intents:
                        if intent['intent_type'] == 'DotaIntent':
                            events.dotaQuery(bot, message, dotes)
                        elif intent['intent_type'] == 'NewDotaIntent':
                            dota_checked = False
                            time = events.get_time(bot,message)
                            if (dotes):
                                dotes.set_time(time)
                                bf.sendText(bot,chat_id,'Dota time modified')
                                dotes.time_info(message)
                            else:
                                shotguns = events.get_str_list(bot,message,'with')
                                dotes = events.dota(bot,message,time)
                                logging.info('multi-shotgun:',shotguns)
                                if shotguns:
                                    for cat in shotguns:
                                        dotes.shotgun(message,cat)
                        elif intent['intent_type'] == 'StackIntent':
                            if (dotes):
                                dotes.stack(message)
                            else:
                                events.nodota(bot,message)
                except:
                    print('no intents detected')

                #tag someone in a message for the bot to send again when they're active in the chat
                pending_tag = btools.keySearch(tags,'name',user.first_name.lower())
                if pending_tag and pending_tag['chat_id']==chat_id:
                    bf.tagReply(bot,message,pending_tag)
                    i = next(index for (index, entry) in enumerate(tags) if entry['name'] == pending_tag['name'])
                    tags.pop(i)

                tag_match = re.search(r'\/tag\s*(\w+)',text)
                if tag_match:
                    tags.append(bf.msgTag(bot,message,tag_match.group(1)))
              #  print(tags)

                update_id= update.update_id + 1

        except telegram.TelegramError as e:
            if e.message in ("Bad Gateway", "Timed out"):
                sleep(1)
            else:
                raise e
        except URLError as e:
            sleep(1)


if __name__ == '__main__':
    while True: #pls no more
        main()
