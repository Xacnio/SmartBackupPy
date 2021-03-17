import paramiko
import zipfile
import os.path
from os import remove
from datetime import datetime
from config import config
import traceback
import ftplib
import shutil

def get_date_time():
    now = datetime.now()
    dt_string = now.strftime("%d-%b-%Y-%H-%M-%S")
    return dt_string

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def smartbackup(prefix, local_backup_dir, path, remote_dir, maxBackupOnRemoteDir=0, deleteLocal=False):
    if os.path.isdir(path):
        local_backup_dir = os.path.dirname(local_backup_dir+"/")
        loczip = local_backup_dir + "/" + prefix + "-" + get_date_time() + ".zip"
        zip = zipfile.ZipFile(loczip, "w", zipfile.ZIP_DEFLATED)
        zipdir(path, zip)
        zip.close()
    elif os.path.isfile(path):
        local_backup_dir = os.path.dirname(local_backup_dir+"/")
        extension = os.path.splitext(path)
        loczip = local_backup_dir + "/" + prefix + "-" + get_date_time() + extension[1]     
        shutil.copy(path, loczip)
    else:
        return {
            'error': True,
            'exception': None,
            'error_str': "Directory or file not found",
            'traceback': None,
            'success': False,
            'uploaded_file': None,
            'remote_dir': remote_dir
        }
    if os.path.isfile(loczip):
        timestamp = int(datetime.timestamp(datetime.now()))
        filesize = os.path.getsize(loczip)
        if config['type'].lower() == "sftp":
            return upload_to_backup_sftp(remote_dir, loczip, {'timestamp': timestamp, 'filesize': filesize}, maxBackupOnRemoteDir, deleteLocal)
        elif config['type'].lower() == "ftp":
            return upload_to_backup_ftp(remote_dir, loczip, {'timestamp': timestamp, 'filesize': filesize}, maxBackupOnRemoteDir, deleteLocal)
        else:
            return {
                'error': True,
                'exception': None,
                'error_str': "Invalid protocol type (sftp/ftp)",
                'traceback': None,
                'success': False,
                'uploaded_file': loczip,
                'remote_dir': remote_dir
            }
    else:
        return {
            'error': True,
            'exception': None,
            'error_str': "ZIP not found",
            'traceback': None,
            'success': False,
            'uploaded_file': loczip,
            'remote_dir': remote_dir
        }

def upload_to_backup_sftp(remote_dir, file, fileinfo, maxBackupOnRemoteDir=0, deleteLocal=False):
    # UPLOAD & PROCESS SETTINGS #
    dir = os.path.dirname(remote_dir+"/")
    localpath = file
    file = os.path.basename(file)
    path = dir+'/' + file
    extension = os.path.splitext(file)
    pathtmp = dir+'/' + extension[0] + "-tmp" + extension[1]
    maxBackupOnRemoteDir = maxBackupOnRemoteDir - 1 # Upload and delete +1 uploading file
    remote_deleted = []

    # REMOTE PROTOCOL SETTINGS #
    try:
        host = config['host']
        port = int(config['port'])
        username = config['user']
        password = config['pass']
    except KeyError as err:
        return {
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path
        }
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(None,username,password)
        protocol = paramiko.SFTPClient.from_transport(transport)
    except Exception as err:
        return {
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path
        }

    try:
        protocol.stat('./'+dir)
        files = protocol.listdir('./'+dir)
        protocol.put(localpath, pathtmp)
        protocol.rename(pathtmp, path)
        if maxBackupOnRemoteDir > 0 and len(files) > maxBackupOnRemoteDir:
            diff = len(files) - maxBackupOnRemoteDir
            count = 0
            for tfile in files:
                extension = os.path.splitext(tfile)
                if tfile.find("-tmp"+extension[1]) != -1:
                    continue
                try:
                    protocol.remove(dir + '/'+tfile)
                    remote_deleted.append(dir + '/'+tfile)
                except:
                    continue
                count = count + 1
                if count >= diff:
                    break
        if deleteLocal is True:
            if os.path.isfile(localpath):
                remove(localpath)
    except IOError as err:
        protocol.close()
        transport.close()
        return {
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path,
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
        }
    except Exception as err:
        protocol.close()
        transport.close()
        return {
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path,
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
        }

    protocol.close()
    transport.close()
    return {
        'success': True,
        'uploaded_file': localpath,
        'remote_dir': path,
        'fileinfo': fileinfo,
        'error': False,
        'exception': "",
        'error_str': "",
        'traceback': "",
    }

def upload_to_backup_ftp(remote_dir, file, fileinfo, maxBackupOnRemoteDir=0, deleteLocal=False):
    # UPLOAD & PROCESS SETTINGS #
    dir = os.path.dirname(remote_dir+"/")
    localpath = file
    file = os.path.basename(file)
    path = dir+'/' + file
    extension = os.path.splitext(file)
    pathtmp = dir+'/' + extension[0] + "-tmp" + extension[1]
    maxBackupOnRemoteDir = maxBackupOnRemoteDir - 1 # Upload and delete +1 uploading file
    remote_deleted = []

    # REMOTE PROTOCOL SETTINGS #
    try:
        host = config['host']
        port = int(config['port'])
        username = config['user']
        password = config['pass']
    except KeyError as err:
        return {
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path
        }
    try:
        protocol = ftplib.FTP()
        protocol.connect(host, port)
        protocol.login(username, password)
    except Exception as err:
        return {
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path
        }

    try:
        protocol.mlsd('./'+dir)
        files = protocol.mlsd('./'+dir)
        _file = open(localpath, "rb")
        protocol.storbinary(f"STOR {pathtmp}", _file)
        protocol.rename(pathtmp, path)
        _file.close()
        if maxBackupOnRemoteDir > 0 and len(files) > maxBackupOnRemoteDir:
            diff = len(files) - maxBackupOnRemoteDir
            count = 0
            for tfile in files:
                _extension = os.path.splitext(tfile)
                if tfile.find("-tmp"+_extension[1]) != -1 or tfile.split('-')[0] != extension[0].split('-')[0]:
                    continue
                try:
                    protocol.delete(dir + '/'+ tfile)
                    remote_deleted.append(dir + '/'+tfile)
                except:
                    continue
                count = count + 1
                if count >= diff:
                    break
        if deleteLocal is True:
            if os.path.isfile(localpath):
                remove(localpath)
    except IOError as err:
        protocol.close()
        return {
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path,
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
        }
    except Exception as err:
        protocol.close()
        return {
            'success': False,
            'uploaded_file': localpath,
            'remote_dir': path,
            'error': True,
            'exception': err,
            'error_str': str(err),
            'traceback': traceback.format_exc(),
        }

    protocol.close()
    return {
        'success': True,
        'uploaded_file': localpath,
        'remote_dir': path,
        'fileinfo': fileinfo,
        'error': False,
        'exception': "",
        'error_str': "",
        'traceback': "",
    }