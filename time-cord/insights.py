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

    def update(self):
        """
        Updates TCInsights with new logging data, and moves the time marker forward.
        """

        self.runtime = time.time()

        path = os.path.realpath(__file__)
        path_split = path.split("/")
        path_split[-1] = ""
        path = "/".join(path_split)
        self.path = path

        self.offset = -1 * time.timezone

        self.logs = []
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

    def human_interval(self, interval):
        """
        Converts seconds into a human-readable interval.  For example, 3600 seconds => 1h.

        Input:
            interval: the interval to be converted

        Output:
            str: interval in human-readable format (xhymzs).
        """
        if interval < 60:
            return str(int(interval) % 60) + "s"
        elif interval < 3600:
            return str(int(interval//60) % 60) + "m" + str(int(interval) % 60) + "s"
        else:
            return str(int(interval//3600)) + "h" + str(int(interval//60) % 60) + "m" + str(int(interval) % 60) + "s"

    def phrase_to_sec(self, phrase):
        """
        Converts a time phrase ("past day", "past 24 hr", etc.) into a number of seconds to be calculated.

        --How does conversion work?--

        A number of patterns are recognized and checked for.

        Pattern 1: explicit number of seconds, ex. "3600"
            ==> return exactly what is given.

        Pattern 2: this hour
            ==> since the beginning of the hour.

        Pattern 3: today
            ==> since last midnight.

        Pattern 4: this week
            ==> since the beginning of the week, midnight on Monday.

        Pattern 5: last [n] hours
            ==> last n hours.

        Pattern 6: last [n] days
            ==> last n days.

        Pattern 7: last [n] weeks
            ==> last n weeks.

        Input:
            phrase: The phrase to parse.

        Output:
            int: Number of seconds.
        """

        # See if the phrase is already just a number.
        try:
            return int(phrase)
        except ValueError:
            f = 1 # a line which means nothing

        if type(phrase) != str:
            raise Exception("phrase given to time phrase parser not a string or number")

        phrase = phrase.lower()

        now = self.runtime + self.offset

        if phrase == "this hour":
            return now % 3600
        elif phrase == "today":
            return now % 86400
        elif phrase == "this week":
            return now % (86400 * 7)

        phrase = phrase.split(" ")
        if phrase[0] != "last":
            raise Exception("phrase given to time phrase parser not acceptable")
        elif phrase[2] not in ["hours", "days", "weeks"]:
            raise Exception("phrase given to time phrase parser not acceptable")

        num = -1
        try:
            num = float(phrase[1])
        except ValueError:
            raise Exception("phrase given to time phrase parser not acceptable")

        if phrase[2] == "hours":
            return int(num * 3600)
        elif phrase[2] == "days":
            return int(num * 86400)
        elif phrase[2] == "weeks":
            return int(num * 86400 * 7)

    def sprawl_data(self, scope=-1, lvl="discord", nice=True):
        """
        Gives a breakdown of time data in the last scope seconds.

        Inputs:
            scope: the number of seconds to look back in time.  If -1, the
                current day.
            lvl: how fine-grained the data should be.  There are three accepted values:
                discord: over the entire system. ("0" works also.)
                server: separate data by server. ("1" works also.)
                channel: separate data by channel. ("2" works also.)
            nice: make times human-readable.

        Outputs:
            list of lists: each sub-list is of the form (name, time spent.).
        """
        out = AddLog()
        if scope == -1:
            scope = (self.runtime + self.offset) % 86400
        else:
            scope = self.phrase_to_sec(scope)
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
        if not nice:
            return {k: v for k, v in sorted(out.give().items(), key=lambda item: -1*item[1])}
        else:
            return {k: self.human_interval(v) for k, v in sorted(out.give().items(), key=lambda item: -1*item[1])}

    def detail_data(self, obj, lvl, scope=-1, fuzz=1, nice=True):
        """
        Gives a detailed breakdown of time spent on the specified object, whether
        it be a channel, server, or the entirety of Discord.  Specifies which times
        and how long the object was open.

        Input:
            obj: the object to track.  If tracking all of Discord it can be
                anything.  If channel, should be in format "channel,server".
            lvl: whether the object is a channel, server, or all of Discord.
                Three accepted values:
                discord: entire system. ("0" works also.)
                server: a server. ("1" works also.)
                channel: a channel. ("2" works also.)
            scope: amount of time, in seconds, to go backwards.  If -1, track
                only today.
            fuzz: the amount of "fuzz" or time spent somewhere else that can be
                counted within a single "consecutive" block of time or minimal
                interval length that will be counted.
            nice: make times human-readable.

        Output:
            list of lists: breakdown of time spent on the object, in the format
                (beginning, end) for each interval of time spent there.
        """
        if scope == -1:
            scope = (self.runtime + self.offset) % 86400
        else:
            scope = self.phrase_to_sec(scope)
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
                if intervals[i][1] - intervals[i][0] > intervals[i + 1][0] - intervals[i][1] or intervals[i + 1][1] - intervals[i + 1][0] > intervals[i + 1][0] - intervals[i][1]:
                    intervals[i][1] = intervals[i + 1][1]
                    del intervals[i + 1]
                    i = i - 1
            i = i + 1

        i = 0
        while i < len(intervals):
            if intervals[i][1] - intervals[i][0] < fuzz:
                del intervals[i]
                i = i - 1
            i = i + 1

        if nice:
            for i in intervals:
                i[0] = self.human_time(i[0])
                i[1] = self.human_time(i[1])

        return intervals

    def log_data(self, lvl="discord", scope=-1, fuzz=1, nice=True):
        """
        Return data in a "log-like" format, where accesses to specific parts of
        Discord are recorded.  Note that due to fuzz, times may add up to more
        than the actual time spent on Discord.

        Inputs:
            cope: the number of seconds to look back in time.  If -1, the
                current day.
            lvl: how fine-grained the data should be.  There are three accepted values:
                discord: over the entire system. ("0" works also.)
                server: separate data by server. ("1" works also.)
                channel: separate data by channel. ("2" works also.)
            fuzz: the amount of "fuzz" or time spent somewhere else that can be
                counted within a single "consecutive" block of time or minimal
                interval length that will be counted.
            nice: make times human-readable.

        Outputs:
            list of lists: activity log.
        """
        if scope == -1:
            scope = (self.runtime + self.offset) % 86400
        else:
            scope = self.phrase_to_sec(scope)
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

        activity_log = []
        if lvl == "discord":
            pending = self.detail_data("", "discord", scope=scope, fuzz=fuzz, nice=False)
            for p in pending:
                activity_log.append([p[0], p[1], p[1]-p[0], "Discord"])
        elif lvl == "server":
            server_list = self.sprawl_data(scope=scope, lvl="server", nice=False).keys()
            for server in server_list:
                pending = self.detail_data(server, "server", scope=scope, fuzz=fuzz, nice=False)
                for p in pending:
                    activity_log.append([p[0], p[1], p[1]-p[0], server])
        elif lvl == "channel":
            channel_list = self.sprawl_data(scope=scope, lvl="channel", nice=False).keys()
            for channel in channel_list:
                pending = self.detail_data(channel, "channel", scope=scope, fuzz=fuzz, nice=False)
                for p in pending:
                    activity_log.append([p[0], p[1], p[1]-p[0], channel])

        activity_log = sorted(activity_log, key=lambda x: x[0])

        if nice:
            for line in activity_log:
                line[0] = self.human_time(line[0])
                line[1] = self.human_time(line[1])
                line[2] = self.human_interval(line[2])

        return activity_log
