from crontab import CronTab3

with CronTab(user=True) as cron:
    job = cron.new(command="PYTHONPATH=/Users/califynic/anaconda3/bin/python3.7 /Users/califynic/anaconda3/bin/python3.7 /Users/califynic/Desktop/coding/cs630/fall21/time-cord/time-cord/monitor.py")
    job.minute.every(1)
