import redis
import numpy as np
import pickle
import cv2
import time

r = redis.Redis(host='localhost', port=6379, db=0)
#ps = r.pubsub()
#ps.subscribe('img')

while True:
    try:
        data = cv2.imread('/home/giovanni/Downloads/faces5.png')
        r.publish('peopledetected', pickle.dumps(data))
        time.sleep(0.1)
        print('Msg sent')
    except KeyboardInterrupt:
        break