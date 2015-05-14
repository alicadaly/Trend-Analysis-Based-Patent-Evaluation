#!/usr/bin/python
# -*- encoding: utf8 -*-

__author__ = 'Leon'

from optparse import OptionParser
import csv, sys, logging, os, math
from trend_distribution_analysis import write_distribution,filter_By_Year,read_renew_file,filter_By_Number,addintoTrendDic,distribution2,store_dictionary
from with_in_trend_analysis import load_renewfile,load_dateFile,load_dictionary,renew_ratio,nth_renew_average
from scipy.stats.stats import pearsonr
from trendslope import load_trendFile,writefeature
csv.field_size_limit(sys.maxsize)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def main(options,args):
	'''\
	%prog [options] <citationFile> <patentidfile> <TrnedFile1> <TrnedFile2>...
	'''
	if not os.path.exists(directory):
		os.makedirs(directory)
	citationFile = args[0]
	patentidfile = args[1]
	trendFiles = args[2:]

	Citation = load_dictionary(citationFile)
	patentidlist = readPatentIDList(patentidfile)

	for trendFile in trendFiles:
		logging.info(os.path.basename(trendFile))
		Trend = load_trendFile(trendFile)
		# Trend = filter_By_Year(Trend,Date,1981,1998)
		# Trend = filter_By_Number(Trend,100)
		logging.info( 'number of qualified trend '+str(len(Trend)))
		trendconnectivity = calculate_connectivity(Trend,Citation)
		testDic(trendconnectivity,'trendConnectivity',1)
		# print out the average value of connectivity
		averageTrendAttribute(trendconnectivity,1,'connectivity')
		averageTrendAttribute(trendconnectivity,4,'InOverAllCitation')
		
		patentConnectivity = connectivityTrend2Patent(Trend,trendconnectivity,patentidlist)
		# testDic(patentConnectivity,'patentConnectivity')
		# the name of feature file
		name = trendFile.strip('./').rstrip('.csv')[:-5]
		if not os.path.exists('./feature'):
			os.makedirs('./feature')
		if 'LDA_Kmeans' in trendFile:
			name = 'LDA_Kmeans'
		elif 'Topic' in trendFile:
			name = 'Topic'
		elif 'TFIDF_Kmeans' in trendFile:
			name = 'TFIDF_Kmeans'
		elif 'Word' in trendFile:
			name = 'Word'

		featurefile = './feature/connectivity_feature_'+name+'.txt'
		store_dictionary(trendconnectivity,'./feature/trend_connectivity_dic.csv')
		writefeature(patentConnectivity,patentidlist,featurefile,5,'0')
		print '\n'
	return 0


def readPatentIDList(patentidfile):
	with open(patentidfile,'r') as f:
		PatentidList = [x.strip() for x in f]
	return PatentidList
def calculate_connectivity(TrendDic,CitationDic):
	Connectivity4trend = {} #{trend:connectivity}
	InOverAllCitation = []
	for trend,patentlist in TrendDic.iteritems():
		currentpatents = set(patentlist)
		InTrendCitation = 0
		outTrendCitation = 0
		for patent in patentlist:
			for citedPatent in CitationDic[patent]:
				if citedPatent in currentpatents:
					InTrendCitation += 1
				else:
					outTrendCitation += 1
		numberOfPatent = len(patentlist)
		if numberOfPatent == 0:
			logging.info('trend %s have 0 patents' %trend)
			continue
		InOverAllCitation=(float(InTrendCitation)/(InTrendCitation+outTrendCitation))
		connectivity = float(InTrendCitation)/(numberOfPatent**2/2)
		outconnectivity = float(outTrendCitation)/(numberOfPatent**2/2)
		Connectivity4trend[trend] = [InTrendCitation,connectivity,outTrendCitation,outconnectivity,InOverAllCitation]
	# testDic(Connectivity4trend,'connectivity')
	return Connectivity4trend
def connectivityTrend2Patent(Trend,trendConnectivity,patentlist):
	'''given a dictionary trendConnectivity {trend: connectivity},
		output the dictionary for patent connectivity {patent,connectivity}
		handle the case that a patent in different trend'''
	Connectivity4patent = {} #{patent:connectivity}
	for trend, patentlist in Trend.iteritems():
		connectivity = trendConnectivity[trend]
		for patent in patentlist:
			addintoTrendDic(connectivity,patent,Connectivity4patent)
	for patent, connectivitylist in Connectivity4patent.iteritems():
		if len(connectivitylist) == 1:
			Connectivity4patent[patent] = connectivitylist[0]
			continue
		else:
			patentconnectivity = []
			for i in range(len(connectivitylist[0])):
				# try:
				conn = [x for x in zip(*connectivitylist)[i] if x]
				# except TypeError:
				# 	print zip(*connectivitylist)
				# 	print zip(*connectivitylist)[i][0]
				# 	sys.exit()
				conn = None if len(conn) == 0 else sum(conn)/float(len(conn))
				if conn == None:
					print 'connectivity list do not have same length'
				patentconnectivity.append(conn)
			Connectivity4patent[patent] = patentconnectivity
	logging.info('finished connectivity which has %s patents'%(len(Connectivity4patent)))
	return Connectivity4patent


def testDic(Dic,name = 'Nonename',n = 20):
	logging.info('Dictionary %s (%s elements) %s examples:'%(name,len(Dic),n)) 
	for i,key in enumerate(Dic):
		logging.info('\t%s%s'%(key, Dic[key]))
		if i == n-1:
			break
def averageTrendAttribute(TrendDic,attributeIndex,featureName):
	'given a dictionary of {trend : [trend features]}, calculate the average of features specified by attributeIndex'
	trendAttributeList = [x[1] for trend,x in TrendDic.iteritems()]
	average = sum(trendAttributeList)/float(len(trendAttributeList))
	logging.info('The average value of all trends %s is %s'%(featureName,average))

if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)

	# parser.add_option('-n','--******',action = 'store',\
	# 	type = 'int',dest = '******',default = 10,\
	# 	help = '*********')

	options,args = parser.parse_args()

	if len(args) < 3:
	  print 'arguments are the <citationFile> <patentidfile> <TrnedFile1> <TrnedFile2>...'
	  sys.exit()
	directory = './feature'
	if 0==main(options,args):
	# print 'finished',__file__
		logging.info('finished %s'%__file__)