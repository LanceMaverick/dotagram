import dataset
import sys

admin = sys.argv[1]
tg_id = int(sys.argv[2])

def setuser(admin,tg_id):
    with dataset.connect() as db:
        if not db['user'].find_one(telegram_id=tg_id):
            return 'user '+str(tg_id)+' not found.'
        if admin == 'add':
            db['user'].update(dict(telegram_id = tg_id, admin = 1),['telegram_id'])
            return 'success!'
        elif admin == 'remove':
            db['user'].update(dict(telegram_id = tg_id, admin = None),['telegram_id'])
            return 'success!'
        else:
            return 'Please specify whether to \'add\' or \'remove \' admin as first argument, telegram id as second'

#print setuser(admin,tg_id)
