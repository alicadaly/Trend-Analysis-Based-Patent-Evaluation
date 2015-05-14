#!/usr/bin/python
# -*- encoding: utf8 -*-

from optparse import OptionParser
from gensim import corpora, models, similarities,matutils
import csv, sys, logging, os

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

__author__ = 'Leon'


def main(options,args):
	'''\
	%prog [options] <dictionary file> <tfidfValueFile> <patentidfile> <number_topword1> <number_topword2>...
	'''
	dictionaryfile = args[0]
	tfidfValueFile = args[1]
	patentidfile = args[2]
	threshold = options.threshold
	number_trendword_list = map(int,args[3:])

	# create a new directory for all data 
	if not os.path.exists(directory):
		os.makedirs(directory)
	# load the readPatentidList
	PatentidList = readPatentIDList(patentidfile)
	logging.info('patent id list has %s patents'%len(PatentidList))

	# load the popular word id list
	# TrendWordList = TrendWord(tfidfValueFile,number_trendword, options.top_k_word)

	# initailize a dictionary to store all trendword and their patent number
	Trend = {}
	WordFrequency = {}
	# for word in TrendWordList:
	# 	Trend[word] = []
	with open(tfidfValueFile,'r') as f:
		reader = csv.reader(f)
		for i,line in enumerate(reader):
			patent = map(eval,line)
			patent = [word for (word,weight) in patent if weight>threshold]
			try:
				for word in patent:
					if word not in Trend:
						Trend[word] = [PatentidList[i]]
					else:
						Trend[word].append(PatentidList[i])
					addIntoDic(word,WordFrequency)
			except IndexError:
				logging.info('ldaValueFile is bigger than patent id list')
				break
			last = i
		if last < len(PatentidList)-1:
			logging.info('ldaValueFile is smaller than patent id file')
			logging.info('ldaValueFile has %s patents'%(last+1))
	logging.info('finished creating Trend dictionary')
	# load the dictionary and corpus
	dictionary = corpora.Dictionary.load(dictionaryfile)
	logging.info('load the %s' %(dictionary))

	Trendlength = [(word,len(Trend[word])) for word in Trend]
	logging.info('%s words left after filter out based on beta'%len(Trendlength))

	sortedTrendWords = sorted(Trendlength,key = lambda e:e[1],reverse = True)

	patents = set()
	pre = 0
	for number_trendword in number_trendword_list:
		for (word,length) in sortedTrendWords[pre:number_trendword]:
			for patent in Trend[word]:
				patents.add(patent)
		logging.info('top %s word trend cover %s percent patents'%(number_trendword,len(patents)/float(len(PatentidList))))
		with open(directory+'/Top'+str(number_trendword)+'WordTrend.csv','w') as writefile:
			writer = csv.writer(writefile)
			for (word,length) in sortedTrendWords[0:number_trendword]:
				line = [dictionary.get(word)]
				line.extend(Trend[word])
				writer.writerow(line)		
		pre = number_trendword

# record the frequency of word
def addIntoDic ( key, myDict ):
	if key in myDict:
		myDict[key] += 1
	else:
		myDict[key] = 1
	return

def TrendWord(tfidf_value_file, top_n_trend_word, top_k_word):
	# the dictionary contain all word
	Dic = {}
	infile = file(tfidf_value_file,'r')
	reader = csv.reader(infile,delimiter=',')
	n = 1
	for line in reader:
		patent = map(eval,line)
		sortedpatent = sorted(patent, key = lambda x:x[1],reverse = True)
		y = len(sortedpatent)
		# print y
		x = 1
		while(x < y):
			# indicate to choose the top 10 key word
			if x > top_k_word:
				break
			addIntoDic(sortedpatent[x][0],Dic)
			x += 1
		# n += 1
		# if n > 100:
		# 	break
	infile.close()
	sortedWord = sorted(Dic.iteritems(), key=lambda e:e[1],reverse=True)
	trendWord = [x[0] for x in sortedWord[0:top_n_trend_word]]
	return trendWord	

def readPatentIDList(patentidfile):
	with open(patentidfile,'r') as f:
		PatentidList = [int(x) for x in f]
	return PatentidList

if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)
	parser.add_option('-t','--threshold',action = 'store',\
		type = 'float',dest = 'threshold',default = 0.02,\
		help = 'specify the threshold. if the tfidf vlue of a word in \
		one patent is smaller than the threshold, this patent will not belong to \
		the word trend')
	# parser.add_option('-k','--top_k_word',action = 'store',\
	# 	type = 'int',dest = 'top_k_word',default = 20,\
	# 	help = 'specify how many tfidf words can represent a patent.')

	options, args = parser.parse_args()
	if len(args) == 0:
		parser.print_help()
		sys.exit()
	# print args
	directory = './TFIDF_WordTrend'
	main(options, args)

