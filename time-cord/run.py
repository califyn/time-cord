from concurrent.futures import ThreadPoolExecutor
import threading
import time
from monitor import Monitor
from tendo import singleton
import os

me = singleton.SingleInstance() # make sure no other instances are running

mon = Monitor(debug=True)

parpath = os.path.realpath(__file__)
path_split = parpath.split("/")
path_split[-1] = ""
parpath = "/".join(path_split)

interval = 30
# every N seconds, execute something

def rec_write(line, path="records.log"): # TODO: quicker file reading/writing
    lines = []
    try:
        with open(parpath + path, "r") as file:
            lines = file.readlines()
            ind = 0
            for i in range(0,len(lines)):
                if lines[i].split(",")[0] > line.split(",")[0]:
                    break
                else:
                    ind = i + 1
            lines.insert(ind, line)
        with open(parpath + path, "w") as file:
            for l in lines:
                file.write(l)
    except Exception as e:
        print(e)

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

# TODO: make sure not too many threads are running at once (interval too low)
# TODO: replace commas
sleep_time = 0
while not time.sleep(sleep_time):
    record()
    sleep_time = interval - (time.time() % interval)
