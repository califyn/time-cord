from concurrent.futures import ThreadPoolExecutor
import threading
import time
from monitor import Monitor
from tendo import singleton

me = singleton.SingleInstance() # make sure no other instances are running

#mon = Monitor(debug=True) # load it once
interval = 30
# every N seconds, execute something

def rec_write(line, path="records.log"): # TODO: quicker file reading/writing
    lines = []
    try:
        with open(path, "r") as file:
            lines = file.readlines()
            ind = 0
            for i in range(0,len(lines)):
                if lines[i].split(",")[0] > line.split(",")[0]:
                    break
                else:
                    ind = i + 1
            lines.insert(ind, line)
        with open(path, "w") as file:
            for l in lines:
                file.write(l)
    except Exception as e:
        print(e)

def thread_func():
    try:
        line = str(time.time()) + ",hello!" # Fake task for now
        line = line+"\n"
        rec_write(line)
    except Exception as e:
        print(e)

# TODO: make sure not too many threads are running at once (interval too low)

with ThreadPoolExecutor(max_workers=3) as executor:
    sleep_time = 0
    while not time.sleep(sleep_time):
        task = executor.submit(thread_func)
        sleep_time = interval - (time.time() % interval)
