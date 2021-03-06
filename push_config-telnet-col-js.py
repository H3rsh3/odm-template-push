import pexpect
import time
import sys
import getpass
import time
import joblib
import multiprocessing
import getpass
#
#
#
max_par = int(raw_input("enter the number of max simultaneous connections: "))
#
#print num_cores
#
ios_js = "R1"
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
#print (gusername)
#print (gpassword)
#initdate = (time.strftime("%Y%m%d_%H%M"))
initdate = (time.strftime("%Y%m%d-%H_%M%S"))
#
#host_list = (["2.2.2.101", "2.2.2.102", "2.2.2.103", "2.2.2.104"])
#command_list = (["term len 0", "show ip route", "show ip bgp", "show ip int brief", "show ver", "show proc cpu"])
#
#session1 = pexpect.spawn('telnet 2.2.2.104')
#
#
#targetcommandfile = open('command.txt', 'r')
#targetcommandfile_list = targetcommandfile.readlines()
#
#targethostfile = open('targethost.txt', 'r')
#targethostfile_list = targethostfile.readlines()
with open('targethost.txt', 'r') as file:
    targethostfile_list = file.read().splitlines()
#test="testfile"
#
def main_process(gusername, gpassword, targethosthost):
#for targethosthost in targethostfile_list:
	#targethosthost = targethosthost[:-1]
	session1 = pexpect.spawn('telnet %s' % ios_js)
	if pexpect_authenticate_enable(gusername, gpassword, session1, targethosthost) == "priv_mode_access":
		#print "match"
		if lgn_from_js(session1,targethosthost) == "priv_mode_access":
			hostlogfile = open('log/{0}_{1}'.format(initdate, targethosthost), 'wb')
			command_file = "command.txt"
			session1.logfile_read = hostlogfile
			targetcommandfile = open('{0}'.format(command_file), 'r')
			targetcommandfile_list = targetcommandfile.readlines()
			priv_config(session1,targetcommandfile_list)
			#print "DONE========================================================================="
		else:
			print "!@#!@#!@#login error from js!@#!@#!@#"
	else:
		print "!@#!@#!@#login error!@#!@#!@#"
	print "%s complete" % targethosthost
#
#
#
def lgn_from_js(session1,targethosthost):
	session1.sendline("telnet {0}".format(targethosthost))
	return pexpect_authenticate_enable(gusername, gpassword, session1, targethosthost)

#
#
#
def priv_config(session1,targetcommandfile_list):
	session1.sendline("term len 0")
	for command in targetcommandfile_list:
		print "{0}".format(command)
		session1.sendline("%s" % command)
		#session1.wait()
		session1.expect("#", timeout=120)
		#config_results  = session1.expect (["#" , "]?"])
		#if config_results == 0:
		#	session1.sendline("%s" % command)
		#elif config_results == 1:
		#	session1.sendline("")
		continue
	session1.expect("#")
	#session1.sendline("you are here")
	session1.sendline("end")
	session1.expect("#")
	session1.sendline("exit")
	session1.expect("closed")
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
			print "!@#!@#!@#enable password missing!@#!@#!@#"
		elif priv_pass_results == 1: 
			session1.sendline("{0}".format(gpassword))
		#session1.expect("Password: ")
		#session1.sendline("%s" % gpassword)
			priv_authen_results  = session1.expect (["#" , "Access denied"])
			if priv_authen_results == 0:
				return "priv_mode_access"
			elif priv_authen_results == 1:
				return "priv_mode_denied"
			else:
				return "priv_mode_error"
	elif pexpect_authenticate_result == "enable_authen_err":
		print "authen"
#
#
#
def pexpect_authenticate(gusername, gpassword, session1, targethosthost):
	pextect_spawn_result = pextect_spawn(session1, targethosthost)
	if pextect_spawn_result == "login_username":
		session1.sendline("%s" % gusername)
		session1.expect("[pP]assword: ")
		session1.sendline("%s" % gpassword)
		priv_results  = session1.expect (["#", "\r\n\w+>", "Access denied", "failed","\r\n(\w|-)+>"])
		if priv_results == 0:
			return "enable_mode"
		elif priv_results == 1:
			return "enable_run_authen"
		elif priv_results == 2:
			return 'enable_authen_err'
		elif priv_results == 3: 
			print "!@#!@#!@#authentication error!@#!@#!@#"
		print "authen_comp_user"
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
			print "!@#!@#!@#authentication error!@#!@#!@#"
		print "authen_comp_pass"
#
#
#
def pextect_spawn(session1, targethosthost):
	#session1 = pexpect.spawn('telnet %s' % host)
	#session1.logfile = sys.stdout
	spawn_results  = session1.expect (["Unable to connect", "[uU]sername: ", "[pP]assword: ", "not responding", " Bad IP", " refused", pexpect.EOF, pexpect.TIMEOUT])
	if spawn_results == 0:
		print "!@#!@#!@#host down can not connect to host {0}!@#!@#!@#".format(targethosthost)
		return "host_down"
	elif spawn_results == 1:
		print "###starting {0}###".format(targethosthost)
		return "login_username"
	elif spawn_results == 2:
		print "###starting {0}###".format(targethosthost)
		return "login_password"
	elif spawn_results == 3 or spawn_results == 4 or spawn_results == 5:
		print "!@#!@#!@#authentication or login error {0}!@#!@#!@#".format(targethosthost)
		return "login_error"
	else:
		print "!@#!@#!@#authentication or login error {0}!@#!@#!@#".format(targethosthost)
		return "login_error"
#
#
#
def main():
	#main_process(gusername, gpassword)
	joblib.Parallel(n_jobs=max_par)(joblib.delayed(main_process)(gusername, gpassword,targethosthost) for targethosthost in targethostfile_list)
#
if __name__ == "__main__":
   main()
#
