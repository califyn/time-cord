from concurrent.futures import ThreadPoolExecutor
import threading
import time
from monitor import Monitor
from tendo import singleton
import os
from loguru import logger
logger.add("records.log", retention="10 days")  # Cleanup after some time

def rec_write2(line, path="records.log"): # TODO: quicker file reading/writing
    logger.info(line)

me = singleton.SingleInstance() # make sure no other instances are running

mon = Monitor(debug=True)

parpath = os.path.realpath(__file__)
path_split = parpath.split("/")
path_split[-1] = ""
parpath = "/".join(path_split)

interval = 30
# every N seconds, execute something


def record():
    try:
        line = str(time.time())
        chnl = mon.channel_name()
        line = line + "," + str(chnl)
        if chnl != None:
            line = line + "," + mon.server_name()
        else:
            line = line + ",None"
        line = line + "\n"
        rec_write(line)
    except Exception as e:
        print(e)

# # TODO: make sure not too many threads are running at once (interval too low)
# # TODO: replace commas
# sleep_time = 0
# while not time.sleep(sleep_time):
#     record()
#     sleep_time = interval - (time.time() % interval)
