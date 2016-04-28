#functions called directly by the bot
import requests
import events
import telegram
import re
import random
import dota_functions as df
import bottools as btools
from msg_texts import * #imports 'msgs' dictionary
import numpy as np
import matplotlib
matplotlib.use('Agg') #disable x-forwarding
import matplotlib.pyplot as plt
import pickle
import yaml
import logging
import math
import datetime
import time
import sys
import os
import dataset
plt.xkcd()

#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout, level=logging.INFO)
#logging.getLogger().addHandler(logging.StreamHandler())

def matches(bot,message):
    try:
        dota_id = df.get_dota_id_from_telegram(message.from_user.id)
    except:
        return bot.sendMessage(chat_id=message.chat_id,text='You do not appear to be in the database. Please register with /register')
    matches = df.findMatches(dota_id)
    if not matches:
        logging.error('No results from match requests. WebAPI servers down?')
        return sendText(bot,message.chat_id,'Request failed. Steam webAPI servers may be down')
    match_ids = ['#m_' + str(d['match_id']) for d in matches]
    keyboard = [match_ids[:3],match_ids[4:7]]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard,one_time_keyboard=True)
    bot.sendMessage(chat_id=message.chat_id, text="Choose match:", reply_markup=reply_markup)

# Request, format and send dota last match info
def last_match(bot, message, match_id=None):
    reply_markup = telegram.ReplyKeyboardHide()
    bot.sendMessage(chat_id=message.chat_id,text=msgs['getmatch'],reply_markup=reply_markup)
#    sendText(bot,message.chat_id,msgs['getmatch'])

    if not match_id:
        try:
            dota_id = df.get_dota_id_from_telegram(message.from_user.id)
        except:
            logging.info('last match info requested by non-registered user,',message.user)
            return bot.sendMessage(chat_id=message.chat_id,text='You don\'t appear to be in the database. Please register using the /register command')
        match_id = df.getLastMatch(dota_id)
        logging.info('Last match request:',dota_id,message.from_user.first_name,dota_id,message.from_user.id)

    bot.sendMessage(chat_id=message.chat_id,
        text="[Requested DotaBuff page for match "
        +str(match_id)+"](http://dotabuff.com/matches/"+str(match_id)+").",
        parse_mode=telegram.ParseMode.MARKDOWN)

#Request, format and send dota feeding info.
def feeding(bot,message,BASE_URL,update=False):
    sendText(bot,message.chat_id,msgs['getfeed'])

    with dataset.connect() as db:
        db['feeds'].delete()
    table = msgs['feedtable']

    #refreshed data from dota api
    if (update):
        logging.info('feed data update requested')
        sendText(bot,message.chat_id,msgs['serverpoll'])
        feeds = df.valRank('deaths')
        pickle.dump(feeds,open('database/feeds.p','wb'))
        logging.info('new feeds file saved')

    #displays cached data
    else:
        try:
            feeds = pickle.load(open('database/feeds.p','rb'))
        #will update automatically if local cache not found
        except Exception as e:
            logging.error(e)
            sendText(bot,message.chat_id,'Local feed data not found...')
            sendText(bot,message.chat_id,msgs['serverpoll'])
            feeds = valRank('deaths')
            logging.info('feeding data defaulted to:', feeds)
            pickle.dump(feeds,open('database/feeds.p','wb'))

    i=0; #rank iterator
    for rank in feeds:
        i+=1
        table+=str(i)+"....."+str(rank['dota_name'])+"...."+str(rank['total_vals'])+"\n"
    sendText(bot,message.chat_id,table)

    footer = "Congratulations to "+str(feeds[0]['dota_name'])+"! \nCheck out the match where he fed the most ("+str(feeds[0]['top_vals'])+" times!)"

    sendText(bot,message.chat_id,footer)

    bot.sendMessage(chat_id=message.chat_id,
            text="["+str(feeds[0]['dota_name'])+"'s DotaBuff Match](http://dotabuff.com/matches/"+str(feeds[0]['top_match'])+").",
            parse_mode=telegram.ParseMode.MARKDOWN)

    #graphing test
    fig = plt.figure()
    ax = fig.add_subplot(111)
    feed_values = feeds[0]['val_list']
    match_ids = feeds[0]['match_list']
    N= len(feed_values)
    ind = np.arange(N)
    width =0.8
    bars = ax.bar(ind, feed_values, width)
    ax.set_xlim(-width,len(ind)+width)
    ax.set_ylim(0,max(feed_values)+2)
    ax.set_ylabel('deaths per game')
    ax.set_title(feeds[0]['dota_name']+'\'s graph of shame')
    ax.set_xticks(ind+width)
    ax.set_xlabel('games')
    xtickNames = ax.set_xticklabels(match_ids)
    plt.setp(xtickNames, rotation=90, fontsize=6)
    imgPath = 'img/feed.png'
    plt.savefig(imgPath)#,facecolor='#bcc5d4')
    postImage(imgPath,message.chat_id,BASE_URL)

    with dataset.connect() as db:
        db['feeds'].insert(dict(name = feeds[0]['dota_name'], av_feeds = feeds[0]['total_vals']/len(feeds[0]['val_list'])))

#Wrapper for telegram.bot.sendMessage() function. Markdown enabled
def sendText(bot,chat_id,text,webprevoff=False):

    try:
        bot.sendMessage(chat_id=chat_id,text=text,parse_mode="Markdown",disable_web_page_preview=webprevoff)
    except:
        bot.sendMessage(chat_id=chat_id,text=text,disable_web_page_preview=webprevoff)

#Searches for commands sent to bot
def command(cmd,text):
    if re.match(cmd, text, flags=re.IGNORECASE):
        return True
    else:
        return False

#Searches for keywords sent to bot
def keywords(words,text):
    # import pdb; pdb.set_trace()
    if any(word in text for word  in words):
        return True
    else:
        return False

#http POST request
def postImage(imagePath,chat_id,REQUEST_URL):
#    pdb.set_trace()
    data = {'chat_id': chat_id}
    try:
        files = {'photo': open(imagePath,'rb')}
    except:
        return logging.error('could not send local photo',sys.exc_info()[0])
    return requests.post(REQUEST_URL + '/sendPhoto', params=data, files=files)

#thank user
def thank(bot, chat_id, message):

    sendText(
            bot,chat_id,
            ' '.join([msgs['thanks'],str(message.from_user.first_name)]))

#greet user
def greet(bot,chat_id,message):
    sendText(
            bot,chat_id,
            ''.join([msgs['welcome1'],
                str(message.from_user.id),
                msgs['welcome2'],
                message.from_user.first_name]))

#say goodbye to users
def goodbye(bot,chat_id,message):
    sendText(bot,chat_id,"Daisy...daisy...")

#echo user message to given chat id
def echocats(bot,message):
    echo = message.text.split('/echo',1)[1]
    chat = yaml.load(open('database/echochat.yaml','rb'))
    try:
        sendText(bot,chat,echo)
    except:
        return logging.error('failed to echo message',message,echo,chat)

#get latest dota news post
def dotaNews(bot,message):

    payload={
            'appid':'570',  #dteam appid for dota2
            'count':'1',    #latest news post only
            'maxlength':'300' #maximum length of news summary for bot message
            }
    try:
        news = df.steamNews(payload)[0]
    except:
        sendText(bot,message.chat_id,'Request failed. Servers may be down')
        return logging.error('Failed to get steam news item')

    logging.info(news)

    if not news:
        logging.error('No news items found in steam api request')
        return sendText(bot,message.chat_id,msgs['nonews'])

    header = '*Latest Dota 2 news post* ('+news['feedlabel']+')'

    try:
        return sendText(bot,message.chat_id,newsReply(header,news),True)
    except:
        logging.error('Couldn\'t parse: ',news)

#format news message for bot message
def newsReply(header,news):
    title = '\n*'+news['title']+'*'
    contents = news['contents']
    url = news['url']
    texts = [
            header,
            title,
            contents,
            '\nSee the rest of this post here:',
            url]
    reply = '\n'.join(texts)
    return reply

#post new dota 2 patch
def postUpdate(bot,message):
    patch = df.getNewPatch()
    if patch:
        date = datetime.datetime.fromtimestamp(
            patch['date']
            ).strftime('%Y-%m-%d %H:%M')

        header = '*NEW DOTA 2 PATCH!*'+date+''
        try:
            #using sendMessage as markdown can cause problems
            sendText(bot,message.chat_id,newsReply(header,patch),True)
        except:
            logging.error('Couldn\'t parse: ',patch)

        #update list of potentially unpatched players from the database
        with dataset.connect() as db:
            db_size = len(db['users'])
            for i in range (1,db_size+1):
                db['user'].update(dict(id=i,unpatched=True),['id'])

#checks if something has expired, e.g a dota event or the time between dota 2 update checking
def expiry(initial_time,dtime): #dtime in minutes
    if datetime.datetime.now() > initial_time+datetime.timedelta(minutes=dtime):
        return True

def msgTag(bot, message, name):
    user_name = message.from_user.first_name
    tagged_msg = {
            'time':         datetime.datetime.now(),
            'chat_id':      message.chat_id,
            'name':         name.lower(),
            'sender':       user_name,
            'sender_id':    message.from_user.id,
            'text':         message.text
            }
    sendText(bot,message.chat_id,'Ok '+user_name.lower()+msgs['tag_saved']+name+'.')
    return tagged_msg

def tagReply(bot,message,tag):
    user_name = message.from_user.first_name
    sendText(bot,message.chat_id,user_name+msgs['tag_reply'])
    sendText(bot,message.chat_id,'from: '+tag['sender']+' at '+tag['time'].strftime('%m-%d %H:%M')+'\n\n'+tag['text'])

def delDotaTable():
    with dataset.connect() as db:
        try:
            db['dota_evt'].delete()
        except:
            logging.info('no dota table to delete in database')
