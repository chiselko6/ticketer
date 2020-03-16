import os
from redis import Redis
from rq import Queue


queue = Queue(connection=Redis(host=os.environ['REDIS__HOST'],
                               username=os.environ['REDIS__USER'],
                               port=os.environ['REDIS__PORT'],
                               password=os.environ['REDIS__PASSWORD'],
                               ))
