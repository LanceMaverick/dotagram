import telegram
import dataset
import datetime
import beard_functions as bf
import os
token = os.environ.get('TG_BOT_TOKEN')
BASE_URL = 'https://api.telegram.org/bot%s' % token
def checkMotion(bot):
    with dataset.connect() as db:
        motion_log = db['motion']
        detections = motion_log.find(new=True)

        if motion_log.find(new=True,return_count=True)!=0:
            motions = motion_log

            times = []
            new_ids = []
            for detection in detections:
                times.append(detection['mtime'])
                new_ids.append(detection['id'])

            text = "MOTION DETECTED:\n"+'\n'.join(times)
            send_to_user = db['user'].find_one(id=5)['telegram_id']
            bf.sendText(bot,send_to_user,text)
            bf.postImage('img/motion.png',send_to_user,BASE_URL)
            for new_id in new_ids:
                db['motion'].update(dict(id=new_id,new=False),['id'])
                
def clearMotion():
    with dataset.connect() as db:
        db['motion'].delete()

def resetMotion():
        with dataset.connect() as db:
            db_size = len(db['motion'])
            for i in range (1,db_size+1):
                db['motion'].update(dict(id=i,new=False),['id'])

