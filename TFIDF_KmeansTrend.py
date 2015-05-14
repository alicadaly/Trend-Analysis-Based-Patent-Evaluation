# this code do the Kmeans for the tfidf vector

from sklearn.cluster import KMeans
from optparse import OptionParser
from gensim import corpora, models, similarities,matutils
import csv, sys, logging, os
csv.field_size_limit(sys.maxsize)


def main(options,args): # 'the arguments are dictionary file, corpus file tfidfmodel and raw data'G
	'''\
	%prog [options] <dictionary file> <corpus file> <tfidfmodel>  <patentidfile>
	'''
	

	labels = Kmeans(options.trend_number,args)
	patentlist = readPatentIDList(args[3])
	# initialize a list of list to put patent id in corresponding label list
	trends = [[] for i in range(0,options.trend_number)]
	for label,patent in zip(labels,patentlist):
		trends[label].append(patent)
	# write the trend list into a csv file
	writefile = open(directory+'/TFIDF_KmeansTrend'+str(options.trend_number)+'.csv','w')
	writer = csv.writer(writefile)
	trendIndex = 0
	for trend in trends:
		line = [trendIndex]
		line.extend(trend)
		writer.writerow(line)
		trendIndex += 1
	writefile.close()
# def patentID(rawdata):
# 	readfile = open(rawdata,'r')
# 	reader = csv.reader(readfile, delimiter = '\t')
# 	patentlist = []
# 	for line in reader:
# 		patentlist.append(line[0])
# 	return patentlist
def readPatentIDList(patentidfile):
	with open(patentidfile,'r') as f:
		PatentidList = [int(x) for x in f]
	return PatentidList

def Kmeans(n_clusters,args):
	corpus = corpora.MmCorpus(args[1])
	tfidf = models.tfidfmodel.TfidfModel.load(args[2])
	logging.info('finished loading corpus and tfidf models')

	# load the dictionary and corpus
	dictionary = corpora.Dictionary.load(args[0])
	tfidfValue = tfidf[corpus]
	logging.info('finished tfidfValue = tfidf[corpus]')

	fitdata = matutils.corpus2csc(tfidfValue, num_terms=len(dictionary) , dtype='float32', num_docs=len(tfidfValue), num_nnz=None, printprogress=0).transpose()
	logging.info('finished transfer tfidf vector to sparse vector and transpose sparse vector')

	logging.info('begin kmeans fit')
	#TODO refactor parameters
	km = KMeans(n_clusters = n_clusters, init='random', max_iter=100, n_init=5, verbose=1)
	km.fit(fitdata)
	logging.info('finished kmeans fit')
	# l = open('./TFIDF_KmeansTrend.txt','w')
	# for label in km.labels_:
	# 	l.write(str(label)+'\n')
	# l.close()
	return km.labels_


if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)
	parser.add_option('-n','--numberOfTrends',action = 'store',\
		type = 'int',dest = 'trend_number',default = 10,\
		help = 'specify the number of cluster ')
	options,args = parser.parse_args()

	if len(args) <3:
		parser.print_help()
		print 'the arguments are dictionary file, corpus file tfidfmodel and patent id file'
		sys.exit()

	directory = './TFIDF_Kmeans'
	# create a new directory for all data 
	if not os.path.exists(directory):
		os.makedirs(directory)

	logging.basicConfig(filename= './TFIDF_Kmeans/Word_Cluster'+str(options.trend_number)+'log.txt',format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	main(options,args)
	logging.info('finished tfidfKmeans.py')
