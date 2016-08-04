#!/usr/bin/python
import pexpect
import time
import sys
import getpass
import time
import joblib
import multiprocessing
import getpass
from optparse import OptionParser
import subprocess
#
#
#
max_par = int(raw_input("enter the number of max simultaneous connections: "))
#
#
#
gusername = ''
gpassword = ''
gusername = raw_input("enter username: ")
while True:
	if gusername == '':
		try:
			print("Warning!!, username is not valid, try again")
			gusername = raw_input("enter username: ")
		except Exception as e:
			raise
		else:	
			print("username is {0}".format(gusername))
		#finally:
		#	print("done with username")
	else:
		break
#self.gusername = gusername
# set up password
gpassword = getpass.getpass("enter password: ")
gpassword_val = getpass.getpass("enter password again: ")
while True:
	if gpassword == '':
		print("Password can not be empty")
		gpassword = getpass.getpass("enter password: ")
		gpassword_val = getpass.getpass("enter password again: ")
		continue
	elif gpassword != gpassword_val:
		print("Warning!!, Passwords do not match, retry")
		gpassword = getpass.getpass("enter password: ")
		gpassword_val = getpass.getpass("enter password again: ")
	else:
		break
#initdate = ""
initdate = (time.strftime("%Y%m%d-%H_%M%S"))
#
#
#
#if opt.ccmdfile != "-":
#	with open('targethost.txt', 'r') as file:
#		targethostfile_list = file.read().splitlines()
#elif opt.ccmddir != "-":
#	file = subprocess.check_output(['ls', '{0}'.format(opt.ccmddir)]).decode('ascii')
#	targethostfile_list = file.split()
#
#
green_cl = '\033[92m'
red_cl = '\033[91m'
yel_cl = '\033[93m'
blk_cl = '\033[0m'
#
def main_process(gusername, gpassword, targethosthost):
	host_authen_err = False
	host_con_err = False
	if opt.utelnet:
		session1 = pexpect.spawn('telnet %s' % targethosthost)
	elif opt.ussh:
		session1 = pexpect.spawn('ssh -oStrictHostKeyChecking=no {0}@{1}'.format(gusername,targethosthost))	
	else: 
		print("please specifiy -s or -t for ssh or telnet")
	if pexpect_authenticate_enable(gusername, gpassword, session1, targethosthost) == "priv_mode_access":
		hostlogfile = open('log/{0}_{1}'.format(initdate, targethosthost), 'wb')
		if opt.ccmdfile != "-":
			command_file = str(opt.ccmdfile)
		elif opt.ccmddir != "-":
			command_file = str(str(opt.ccmddir) + '/' + targethosthost)
			#print(command_file)
		session1.logfile_read = hostlogfile
		targetcommandfile = open('{0}'.format(command_file), 'r')
		#targetcommandfile = open('config_output/{0}'.format(targethosthost), 'r')
		targetcommandfile_list = targetcommandfile.readlines()
		priv_config(session1,targetcommandfile_list)
		#targetcommandfile.close
	else:
		host_authen_err = True
		#print("!@#!@#!@#login error_{0}_!@#!@#!@#".format(targethosthost))
	#
	if host_con_err:
		print(red_cl + "{0}-:------------------------------------login error".format(targethosthost) + blk_cl)
	elif host_authen_err:
		print(yel_cl + "{0}-:------------------------------------authentication error".format(targethosthost) + blk_cl)
	else:
		print(green_cl + "{0}-:------------------------------------complete".format(targethosthost) + blk_cl)	

	
#
#
#
def priv_config(session1,targetcommandfile_list):
	session1.sendline("term len 0")
	for command in targetcommandfile_list:
		#print("{0}".format(command))
		session1.sendline("%s" % command)
		session1.expect("#", timeout=120)
		session1.sendline("")
		session1.expect("#", timeout=120)
		#continue
	session1.expect("#")
	session1.sendline("end")
	session1.expect("#")
	session1.sendline("exit")
	session1.expect(pexpect.EOF)
	session1.close()
#
#
#
def pexpect_authenticate_enable(gusername, gpassword, session1, targethosthost):
	pexpect_authenticate_result = pexpect_authenticate(gusername, gpassword, session1 , targethosthost)
	if pexpect_authenticate_result == "enable_mode":
		return "priv_mode_access"
	elif pexpect_authenticate_result == "enable_run_authen":
		session1.sendline("enable")
		priv_pass_results = session1.expect(["error", "[pP]assword: "])
		if priv_pass_results == 0:
			#print ("!@#!@#!@#enable password missing_{0}_!@#!@#!@#".format(targethosthost))
			host_authen_err = True
		elif priv_pass_results == 1:
			session1.sendline("{0}".format(gpassword))
			priv_authen_results  = session1.expect (["#" , "Access denied"])
			if priv_authen_results == 0:
				return "priv_mode_access"
			elif priv_authen_results == 1:
				return "priv_mode_denied"
			else:
				return "priv_mode_error"
	elif pexpect_authenticate_result == "enable_authen_err":
		#print ("enalbe authentication failure_{0}_".format(targethosthost))
		host_authen_err = True
#
#
#
def pexpect_authenticate(gusername, gpassword, session1, targethosthost):
	pextect_spawn_result = pextect_spawn(session1, targethosthost)
	if pextect_spawn_result == "login_username":
		session1.sendline("%s" % gusername)
		session1.expect("[pP]assword: ")
		session1.sendline("%s" % gpassword)
		priv_results  = session1.expect (["#", ">", "Access denied", "failed"])
		if priv_results == 0:
			return "enable_mode"
		elif priv_results == 1:
			return "enable_run_authen"
		elif priv_results == 2:
			return 'enable_authen_err'
		elif priv_results == 3: 
			#print("!@#!@#!@#authentication error_{0}_!@#!@#!@#".format(targethosthost))
			host_authen_err = True
		#print "authen_comp_user"
	elif pextect_spawn_result == "login_password":
		session1.sendline("%s" % gpassword)
		priv_results  = session1.expect (["#", ">", "Access denied"])
		if priv_results == 0:
			return "enable_mode"
		elif priv_results == 1:
			return "enable_run_authen"
		elif priv_results == 2:
			return 'enable_authen_error'
		else:
			#print("!@#!@#!@#authentication error_{0}_!@#!@#!@#".format(targethosthost))
			host_authen_err = True
		print "authen_comp_pass"
#
#
#
def pextect_spawn(session1, targethosthost):
	spawn_results  = session1.expect (["Unable to connect", "[uU]sername: ", "[pP]assword: ", "not responding", " Bad IP", " refused", pexpect.EOF, pexpect.TIMEOUT])
	if spawn_results == 0:
		#print ("!@#!@#!@#host down can not connect to host {0}!@#!@#!@#".format(targethosthost))
		host_con_err = False
		return "host_down"
	elif spawn_results == 1:
		#print ("###starting {0}###".format(targethosthost))
		return "login_username"
	elif spawn_results == 2:
		#print ("###starting {0}###".format(targethosthost))
		return "login_password"
	elif spawn_results == 3 or spawn_results == 4 or spawn_results == 5:
		host_authen_err = True
		#print ("!@#!@#!@#authentication or login error {0}!@#!@#!@#".format(targethosthost))
		host_con_err = False
		return "login_error"	
	else:
		#print ("!@#!@#!@#authentication or login error {0}!@#!@#!@#".format(targethosthost))
		host_authen_err = True
		return "login_error"
#
#
#
def main():
	joblib.Parallel(n_jobs=max_par)(joblib.delayed(main_process)(gusername, gpassword,targethosthost) for targethosthost in targethostfile_list)
#
#
#
if __name__ == "__main__":
	pars = OptionParser()
	pars.add_option("-s", "--usessh",help="connect using ssh", action="store_true", dest="ussh", default=False)
	pars.add_option("-t", "--usetelnet",help="connect using telnet", action="store_true", dest="utelnet", default=False)
	pars.add_option("-c", "--ccmdfile",help="send command from a specific file", dest="ccmdfile", default='-')
	pars.add_option("-d", "--ccmddir",help="send command from a specific dir", dest="ccmddir", default='-')
	opt, args = pars.parse_args()
	if opt.ccmdfile != "-":
		with open('targethost.txt', 'r') as file:
			targethostfile_list = file.read().splitlines()
	elif opt.ccmddir != "-":
		file = subprocess.check_output(['ls', '{0}'.format(opt.ccmddir)]).decode('ascii')
		targethostfile_list = file.split()
	main()
#
#
#####use telnet and use a static command file
# 			python push-config-telnet-collection.py -t -c command.txt
#####use telnet and use a dynamic config file
# 			python push-config-telnet-collection.py -t -d cmd_dir
#####use ssh and use a dynamic config file
#			python push-config-telnet-collection.py -s -d cmd_dir