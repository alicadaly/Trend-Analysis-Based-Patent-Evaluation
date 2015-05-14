
#!/usr/bin/python
# -*- encoding: utf8 -*-

# based on the lda value, filter out all value that is below than threshold \alpha.
# based on the rest of tipic value, group all the patents under one topic as a trend.
from optparse import OptionParser
from gensim import corpora, models, similarities,matutils
import csv, sys, logging, os


__author__ = 'Leon'


def main(options,args):
	'''\
	%prog [options] <ldaValueFile> <patentidfile>
	'''
	ldaValueFile, patentidfile = args
	threshold = options.threshold
	topic_number = options.topic_number



	# load the readPatentidList
	PatentidList = readPatentIDList(patentidfile)
	logging.info('patent id list has %s patents'%len(PatentidList))
	
	# load the popular word id list
	# TrendWordList = TopicWord(ldaValueFile,number_trendtopic, options.top_k_topic)
	# print '%s trend wrod' %(len(TrendWordList))

	# initailize a dictionary to store all trend number and their patent number
	Trend = {}
	TopicFrequency = {}
	# for topic in TrendWordList:
	# 	Dic[topic] = []
	with open(ldaValueFile,'r') as f:
		reader = csv.reader(f)
		for i,line in enumerate(reader):
			patent = map(eval,line)
			patent = [topic for (topic,weight) in patent if weight>threshold]
			try:
				for topic in patent:
					if topic not in Trend:
						Trend[topic] = [PatentidList[i]]
					else:
						Trend[topic].append(PatentidList[i])
					addIntoDic(topic,TopicFrequency)
			except IndexError:
				logging.info('ldaValueFile is bigger than patent id list')
				break
			last = i
		if last < len(PatentidList)-1:
			logging.info('ldaValueFile is smaller than patent id file')
			logging.info('ldaValueFile has %s patents'%(last+1))



	with open(directory+'/'+str(len(Trend))+'TopicTrend.csv','w') as writefile:
		writer = csv.writer(writefile)
		for topic in Trend:
			line = [topic]
			line.extend(Trend[topic])
			writer.writerow(line)
	TopicFrequencyList = sorted(TopicFrequency.items(),key = lambda e:e[1],reverse = True)
	logging.info('The top topics and frequency %s'%str(TopicFrequencyList)) 
# record the frequency of topic
def addIntoDic ( key, myDict ):
	if key in myDict:
		myDict[key] += 1
	else:
		myDict[key] = 1
	return

# def TopicWord(lda_value_file, top_n_trend_topic, top_k_topic):
# 	# the dictionary contain all topic
# 	Dic = {}
# 	infile = file(lda_value_file,'r')
# 	reader = csv.reader(infile,delimiter=',')
# 	n = 1
# 	for line in reader:
# 		patent = map(eval,line)
# 		sortedpatent = sorted(patent, key = lambda x:x[1],reverse = True)
# 		y = len(sortedpatent)
# 		# print y
# 		x = 1
# 		while(x < y):
# 			# indicate to choose the top k key word
# 			if x > top_k_topic:
# 				break
# 			addIntoDic(sortedpatent[x][0],Dic)
# 			x += 1
# 		# n += 1
# 		# if n > 3:
# 		# 	break
# 	infile.close()
# 	sortedWord = sorted(Dic.iteritems(), key=lambda e:e[1],reverse=True)
# 	trendWord = [x[0] for x in sortedWord[0:top_n_trend_topic]]
# 	return trendWord

def readPatentIDList(patentidfile):
	with open(patentidfile,'r') as f:
		PatentidList = [int(x) for x in f]
	return PatentidList

if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)
	parser.add_option('-t','--threshold',action = 'store',\
		type = 'float',dest = 'threshold',default = 0.01,\
		help = 'specify the threshold. if the lda value of a topic in \
		one patent is smaller than the threshold, this patent will not belong to \
		the topic trend')
	parser.add_option('-k','--topic_number',action = 'store',\
		type = 'int',dest = 'topic_number',default = None,\
		help = 'specify how many lda topic in the lda value file.')

	options, args = parser.parse_args()

	if not options.topic_number:
		logging.info('use -k to specify the number of topic in lda value file')
		sys.exit()
	if len(args) == 0:
		parser.print_help()
		sys.exit()
	# print args
	directory = './LDA_TopicTrend'
	# create a new directory for all data 
	if not os.path.exists(directory):
		os.makedirs(directory)
	logging.basicConfig(filename= './LDA_TopicTrend/LDA_TopicTrend'+str(options.topic_number)+'log.txt',format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	main(options, args)
	logging.info('finished LDA_TopicTrend.py')