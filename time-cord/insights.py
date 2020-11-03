# Total time spent in the last day, week,  etc

# Time spent on specific channels ^^
# Time spent on specific servers ^^

# Length of consecutive periods spent on Discord/specific server/specific channel

# What you tend to access at certain times of day

import time, os
from datetime import datetime
import tzlocal

class AddLog:
    """
    Class to provide an easy way to update counts of time spent on channels,
    servers, etc.  Logs are stored in format (name, value).  Increments value
    by name.
    """
    dict = {}

    def __init__(self):
        """
        Initiates the class.
        """
        self.dict = {}

    def increment(self, name, val):
        """
        Increment the object associated with name by val, or set it to val if it
        doesn't currently exist.

        Input:
            name: name of the object to be incremented.
            val: value to increment by.
        """
        ind = -1
        if name in self.dict:
            self.dict[name] = self.dict[name] + val
        else:
            self.dict[name] = val

    def give(self):
        """
        Return the logged dictionary.

        Output:
            dict: the dictionary.
        """
        return self.dict

class TCInsights:
    """
    Class to provide insights into logged Discord data.

    All data is taken from the moment the class is initialized (so it does not
    update with new data once it has been initialized.)
    """
    logs = []
    offset = 0
    runtime = 0
    path = ""

    def __init__(self):
        """
        Initializes the TCInsights class.
        """
        self.runtime = time.time()

        path = os.path.realpath(__file__)
        path_split = path.split("/")
        path_split[-1] = ""
        path = "/".join(path_split)
        self.path = path

        self.offset = -1 * time.timezone

        with open(self.path + "records.log", "r") as file:
            lines = file.readlines()
            for l in range(0, len(lines) - 1):
                split = lines[l].split(",")
                moment = float(split[0])
                chnl = split[1]
                serv = split[2][:-1]
                next = float(lines[l + 1].split(",")[0])
                if next - moment > 300:
                    next = moment + 300
                self.logs.append([moment, next - moment, chnl, serv])

    def human_time(self, logtime):
        """
        Converts seconds since epoch to a human-readable time format.

        Code taken from: jfs's answer on
        https://stackoverflow.com/questions/3682748/converting-unix-timestamp-string-to-readable-date/40769643#40769643

        Input:
            logtime: time in seconds, since epoch.

        Output:
            str: a human readable format of the time.
        """

        local_timezone = tzlocal.get_localzone() # get pytz timezone
        local_time = datetime.fromtimestamp(logtime, local_timezone)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")


    def sprawl_data(self, scope=-1, lvl="discord"):
        """
        Gives a breakdown of time data in the last scope seconds.  Should only be
        used internally.  Not nice to humans.

        Inputs:
            scope: the number of seconds to look back in time.  If -1, the
                current day.
            lvl: how fine-grained the data should be.  There are three accepted values:
                discord: over the entire system. ("0" works also.)
                server: separate data by server. ("1" works also.)
                channel: separate data by channel. ("2" works also.)

        Outputs:
            list of lists: each sub-list is of the form (name, time spent.).
        """
        out = AddLog()
        if scope == -1:
            scope = (time.time() + self.offset) % 86400
        if lvl == 0:
            lvl = "discord"
        elif lvl == 1:
            lvl = "server"
        elif lvl == 2:
            lvl = "channel"
        elif lvl not in [0, 1, 2, "discord", "server", "channel"]:
            raise Exception("Bad input for lvl")

        limit = self.runtime - scope
        logs = [x for x in self.logs if x[0] >= limit]

        for log in logs:
            if lvl == "discord":
                if log[3] != "None":
                    out.increment("discord", log[1])
            if lvl == "server":
                if log[3] != "None":
                    out.increment(log[3], log[1])
            if lvl == "channel":
                if log[3] != "None":
                    out.increment(log[2] + "," + log[3], log[1])
        return out.give()

    def detail_data(self, obj, lvl, scope="-1", fuzz=1):
        """
        Gives a detailed breakdown of time spent on the specified object, whether
        it be a channel, server, or the entirety of Discord.  Specifies which times
        and how long the object was open.  Use internally.  Not nice to humans.

        Input:
            obj: the object to track.  If tracking all of Discord it can be
                anything.  If channel, should be in format "channel,server".
            scope: amount of time, in seconds, to go backwards.  If -1, track
                only today.
            lvl: whether the object is a channel, server, or all of Discord.
                Three accepted values:
                discord: entire system. ("0" works also.)
                server: a server. ("1" works also.)
                channel: a channel. ("2" works also.)
            fuzz: the amount of "fuzz" or time spent somewhere else that can be
                counted within a single "consecutive" block of time.

        Output:
            list of lists: breakdown of time spent on the object, in the format
                (beginning, end) for each interval of time spent there.
        """
        if scope == -1:
            scope = (time.time() + self.offset) % 86400
        if lvl == 0:
            lvl = "discord"
        elif lvl == 1:
            lvl = "server"
        elif lvl == 2:
            lvl = "channel"
        elif lvl not in [0, 1, 2, "discord", "server", "channel"]:
            raise Exception("Bad input for lvl")

        limit = self.runtime - scope
        logs = [x for x in self.logs if x[0] >= limit]

        intervals = []
        for log in logs:
            match = False
            if lvl == "discord":
                if log[3] != "None":
                    match = True
            if lvl == "server":
                if log[3] == obj:
                    match = True
            if lvl == "channel":
                if log[2] + "," + log[3] == obj:
                    match = True
            if match == True:
                intervals.append([log[0], log[0] + log[1]])

        i = 0
        while i < len(intervals) - 1:
            if (intervals[i + 1][0] - intervals[i][1]) < fuzz:
                intervals[i][1] = intervals[i + 1][1]
                del intervals[i + 1]
                i = i - 1
            i = i + 1
            
        return intervals
