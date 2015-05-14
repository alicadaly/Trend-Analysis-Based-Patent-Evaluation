# given the parsed text(words are sperated by space) -d data
# parse it into a dictionary(dict) and vector document(mm)
# you can specify the parameter of dictionary compact.


import csv,sys, logging, os, re
from optparse import OptionParser
from porter import stem
from gensim import corpora, models, similarities
csv.field_size_limit(sys.maxsize)

def main(options, args):
	'''\
	%prog [options] <stopwordfile> <raw data>
	'''
	# the input raw data
	data = args[1]
	stopwordlist = args[0]
	
	# create a new deirectory for all data 
	if not os.path.exists(directory):
		os.makedirs(directory)
	# extractPatentID(data)
	if not options.ParsedData and not options.dictionary:
		ParsedData = ParseRawData(data,stopwordlist)
	else:
		if options.ParsedData:
			ParsedData = options.ParsedData

	if options.dictionary == 'None':
		# parse data into dictionary
		Dic = PatentData2Dic(ParsedData)
	else:
		# load the dictionary
		Dic = corpora.Dictionary.load(options.dictionary)

	Dic = DicCompact(Dic,options.no_below,options.no_above,options.keep_n)

	if not options.corpus:
		corpus = Patent2Corpus(Dic,ParsedData)
	else:
		corpus = corpora.MmCorpus(options.corpus)

	if options.dotfidf:
		tfidf = TFIDF(corpus)
	if options.savetfidfValue:
		saveTFIDF_Value(tfidf)

	if options.dolda:
		lda, ldaValue = LDA(corpus, options.n_topics, Dic, options.passes)
	if options.saveldaValue:
		saveLDA_Value(ldaValue,options.n_topics)
		saveTopics(lda,options.n_topics)
	logging.info('finished TFIDF_LDA.py')

	# logging.info('parsing data from %s into dictionary') %options.data
	# dictionary = corpora.Dictionary(line.split() for line in open(options.data))
	# dictionary.save()
def extractPatentID(rawdata):
	readfile = open(rawdata,'r')
	reader = csv.reader(readfile,delimiter = '\t')
	writefile = open(directory+'/patent_id_list.txt','w')
	for line in reader:
		writefile.write(str(line[0])+'\n')
	readfile.close()
	writefile.close()
def cleanTokenizeText ( text ):
	lowerText = text.lower()
	cleanText = re.sub('[^A-Za-z\n ]+', '', lowerText)
	wordList = re.split('\W+', cleanText)
	return wordList

def ParseRawData(data,stopWordFile=[]):
	'''do tokenize, stemming, remove stop word
		return the parsed file name
	'''
	logging.info('begin parse raw data')
	parsedDatafile = 'parsedPatent.txt'
	path = os.path.join(directory, parsedDatafile)
	writefile = open(path,'w')
	# open stop word file
	stopwordlist = [word for word in open(stopWordFile).read().split(',')]
	for line in open(data,'r'):
		stemmed_line =[stem(word) for word in cleanTokenizeText(line)]
		nostop_word_list = [word for word in stemmed_line if word not in stopwordlist]
		writefile.write(' '.join(nostop_word_list)+'\n')
	writefile.close()
	logging.info('finished parsing, store the parsed file into ./TFIDF_LDA/parsedPatent.txt')	
	return path


def PatentData2Dic(parseddata):
	dictionary = corpora.Dictionary(line.split() for line in open(os.path.join(directory, parseddata)))
	# logging.info('parsing data from %s into dictionary') %(str(options.data))
	logging.info(dictionary) 
	return dictionary
def DicCompact(dictionary,no_below,no_above,keep_n):
	# remove stop words and words that appear only once
	# once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
	# dictionary.filter_tokens(once_ids) # remove stop words and words that appear only once
	dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
	dictionary.compactify() # remove gaps in id sequence after words that were removed
	# store the dictionary, for future reference
	dictionary.save(directory+'/dict.dict')
	dictionary.save_as_text(directory+'/dict.txt',sort_by_word=False)
	return dictionary
def Patent2Corpus(dictionary, data):
	class MyCorpus(object):
		def __iter__(self):
			for line in open(data):
				# assume there's one document per line, tokens separated by whitespace
				yield dictionary.doc2bow(line[8:].split())
	corpus_memory_fiendly = MyCorpus()
	corpora.MmCorpus.serialize(directory+'/corpus_noB_'+str(options.no_below)+'_noA_'+str(options.no_above)+'.mm', corpus_memory_fiendly)
	return corpus_memory_fiendly
def TFIDF(corpus):
	# initialize the tf-idf model
	tfidf = models.TfidfModel(corpus,normalize=True)
	# train the corpus
	tfidfValue = tfidf[corpus]
	tfidf.save(directory+'/tfidf.model')
	return tfidfValue
def LDA(corpus,n_topics,dictionary,passes):
	lda = models.ldamulticore.LdaMulticore(corpus,num_topics = n_topics,id2word=dictionary,workers=3, passes = passes )
	lda.save(directory+'/lda_'+str(n_topics)+'.model')
	ldaValue = lda[corpus]
	return lda, ldaValue

def saveTFIDF_Value(tfidfValue):

	writefile = open(directory+'/tfidf_value.csv','w')
	writer = csv.writer(writefile)
	for document in tfidfValue:
		writer.writerow(document)
	writefile.close()

def saveLDA_Value(ldaValue,num_topics):
	name = str(num_topics)+'topics_lda_value.csv'
	writefile = open(os.path.join(directory,name),'w')
	writer = csv.writer(writefile)
	for document in ldaValue:
		writer.writerow(document)
	writefile.close()	

def saveTopics(lda,num_topics):
	name = str(num_topics)+'topics_lda_topics.csv'
	writefile = open(os.path.join(directory,name),'w')
	writer = csv.writer(writefile)
	for topic in lda.show_topics(num_words=100, log=False, formatted=False):
		writer.writerow(topic)
	writefile.close()
 
if __name__ == '__main__':
	parser = OptionParser()

	# specify the name of dictionary
	parser.add_option('-d','--dictionary', action = 'store',\
		type= 'string',dest='dictionary',default = None,\
		help = 'if you already have a dictionary,specify that')
	# specify the path and name of corpus
	parser.add_option('-c','--corpus', action = 'store',\
		type= 'string',dest='corpus',default = None,\
		help = 'if you already have a corpus,specify that')
	# specify the path and name of parsed data
	parser.add_option('-a','--parsed', action = 'store',\
		type= 'string',dest='ParsedData',default = None,\
		help = 'if you already have a corpus,specify that')
	
	# specify whether do tfidf
	parser.add_option("-t", "--tfidf",\
				  action="store_true", dest="dotfidf", default=False,\
				  help="if '-t' is on, calculate the tfidf value")

	# specify whether to save the the value of tfidf
	parser.add_option("-s", "--saveTFIDF",
				  action="store_true", dest="savetfidfValue", default=False,
				  help="if '-s' is on, save the the value of tfidf")

	# specify whether do lda
	parser.add_option("-l", "--lda",
				  action="store_true", dest="dolda", default=False,
				  help="if '-l' is on, calculate the lda value")
	# specify the number of topics in lda
	parser.add_option("-n", "--topics",
				  action="store", type = 'int', dest="n_topics", default=20, 
				  help="specify the number of topics in lda")
	# specify the number of passes in lda
	parser.add_option("-p", "--passes",
				  action="store", dest="passes", default=1,type = 'int',
				  help="specify the number of passes in lda")

	# specify whether to record the the value of lda
	parser.add_option("-r", "--recordLDA",
				  action="store_true", dest="saveldaValue", default=False,
				  help="if '-r' is on, save the the value of tfidf")

	# specify 3 arguments of compact dictionary
	# 1.less than no_below documents (absolute number) or
	parser.add_option('-1','--no_below',action = 'store',\
		type = 'int',dest = 'no_below',default = 0,\
		help = 'less than no_below documents (absolute number)')
	# 2.more than no_above documents (fraction of total corpus size, not absolute number).
	parser.add_option('-2','--no_above',action = 'store',\
		type = 'float',dest = 'no_above',default = 1.0,\
		help = 'more than no_above documents (fraction of total corpus size, not absolute number')
	# 3.after (1) and (2), keep only the first keep_n most frequent tokens (or keep all if None).
	parser.add_option('-3','--keep_n',action = 'store',\
		type = 'int',dest = 'keep_n',default = None,\
		help = 'keep only the first keep_n most frequent tokens (or keep all if None)')


	options,args = parser.parse_args()
	if len(args) <= 1:
		parser.print_help()
		sys.exit()
	logging.basicConfig(filename= './LDA'+str(options.n_topics)+'log.txt',format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

	# option is an instance
	# argument is an list
	directory = './LDA_'+str(options.n_topics)
	main(options,args)
