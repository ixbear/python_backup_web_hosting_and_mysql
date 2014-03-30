<?php
$db_server = 'localhost';  //一般不需要改
$db_user = '数据库用户名';
$db_pass = '数据库密码';
$save_path = './db_backup';  //导出的数据库备份目录
$suf='.sql';
  
function actionExport($db_server, $db_user, $db_pass, $save_path, $suf){
    echo "Now start exporting databases...\n ";
    $conn = mysql_connect($db_server, $db_user, $db_pass) or die("couldn't connect to mysql.");
    mysql_query("SET NAMES 'utf8'");
    $result_db = mysql_list_dbs($conn);
    for ($i=0;$i<mysql_num_rows($result_db);$i++){
    $db_name = mysql_tablename($result_db,$i);
    echo "dump database: $db_name";
        $cmd = "mysqldump -h $db_server -u $db_user -p$db_pass -q --skip-lock-tables $db_name > $save_path/$db_name$suf";
        dbdump($cmd);
    }
    mysql_close($conn);
}
  
function dbdump($cmd){
    passthru($cmd, $ret);
    if ($ret != 0) {
        echo " : Failed\n ";
    }else{
        echo " : OK \n ";
    }
}
  
if (mysql_connect($db_server, $db_user, $db_pass)) {
    actionExport($db_server, $db_user, $db_pass, $save_path, $suf);
}else{
    echo "Could not connect to mysql.";
}
?>
