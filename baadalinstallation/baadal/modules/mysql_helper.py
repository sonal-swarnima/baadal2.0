from gluon import DAL, Field
import remote_vm_task as remote_machine
from helper import get_mysqldb_machine_address , get_mysqldb_configuration

def create_account(user_id,new_password):
	mysql_server = get_mysqldb_machine_address()
	mysql_db = get_mysqldb_configuration()
	cmd = bash -c "mypassword='"+mysql_db[2]+"'/root/mysqlconf/mysql.sh -u"+ user_id" "+ new_password;
    out2 = remote_machine.execute_remote_cmd(mysql_server[0],mysql_server[1],cmd,mysql_server[2])
	return;
	
def change_password(user_id,new_password):
	'''check if user exists
	
	SELECT User FROM mysql.user WHERE User = 'Username'
	if exists then change_password else
	create_account(user_id,new_password)
	return;
	
	'''
	mysql_server = get_mysqldb_machine_address()
	mysql_db = get_mysqldb_configuration()
	cmd = bash -c "mypassword='"+mysql_db[2]+"'/root/mysqlconf/mysql.sh -cp "+ user_id" "+ new_password;
    out2 = remote_machine.execute_remote_cmd(mysql_server[0],mysql_server[1],cmd,mysql_server[2])
	return;
	
def create_databse(user_id,database_name):
	'''check if db_exists
	
	SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'DBName'
	if exists return False else 
	'''
	mysql_server = get_mysqldb_machine_address()
	mysql_db = get_mysqldb_configuration()
	cmd = bash -c "mypassword='"+mysql_db[2]+"'/root/mysqlconf/mysql.sh -d "+ database_name" "+ user_id;
    out2 = remote_machine.execute_remote_cmd(mysql_server[0],mysql_server[1],cmd,mysql_server[2])
	return True;

