#!/usr/bin/python
# -*- coding: utf-8 -*-
import commands
import sys
import os
import re
import zipfile
import urllib2
import shutil
from urllib2 import URLError, HTTPError
from datetime import date,datetime,timedelta
 
class Package:
    """
    检查fuse-curlftpfs软件包的安装与否，如果没有，则安装之
    """
 
    def __init__(self,name):
        self.name=name
    def install(self):
        print('execute "yum install ' + self.name + '"...')
        #cmd=commands.getstatusoutput('yum install ' +  self.name + ' -y')
        print os.system('yum install ' +  self.name + ' -y')
        if self.name in os.popen('rpm -qa | grep ' + self.name).read():
            print('Install ' + self.name + ' successful.')
        else:
            print('Install ' + self.name + ' failed, aborting.')
            sys.exit()
    def checkinstall(self):
        cmd=commands.getstatusoutput('rpm -qa | grep ' +  self.name)
        if self.name in cmd[1]:
            print(self.name + ' has aleady installed. Continue...')
        else:
            print(self.name + ' isn\'t installed. Ready to install it.')
        self.install()
 
class Backup:
    """
    使用shell命令挂载之，然后执行备份过程（压缩目录，删除旧文件），压缩完成以后再解除挂载
    """
 
    def __init__(self,server,user,passwd,webroot,backupname):
        self.server=server
        self.user=user
        self.passwd=passwd
        self.webroot=webroot
        self.backupname=backupname
    def mount(self):
        #判断挂载点是否存在，如果不存在则尝试新建
        try:
            if os.path.isdir('/' + self.backupname):
                print('found mount point /' + self.backupname + ', ready to mount ftp server.')
            else:
                print('doesn\'t found mount point /' + self.backupname + ', build it.')
                os.mkdir('/' + self.backupname)
        except IOError, error:
            print error
            sys.exit()
 
        #开始挂载
        cmd=commands.getstatusoutput(r'curlftpfs ftp://' + self.user + ':' + self.passwd + '@' + self.server + r' /' + self.backupname + ' -o codepage=utf8')
        print cmd[1]
 
        #检验是否挂载成功
        pat=r'fuse(.+)/' + self.backupname
        all=os.popen('df -hT').read()
        if re.search(pat,all):
            print('mounted /' + self.backupname + ', continue...')
        else:
            print('mount failed. please check.')
            sys.exit()
         
    #把php脚本发送至FTP
        try:
            src = file(os.getcwd() + '/db_backup.php', 'r+')
            des = file('/' + self.backupname + '/' + self.webroot + '/db_backup.php', 'w+')
            des.writelines(src.read())
            src.close()
            des.close()
            if not os.path.isdir('/' + self.backupname + '/' + self.webroot + '/db_backup'):
                os.mkdir('/' + self.backupname + '/' + self.webroot + '/db_backup')
        #访问php文件（导出数据库）
            try:
                page=urllib2.urlopen('http://' + self.server + '/db_backup.php')
                print page.read()
            except (URLError, HTTPError), err:
                print err
                print('mysqldump failed! please check.')
        except (IOError, OSError), e:
            print e
            self.umount()
            sys.exit()
         
    def backup(self):
 
        self.mount()
 
        newday = date.today()    #获取今天的日期
        oldday = date.today()-timedelta(5)    #获得5天前的日期
        newfile = self.backupname + '_backup_' + str(newday.year) + '.' + str(newday.month) + '.' +  str(newday.day) + '.zip'    #本次备份的文件名
        oldfile = self.backupname + '_backup_' + str(oldday.year) + '.' + str(oldday.month) + '.' +  str(oldday.day) + '.zip'    #5天前备份的文件名
 
        print('delete old file...')
        try:
            if os.path.isfile(oldfile):
                os.remove(oldfile)
            else:
                print('don\'t found old file, jumped.')
        except IOError, err:
            print err
 
    #开始压缩目录
        print('compress directory. it will take a while.')
        try:
            try:
                f = zipfile.ZipFile(newfile,'w',zipfile.ZIP_DEFLATED)
                for dirpath, dirnames, filenames in os.walk('/' + self.backupname + '/' + self.webroot):
                    for filename in filenames:
                        f.write(os.path.join(dirpath,filename))
                print("backup completely! file name is " + newfile)
            except (IOError, OSError), err:
                print err
        finally:
            f.close()
            self.umount()
            sys.exit()
 
    def umount(self):
 
    #删除FTP里的数据库目录和文件
        if os.path.isdir('/' + self.backupname + '/' + self.webroot + '/db_backup'):
            shutil.rmtree('/' + self.backupname + '/' + self.webroot + '/db_backup')
        if os.path.isfile('/' + self.backupname + '/' + self.webroot + '/db_backup.php'):
            os.remove('/' + self.backupname + '/' + self.webroot + '/db_backup.php')
             
    #判断是否解除挂载成功
        print os.system('umount /' + self.backupname)
        pat=r'fuse(.+)/' + self.backupname
        all=os.popen('df -hT').read()
        if not re.search(pat,all):
            print('umounted /' + self.backupname + '. Done!')
        else:
            print('umount failed. please check.')
 
if __name__=='__main__':
    ps=Package('fuse-curlftpfs')
    ps.checkinstall()
 
    #如果不是独立IP的话，FTP地址请填写服务商分配的三级域名，请确保能通过"http://FTP地址"访问网站首页
    #FTP地址开头不要加http://，末尾不要加/
    #网站目录是指FTP上存放网站的目录，有些国内服务商喜欢把网站目录设置成FTP根目录下的wwwroot目录
    #如果网站目录就是FTP根目录，把此项留空即可（填写成''）
    #标示符是挂载到本地的文件名，及压缩以后的文件名，只能用英文且不能有空格，可以用下划线
    #如果要备份多个FTP，把下面2行复制一遍即可，注意每个的标示符不能一样
    bu=Backup('FTP地址','FTP用户名','FTP密码','网站目录','标示符')
    bu.backup()
