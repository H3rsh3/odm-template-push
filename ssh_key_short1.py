import pexpect
import time
import sys
import getpass
import time
#

gusername = str(raw_input("enter username: "))
gpassword = getpass.getpass("enter password: ")

targethostfile = open(r'targethost.txt', 'r')
targethostfile_list = targethostfile.readlines()


def main_run():
	for targethosthost in targethostfile_list:
		session1 = pexpect.spawn('ssh {0}@{1}'.format(gusername, targethosthost))
		run_authen(session1,gusername,gpassword)



def run_authen(session1,gusername,gpassword):
	prompt_level = check_authen(session1)
	print prompt_level
	if prompt_level == "pass_prompt":
		session1.sendline("%s" % gpassword)
		#session1.expect(">")
		#session1.interact()
		#print(session1.exitstatus, session1.signalstatus)
		#print(session1.after)
	elif prompt_level == "pass_prompt_key":
		session1.sendline("yes")



def check_authen(session1):
	session1.logfile = sys.stdout
	spawn_results  = session1.expect(["Unable to connect", "Username: ", "Password: ", "(yes/no)? ","host", pexpect.EOF, pexpect.TIMEOUT])
	if spawn_results == 0:
		result = "conn_error"
		return result
	if spawn_results == 1:
		result = "user_prompt"
		return result
	if spawn_results == 2:
		result = "pass_prompt"
		return result
	elif spawn_results == 3:
		result = "pass_prompt_key"
		return result
	elif spawn_results == 4:
		print "cannot connect"
		result = "connection_error"
		return result
	elif spawn_results == 5:
		print "cannot connect"
		result = "connection_error"
		return result

def main():
	main_run()

if __name__ == '__main__':
	main()