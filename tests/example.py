import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from backup import smartbackup
# create folder for local backups (backups/)
# create folder for remote backups (backups/)
print(smartbackup("test", "backups/", 'test.txt', './backups')) # file backup
print(smartbackup("test", "backups/", 'test/', './backups')) # directory zipping and backup