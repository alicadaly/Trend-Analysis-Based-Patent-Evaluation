#!/usr/bin/python
# -*- encoding: utf8 -*-
# analysis the effect of gamma threshold on the percentage of topics left in a lda topic or tfidf file.

__author__ = 'Leon'

from optparse import OptionParser
import csv, sys, logging, os
csv.field_size_limit(sys.maxsize)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def main(options,args):
	'''\
	%prog [options]  <ldaValueFile> <number of topics> <list of threshold>
		or [options] <tfidfFile> <list of threshold>
	'''
	# if not os.path.exists(directory):
	# 	os.makedirs(directory)
	ldaOrtfidfFile = args[0]

	if options.lda:
		number_topics = int(args[1])
		thresholds = map(float,args[2:])
		thresholdsDic = {x:[] for x in thresholds}
		thresholdsDic[0.01] = []
		infile = open(ldaOrtfidfFile,'r')
		reader = csv.reader(infile,delimiter=',')
		for line in reader:
			newline = [eval(x)  for x in line]
			for key in thresholdsDic:
				left = [b for (a,b) in newline if float(b) > key]
				thresholdsDic[key].append(len(left)/float(number_topics))
		for key in thresholdsDic:
			thresholdsDic[key] = sum(thresholdsDic[key])/len(thresholdsDic[key])
		print sorted(thresholdsDic.items(),key= lambda e:e[0])
		infile.close()
	if options.tfidf:
		thresholds = map(float,args[1:])
		thresholdsDic = {x:[] for x in thresholds}
		infile = open(ldaOrtfidfFile,'r')
		reader = csv.reader(infile,delimiter=',')
		for line in reader:
			newline = [eval(x)  for x in line]
			for key in thresholdsDic:
				left = [b for (a,b) in newline if float(b) > key]
				thresholdsDic[key].append(len(left)/float(len(line)))
		for key in thresholdsDic:
			thresholdsDic[key] = sum(thresholdsDic[key])/len(thresholdsDic[key])
		print sorted(thresholdsDic.items(),key= lambda e:e[0])
		infile.close()

if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)

	# specify whether it's lda
	parser.add_option("-l", "--lda",
				  action="store_true", dest="lda", default=False,
				  help="if '-l' is on, treat the input file as the lda value")
	# specify whether do tfidf
	parser.add_option("-t", "--tfidf",\
				  action="store_true", dest="tfidf", default=False,\
				  help="if '-t' is on, treat the input file as tfidf value")

	options,args = parser.parse_args()

	# if len(args) < 3:
	# 	print 'arguments are the trend file, date file original data, renewfile'
	# 	sys.exit()
	directory = './feature'
	main(options,args)
	logging.info('finished %s' %__file__)