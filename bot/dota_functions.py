#Functions for interfacting with DOTA 2 API. Uses the thin wrapper Dota2py by Andrew Snowden for requests
#This is very quick and dirty 5am code do test requesting from DOTA 2 API. 
from dota2py import api
import sys
from os.path import abspath, join, dirname
import os
from datetime import date, timedelta
import requests
import register as reg
import bottools as btools
import yaml
import dataset
import logging
#logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',stream=sys.stdout, level=logging.INFO)
#Spacecats dictionary for steam id and name lookup.
#All functions currently use first_name value from telegram message.
#All functions are agnostic of which identifier is used. message.from_user.id is safer,
#will implement method to register user with telegram id and ue config file instead of dict.

#get news posts from steam api
def steamNews(payload):
    
    steam_url = 'http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/'
    try:
        response = requests.get(steam_url,params=payload)
        news = response.json()['appnews']
        return news['newsitems']
    except:
        logging.error('no news items found')
        return None

#check for new dota 2 patch from steam api
def getNewPatch():
    
    last_update = yaml.load(open('catabase/d2_patch_id.yaml','rb'))
    
    payload={
            'appid':'570',
            'count':'20',
            'maxlength':'300'
            }
    news = steamNews(payload)
    if not news:
        return logging.error('No results or http code returned from steam news. Servers down?')
    patch = btools.keySearch(news,'feedname','steam_updates')

    if patch:
        patch_id = patch['gid']
    else:
        return None
    if patch_id == last_update:
        return None
    else:
        logging.info('new patch data found:',patch)
        yaml.dump(patch_id,open('catabase/d2_patch_id.yaml','wb'))
        return patch

#returns last 25 matches for given user
def findMatches(account_id):                                  
    try:
        return api.get_match_history(account_id=account_id)["result"]["matches"]
    except:
        logging.error('no match history data found')
        return logging.error('no match history found')

#returns value for given key in results such as list of players, starttime etc
#abstraction from api requests for simplicity, but currently experimenting with
#using json  
def getResults(match,key):
    
    result = match['result']
    vals_list = result[key]
    return vals_list

#Takes list of players from match and returns the value of an attribute
#for a given player, e.g deaths, hero healing, tower damage etc
def getPlayerVal(vals_list,account_id,val):

    for d in vals_list:
        if d['account_id'] == account_id:
            return d[val]

#returns a zipped list of match_id's with a given player's attribute for each
#of the player's last 25 matches
def getSum(account_id,days,attribute):
    
    matches = findMatches(account_id)
    match_ids = []
    attr_list = []
    
    for i in range (0,25):
        if matches[i].has_key("match_id"):
            try:
                match = api.get_match_details(matches[i]["match_id"])
                match_ids.append(matches[i]['match_id'])
                results = getResults(match,'players')
                attr_list.append(getPlayerVal(results,account_id,attribute))
            except requests.exceptions.HTTPError as e:
                logging.error("request error:",str(e))

    return zip(match_ids,attr_list)    

#To link telegram user with dota profile.
def get_dota_id_from_telegram(user_id):
    with dataset.connect() as db:
        catmatch = db['user'].find_one(telegram_id=user_id)
        return catmatch['dota_id']

#Returns the last match of a given player 
def getLastMatch(dota_id):
    matches = findMatches(dota_id)
    match_id = (matches[0]["match_id"])
    return match_id

#Returns ranked dict based on player value.
def valRank(val):
    db = dataset.connect()
    spacecats = db['user'].all()
    results = []
    for spacecat in  spacecats:
        name = spacecat['dota_name']
        account_id = spacecat['dota_id']
        vals = getSum(account_id,7,val)
        val_lists = zip(*vals)
        top_index =val_lists[1].index(max(val_lists[1]))
        top_vals = val_lists[1][top_index]
        top_match = val_lists[0][top_index]
       
        total_vals=sum(val_lists[1])
        
        result = {
                'dota_name':name,
                'dota_id':account_id,
                'total_vals':total_vals,
                'top_match':top_match,
                'top_vals':top_vals,
                'val_list':val_lists[1],
                'match_list':val_lists[0]
                }
        results.append(result)
    
    ranked = sorted(results, key=lambda k: k['total_vals'],reverse=True) 
    return ranked

