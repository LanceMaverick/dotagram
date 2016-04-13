import telegram
import yaml
import dataset
import pickle
import shutil
import beard_functions as bf
from msg_texts import * 
import logging

def regCats(bot,message):
    
    text = message.text
    user = message.from_user
    tg_id = user.id
    tg_fname = user.first_name
    tg_sname = user.last_name
    
    with dataset.connect() as db: # database URL is set as environment variable in bot_setup shell script.
        users = db['user'] # table of users
        catmatch = users.find_one(telegram_id=tg_id) # does the user already exist?
       
        # only allows users to add new entry and not modify their existing one (must delete it first) 
        if catmatch:
            bf.sendText(bot,message.chat_id,msgs['reg_check'],True)
            return
        else:
            details = text.split('/register',1)[1] # get registration parameters from message
            
            try:
                details_list = [element.strip() for element in details.split(',')] # put parameters into list
                dota_fname = details_list[0]
                dota_sname = details_list[1]
                dota_id = int(details_list[2].split('/players/',1)[1]) # get dota ID from dotabuff url
                dota_name = ' '.join([dota_fname,dota_sname])
            
            except:
                bf.sendText(bot,message.chat_id,msgs['reg_help'],True) # formatting error
                return

            # insert entry into user table 
            db['user'].insert(dict(
                dota_name=    dota_name,
                dota_id=      dota_id,
                first_name=   tg_fname,
                last_name=    tg_sname,
                telegram_id=  tg_id
            ))
            
            return bf.sendText(bot,message.chat_id,'New member added to the database!')

# freeze the database as a yaml file (also supports json. Useful to expose database to other applications 
def saveCats(cats):
    with dataset.connect() as db:
        cats = db['user'].all()
        datset.freeze(cats, format='yaml', filename='catabase_freeze.yaml')

# remove entry from the database given an index e.g /delete cat 3
def deleteCat(bot,message):
   
    
    try:  # get index from message and validate input
        index = int(message.text.split('cat',1)[1].strip())
    except:
        return bf.sendText(bot,message.chat_id,'Couldn\'t parse index')
    
    with dataset.connect() as db:
        cat = db['user'].find_one(id=index)

        if not cat: # check entry exists
            return bf.sendText(bot,message.chat_id,'index not found')

        # check user as permission to do this
        if(permission(message,cat)):
            db['user'].delete(id=index)
        else:
            return bf.sendText(bot,message.chat_id,message.from_user.first_name+', you do not have permission to delete this entry')

    return bf.sendText(bot,message.chat_id,'Entry number '+str(index)+' removed.\nNew catabase saved.')

#Checks user has permission to access entry (only their own entry unless admin)
def permission(message,db_entry):

    user_id = message.from_user.id
    
    if (db_entry['telegram_id']==user_id) or is_user_admin(message):
        return True
    else:
        return False

#checks if the user has admin privelages 
def is_user_admin(message):
    user_id = message.from_user.id
    
    with dataset.connect() as db:
        if db['user'].find_one(telegram_id=user_id,admin=1):
            return True
        else:
            return False

# prints accessible database entries into the chat 
def printCats(bot,message):
    
    db = dataset.connect()
    users = db['user'].all()
    db_size = len(db['user'])
    bf.sendText(bot,message.chat_id,'There are '+str(db_size)+' database entries:')
    entry_found = False

    for cat in users:
        if permission(message,cat):
            entry_found = True
            catdict = dict(cat)
            catdict.pop('name', None)
            catdict.pop('admin', None)
            catdict.pop('unpatched', None)
            vals = [str(i) for i in catdict.values()]
            bf.sendText(bot,message.chat_id,', '.join(vals))
    if not entry_found:
            bf.sendText(bot,message.chat_id,'It appears as though you do not have permission to view any entries.')

