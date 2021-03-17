#  SmartBackupPy
 This package is experimental. You can use it by editing. I am not responsible for any errors and any losses.
 
 
    def smartbackup(prefix, local_backup_dir, path, remote_dir, maxBackupOnRemoteDir=0, deleteLocal=False)
 - **prefix:** Prefix of backup file name
 - **local_backup_dir:** Backup directory path for local
 - **path:** Directory or file path
 - **remote_dir:** Upload path in FTP/SFTP
 - **maxBackupOnRemoteDir:** If the upload path exceeds this variable, old files will be deleted. Backups is keep up to date, you can use less storage. (This is experimental, use in empty folder from remote server. Backup filenames includes date/time, ftp/sftp brings up file list alphabetically but may not be every time and this logic doesn't always right)
 - **deleteLocal:** If is True, local backup files will be deleted after upload.

[Example](tests/example.py)
