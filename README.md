python_backup_web_hosting_and_mysql
===================================

use python scripts to backup web hosting(FTP function) and mysql.

写这个脚本初衷是想借助VPS来定期备份虚拟主机上的文件和数据库。最近对美国VPS的速度有点不满了，想把博客搬到香港的虚拟主机上，但虚拟主机的备份不太方便，于是就冒出了这样一个想法：用VPS备份虚拟主机。

程序包含2个文件，分别是
db_backup.py：主程序，在里面设置好虚拟主机的FTP地址，用户名和密码信息，然后执行备份程序；
db_backup.php：导出Mysql的脚本。

大部分Mysql服务器有个locahost的限制，只能在本地连接，不能远程连接数据库，因此编写了一个php的脚本（db_backup.php），用来导出数据库。主程序（db_backup.py） 会把此脚本发送到远程FTP的根目录，再访问http://ftp/db_backup.php导出数据库（存放在FTP的db_backup目录），备份完成以后会删除此脚本和db_backup目录。

前提条件：
1，VPS安装Python，这个一般没问题，VPS的虚拟化技术不能是OpenVZ。
2，虚拟主机必须是php型的，且支持passthru()函数，中国大陆的主机一般都支持。



