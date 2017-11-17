#!/usr/bin/env python

import sys
from crontab import CronTab

gs_cron = CronTab(user='guestshell')

iter = gs_cron.find_command('msi_token.py')

for line in iter:
    if line:
        # Job already exists.  Just exit.
        sys.exit()

# Job needs to be created in cron
job = gs_cron.new(command='sudo /home/guestshell/azure/msi_token.py')

job.minute.every(55)

gs_cron.write()
