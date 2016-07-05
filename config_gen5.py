import pandas as pd
import numpy as np
import shutil
import fileinput
import sys
import time

def import_config_data():
	#--import config_data file
	config_data = pd.read_csv("config_data", index_col='host')
	#--get the list of all hosts
	xhostconfig_hosts = config_data.index
	for host in xhostconfig_hosts:
		print "generating config for {0}".format(host)
		#--geenerate a copy of a the base file
		shutil.copy2("config_base", "config_output/{0}".format(host))
		#--get the row for the host, ie the host to genereate conig for
		xhostconfig = config_data.loc["{0}".format(host)]
		#--get the columns of the host, ie the items to replace
		xhostconfig_item = config_data.columns
		#--for each config_item(column) replace the config file
		for config_item in xhostconfig_item:
			#--get the "find" item to replace
			replace_item = config_item
			#--get the replacement value
			replace_item_with = xhostconfig["{0}".format(config_item)]
			#--find the config item to replace
			#--replace the config item
			hostconfig_file = fileinput.input(files=("config_output/{0}".format(host)),inplace=1)
			for line in hostconfig_file:
				replace = line.replace("<{0}>".format(replace_item), "{0}".format(replace_item_with))
				# use the "," at the end from preventing extra lines
				print replace,
				#time.sleep(.50)
			hostconfig_file.close()
		print "{0} done".format(host)
		print "======================"

def main():
	import_config_data()

if __name__ == "__main__":
   main()
