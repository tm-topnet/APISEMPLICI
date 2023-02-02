import redis
import numpy as np
import pickle


r = redis.Redis(host='localhost', port=6379, db=0)
ps = r.pubsub()
ps.psubscribe('peopledetected_*')
ii = 0
while True:
    try:
        msg = ps.get_message()
        #print(msg)
        if msg:
            if msg['type'] == 'pmessage':
                new_img = pickle.loads(msg['data'])
            #print('New Image', ii)
                print(new_img.shape, ii)
                ii += 1
    except KeyboardInterrupt:
        break