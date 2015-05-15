#!/usr/bin/python
# -*- encoding: utf8 -*-

# given a folder, walk through the files in the folder, pick all of them with suffix 'txt' 
# combine them based on the first column
# generally, the first column is the same

__author__ = 'Leon'

from optparse import OptionParser
import csv, sys, logging, os
csv.field_size_limit(sys.maxsize)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main(options,args):
	'''given one master folder name, go into each sub folder and combine all these feature files
		or given several folder name, go to each folder and combine all these feature files
	'''

	if options.oneMasterFolder:
		masterFolder = args[0]
		folders = [os.path.join(masterFolder,x) for x in os.listdir(masterFolder) if os.path.isdir(os.path.join(masterFolder,x))]
	else:
		folders = args
	for folder in folders:
		combineFiles(folder,os.path.join(folder,'features'))
def combineFiles(folderName,writefilename):
	filelist = [filename for filename in os.listdir(folderName) if 'txt' in filename]
	for filename in filelist:
	    reader = open(os.path.join(folderName,filename),'r')
	    length = len(reader.next().split(','))
	    for index,line in enumerate(reader):
	        if len(line.split(','))!= length:
	            print filename,index,line
	readers = [open(os.path.join(folderName,x),'r') for x in filelist]
	writefile = open(writefilename,'w')
	writefile.write(','.join(filelist)+'\n')
	for line in zip(*readers):
		linelist = map(lambda one: one.strip().split(','),line)
		lineid = linelist[0][0]
		for columns in linelist:
			if columns[0] != lineid:
				print 'line id do not match'
				sys.ext() 
		newline = [lineid]
		for features in linelist:
			newline.extend(features[1:])
		writefile.write(','.join(newline)+'\n')
		break
	for reader in readers:
		reader.close()
	writefile.close()
if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)

	parser.add_option("-1", "--onemaster",
				  action="store_true", dest="oneMasterFolder", default=False,
				  help="if '-one' is on, given is one master folder")

	options,args = parser.parse_args()

	# if len(args) < 3:
	# 	print 'arguments are the trend file, date file original data, renewfile'
	# 	sys.exit()
	main(options,args)
	logging.info('finished %s' %__file__)