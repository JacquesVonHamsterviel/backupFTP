# coding:utf8

import os
import socket
import sys
import time
from ftplib import FTP
from datetime import datetime

class BackupFTP:
    def __init__(self, address,name,password,port):
        self.file_list = []
        self.address = address
        self.name = name
        self.password = password
        self.port = int(port)
        self.ftp = FTP()

    def __del__(self):
        self.ftp.close()

    def login(self):
        ftp = self.ftp
        try:
            timeout = 60
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(True)
            ulog('[FTP][Login]connecting...')
            ftp.connect(self.address, self.port)
            ftp.login(self.name, self.password)
            ulog('[FTP][Login]'+str(ftp.getwelcome()))
        except Exception as e:
            raise(e)

    def download_file(self, local_file, a_remote_file):
        ulog('[FTP][Download][{}]'.format(str(local_file)))
        file_handler = open(local_file, 'wb')
        self.ftp.retrbinary('RETR %s' % a_remote_file, file_handler.write)
        file_handler.close()

    def download_dir(self, a_local_dir='./', a_remote_dir='./'):                            
        """
        下载文件夹，
        :param a_local_dir:
        :param a_remote_dir:
        :return:
        """
        try:
            self.ftp.cwd(a_remote_dir)
        except Exception as e:
            raise(e, "No dir named" + a_remote_dir)
        if not os.path.isdir(a_local_dir):
            os.makedirs(a_local_dir)
        self.file_list = []
        self.ftp.dir(self.get_file_list)
        remote_names = self.file_list
        for item in remote_names:
            file_type = item[0]
            file_name = item[1]
            local = os.path.join(a_local_dir, file_name)
            if file_type == 'd':
                self.download_dir(local, file_name)
            elif file_type == '-':
                self.download_file(local, file_name)
    

        self.ftp.cwd('..')

    def get_file_list(self, line):
        """
        获取当前目录的所有文件名和目录名以及文件夹标志
        :param line:从dir函数获取的一行
        """
        file_infors = self.get_file_name(line)
        # 排除默认的. 和 .. 两个文件夹
        if file_infors[1] not in ['.', '..']:
            self.file_list.append(file_infors)

    @staticmethod
    def get_file_name(line):
        """
        从传入的一行数据里提取出文件名或者文件夹名
        传入数据格式： -rw-r--r--    1 0        0         3096506 Feb 12 01:02 access_20160211.log，第一个字符是文件类型，文件夹是d
        :param line: 传入的行
        :return: [文件夹标志，文件或者文件夹名]
        """
        # 保存文件夹标志
        file_arr = [line[0]]
        import re
        pattern = re.compile('[drwx-]{10}\s+?\d{1,2}\s+?\w+?\s+?\w+?\s+?\d+?\s+?[\d\w\u4e00-\u9fa5]+?\s+?\d+?\s+?[\d:]+?\s+?(.*)')
        match = pattern.match(line)
        if match:
            file_arr.append(match.group(1))
        else:
            raise("match filename")
        return file_arr


def get_date():
    now = datetime.now()
    return(now.strftime("%Y%m%d"))
def get_time():
    now = datetime.now()
    return(now.strftime("%Y%m%d-%H%M%S"))
def get_time_std_style():
    now = datetime.now()
    return(now.strftime("%Y-%m-%d %H:%M:%S")) 
def ulog(text):
    msg="[{}] {}".format(get_time_std_style(),text)
    print(msg)
    try:
        with open("logs/{}.txt".format(get_date()),'a+') as f:
            f.write(msg+"\n")
    except Exception as ex:
        print(ex)
    
def backup(address,port,name,password,remote_dir,local_dir):
    ulog("Start To BackUp[{}]from[{}:{}]to[{}]".format(remote_dir,address,port,local_dir))
    try:
        aFtp = BackupFTP(address,name,password,port)
        aFtp.login()
        aFtp.local_dir=local_dir
        aFtp.remote_dir=remote_dir
        aFtp.download_dir(local_dir, remote_dir)
        ulog("Successfully BackUp[{}]from[{}:{}]to[{}]".format(remote_dir,address,port,local_dir))
        return(True)
    except Exception as ex:
        ulog("Error Eet When BackUp[{}]from[{}:{}]to[{}]\nError Detail: {}".format(remote_dir,address,port,local_dir,str(ex)))
        return(False)
def daily_backup():
    ulog("[Daily Backup] Starts")
    backup("10.0.1.125","21","username","password","/apps","backup/{}/apps".format(get_date()))
    backup("10.0.1.34","21","username","password","/wwwroot","backup/{}/wwwroot".format(get_date()))
    ulog("[Daily Backup] Accomplished")
    
if __name__ == '__main__':
    #Example: backup("10.0.1.30","21","username","password","/wwwlogs","backup/{}/wwwlogs".format(get_date()))
    
    daily_backup()
