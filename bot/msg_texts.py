# help message info
def help():

    msg = '''

With the powers invested in me by Lord Gaben, I respond to the following commands and actions:

*Commands:*

*THE DATABASE*
*/register <dota first name>, <dota last name>, <dotabuff player page>*"
*/database* - Displays the current entries in the database 
*/delete user <index>* - Deletes the database entry for the given index.

*DOTA EVENTS*
*dota at* - creates a new dota event or modifies an existing event's time:
    "*/dota at 18:45*"
    "*/dota at 18.45*"
    "*/dota at 1845*"
    "*/dota at 18:45 with alice, bob*" (will shotgun alice and bob)
    "*/dota*"

*/delete dota* - will remove the current dota event
*shotgun!* - shotgun for dota
*unshotgun!* - Remove yourself from the shotgun (and ready) list.
*ready!* - ready up
*unready!* - Remove yourself from the readys

*DOTA 2/STEAM API REQUESTS*
*/topfeeds* - See who died the most recently. Add the 'update' argument to refresh the list
*/lastmatch* - Post your last match details
*/news* - latest dota 2 news post

If a message is asking if or when dota is happening, or if there is a 5 stack, the bot will answer

        '''
    return msg

def readme():
    msg = '''

For a more comprehensive guide on how to use the bot, please see the readme section 'How to use':
https://github.com/LanceMaverick/skybeard_bot/blob/master/README.md#how-to-use
        '''
    return msg

# dict of strings for bot messages. Nice than concatenation in functions but still could be better
msgs ={ 
        #skybeard messages
        'welcome1':     'Hello user No. ',
        'welcome2':     ', human name ',
        'thanks':       'You\'re welcome', 
        'reg_help':     '''To register, please format your request comma separated like so:\n"/register <dota first name>, <dota second name (if there is one otherwise leave blank space between commas>, <dotabuff page>\ne.g\n"/register Scrub, Lord, http://www.dotabuff.com/players/123456768" ''',
        'reg_check':    'There seems to already be an entry in the database under your account. Please check it and delete your entry if you wish to re-register. see /help for details on how to do this.',
        #dota2 api requests
        'getmatch':     '*RETRIEVING MATCH*',
        'getfeed':      '*RETRIEVING FEEDING DATA*\nOne moment please.',
        'serverpoll':   'Contacting Steam servers. This may take a while...\n',
        'feedtable':    '*TOP FEEDERS OF THE WEEK* (25 Matches)\n\nRANK....NAME....DEATHS\n',
        #steam api requests
        'nonews':       'Sorry, I couldn\'t find any data',
        
        #dota event messages
        'w'     :       'with',
        't_error':       'I didn\'t understand the time you specified and defaulted to 19:30. Did you format it correctly?',
        'notime':       'No Time specified. Defaulting to 19:30',
        'nodota':       'I don\'t know about any dota happening today',
        'makedota':     'Dota event created for',
        'shotgun':      'you have shotgunned for Dota at',
        'overstack':    'Oh dear, too many people have shotgunned. It must be resolved with a fight to the death. \nShotguns are: \n',
        'patch_warn':    'fyi: new dota patch to download',
        
        #misc
        'tag_saved':    ', I will pass on the message the next time I see ',
        'tag_reply':    ', someone wanted you to see the following message:'
        }
