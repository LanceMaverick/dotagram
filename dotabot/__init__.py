import telegram
import os
import datetime

# from bot/
import sys
sys.path.append(os.getcwd()+'/bot/')
import adapt_functions as af
import beard_functions as bf
import dota_functions as df
import bottools as btools
import msg_texts
import register as reg
import events

from eventbot import EventBot, EventAlreadyPlanned, PersonAlreadyAttending

# From bot.py
stack_queries = ['5 stack','5stack','stacked']
greetings = ['hello','hi','hey']
goodbyes = ['goodbye','bye','laters','cya']
thanks = ['thanks','cheers','nice one']
dota_checked = False
patch_check_time = datetime.datetime.now()
token = os.environ.get('TG_BOT_TOKEN')
BASE_URL = 'https://api.telegram.org/bot%s' % token

#create Mycroft AI Adapt engine
skb_intelligence  = af.skyAdapt()

# This is a bot from a separate library
#
# TODO: eventually phase this out
bot = telegram.Bot(token=os.environ.get('TG_BOT_TOKEN'))

class Namespace(object):
    def __init__(self):
        """An empty class to add members to on the fly"""
        pass

class DotaBot(EventBot):
    def __init__(self, seed_tuple, timeout, db_name="sqlite:///dotabot.db"):
        "docstring"
        super(DotaBot, self).__init__(seed_tuple, timeout, db_name)

    async def on_chat_message(self, msg):
        print(msg)
        # housekeeping
        if bf.expiry(patch_check_time,10):
            bf.postUpdate(bot,message)

        chat_id = msg['chat']['id']
        text = msg['text'] #.encode('utf-8')
        user = msg['from']['username']

        # A little hacking is needed here to make the message object fit the
        # old api
        #
        # TODO phase this out
        message = Namespace()
        message.chat_id = chat_id
        message.text = text
        message.from_user = Namespace()
        message.from_user.first_name = msg['from']['first_name']
        message.from_user.id = msg['from']['id']
        message.user = msg['from']['username']

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
            try:
                await self.create_event(msg)
            except EventAlreadyPlanned:
                event = await self.get_future_event()
                await self.sender.sendMessage(
                    "Event already planned for {}".format(
                        event.start_datetime))
            # dota_checked = False
            # time = events.get_time(bot,message)
            # if (dotes):
            #     dotes.set_time(time)
            #     bf.sendText(bot,chat_id,'Dota time modified')
            #     dotes.time_info(message)
            # else:
            #     shotguns = events.get_str_list(bot,message,'with')
            #     dotes = events.dota(bot,message,time)
            #     logging.info('multi-shotgun:',shotguns)
            #     if shotguns:
            #         for cat in shotguns:
            #             dotes.shotgun(message,cat)

        #shotgun a place in dota
        if bf.command('shotgun!',text):
            # assert False, "Sorry, not implemented yet!"
            event = await self.get_future_event()
            if event:
                try:
                    await self.add_person_to_event(
                        event,
                        {"name": msg["from"]["username"]})
                    await self.sender.sendMessage(
                        "Your interest has been noted.")
                except PersonAlreadyAttending:
                    await self.sender.sendMessage(
                        "Your interest has already been noted.")
            else:
                await self.sender.sendMessage(
                    "I don't know about any Dota happening today.")

        #unshotgun your place in dota
        if bf.command('unshotgun!',text):
            event = await self.get_future_event()
            if event:
                try:
                    await self.remove_person_from_event(
                        event,
                        {"name": msg["from"]["username"]})
                    await self.sender.sendMessage(
                        "Your lack of interest has been noted.")
                except PersonNotAttending:
                    await self.sender.sendMessage(
                        "You were never going to this event.")
            else:
                await self.sender.sendMessage(
                    "I don't know about any Dota happening today.")

        # TODO
        #ready up for dota
        if bf.command('unready!',text):
            assert False, "Sorry, not implemented yet!"
            # if (dotes):
            #     dotes.unshotgun(message,'rdry')
            # else:
            #     events.nodota(bot,message)

        #un-ready up for dota
        if bf.command('ready!',text):
            assert False, "Sorry, not implemented yet!"
            # if (dotes):
            #     dotes.rdry_up(message)
            # else:
            #     events.nodota(bot,message)


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
        if bf.keywords(stack_queries, text.lower()):
            # assert False, "Sorry, not implemented!"
            event = await self.get_future_event()
            if event:
                await self.sender.sendMessage(
                    "There are currently {} people shotgunned.".format(
                        len(event.people_attending)))
            else:
                await self.sender.sendMessage("I don't know about any dota happening today.")

        #AI tests
        intents = af.intentChecker(skb_intelligence, 0.3, text)
        try:
            for intent in intents:
                if intent['intent_type'] == 'DotaIntent':
                    future_event = await self.get_future_event()
                    if future_event:
                        await self.sender.sendMessage("Yes, dota is happening.")
                        await self.sender.sendMessage(str(future_event.start_datetime))
                        await self.sender.sendMessage(
                            "Attending:\n"+\
                            "\n".join((x['name'] for x in future_event.people_attending)))
                    else:
                        await self.sender.sendMessage("I don't know about any dota happening today")
                    # events.dotaQuery(bot, message, dotes)
                elif intent['intent_type'] == 'NewDotaIntent':
                    try:
                        await self.create_event(msg)
                    except EventAlreadyPlanned:
                        future_event = await self.get_future_event()
                        await self.sender.sendMessage(
                            "Event already planned for {}.".format(future_event.start_datetime))
        #             dota_checked = False
        #             time = events.get_time(bot,message)
        #             if (dotes):
        #                 dotes.set_time(time)
        #                 bf.sendText(bot,chat_id,'Dota time modified')
        #                 dotes.time_info(message)
        #             else:
        #                 shotguns = events.get_str_list(bot,message,'with')
        #                 dotes = events.dota(bot,message,time)
        #                 logging.info('multi-shotgun:',shotguns)
        #                 if shotguns:
        #                     for cat in shotguns:
        #                         dotes.shotgun(message,cat)
                elif intent['intent_type'] == 'StackIntent':
                    future_event = await self.get_future_event()
                    if future_event and len(future_event.people_attending) >= 5:
                        await self.sender.sendMessage("Stacked!")
                        await self.sender.sendMessage(str(future_event.start_datetime))
                        await self.sender.sendMessage(
                            "Attending:\n"+\
                            "\n".join((x['name'] for x in future_event.people_attending)))
                    elif future_event:
                        await self.sender.sendMessage("Not stacked yet")
                        await self.sender.sendMessage(str(future_event.start_datetime))
                        await self.sender.sendMessage(
                            "Attending:\n"+\
                            "\n".join((x['name'] for x in future_event.people_attending)))
                    else:
                        await self.sender.sendMessage("No event planned.")

        #             if (dotes):
        #                 dotes.stack(message)
        #             else:
        #                 events.nodota(bot,message)
        except:
            print('no intents detected')

        # TODO: figure out what this does and convert it
        # pending_tag = btools.keySearch(tags,'name',user.first_name.lower())
        # if pending_tag and pending_tag['chat_id']==chat_id:
        #     bf.tagReply(bot,message,pending_tag)
        #     i = next(index for (index, entry) in enumerate(tags) if entry['name'] == pending_tag['name'])
        #     tags.pop(i)

        # tag_match = re.search(r'\/tag\s*(\w+)',text)
        # if tag_match:
        #     tags.append(bf.msgTag(bot,message,tag_match.group(1)))
        # #  print(tags)
