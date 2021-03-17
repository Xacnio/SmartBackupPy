import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from smartbackup import smartbackup
# create folder for local backups (backups/)
# create folder for remote backups (backups/)
print(smartbackup("test", "backups/", 'testfile.txt', './backups')) # file backup
print(smartbackup("test", "backups/", 'testfolder/', './backups')) # directory zipping and backup