#!/usr/bin/python
# -*- encoding: utf8 -*-

__author__ = 'Leon'

from optparse import OptionParser
import csv, sys, logging, os, math
from trend_distribution_analysis import write_distribution,filter_By_Year,read_renew_file,filter_By_Number,addintoTrendDic,distribution2,store_dictionary
from with_in_trend_analysis import load_renewfile,load_dateFile,load_dictionary,renew_ratio,nth_renew_average
from scipy.stats.stats import pearsonr
from trendslope import load_trendFile,calculateSlope,drawTrend,correlation,correlation2,readPatentIDList,writefeature
csv.field_size_limit(sys.maxsize)

def main(options,args):
	'''\
	%prog [options]<renewfile> <datefile>  <citationFile> <patentidfile> <TrnedFile1> <TrnedFile2>...
	'''
	if not os.path.exists(directory):
		os.makedirs(directory)
	# input
	windowSize = options.windowSize
	renewfile = args[0]
	datefile = args[1]
	citationFile = args[2]
	patentidfile = args[3]
	trendFiles = args[4:]

	logging.info('reading Citation,id list, renew, Date information')
	Citation = load_dictionary(citationFile)
	patentidlist = readPatentIDList(patentidfile)
	RenewInfo = read_renew_file(renewfile)
	Date = load_dateFile(datefile)
	logging.info('finished reading')


	for trendFile in trendFiles:
		trendName = os.path.basename(trendFile)[:-4]
		subdirectory = os.path.join(directory,trendName)
		if not os.path.exists(subdirectory):
			os.makedirs(subdirectory)
		logging.info('----------------------------------')
		logging.info(os.path.basename(trendFile))
		Trend = load_trendFile(trendFile)
		# Trend = filter_By_Year(Trend,Date,1981,1998)
		# Trend = filter_By_Number(Trend,100)
		logging.info('number of qualified trend '+str(len(Trend)))

		# -----------------------------
		# trend connectivity
		logging.info('***trend connectivity***')
		trendconnectivity = calculate_connectivity(Trend,Citation)
		testDic(trendconnectivity,'trendConnectivity',1)
		# print out the average value of connectivity
		averageTrendAttribute(trendconnectivity,1,'connectivity')
		averageTrendAttribute(trendconnectivity,4,'InOverAllCitation')
		patentConnectivity = connectivityTrend2Patent(Trend,trendconnectivity,patentidlist)
		testDic(patentConnectivity,'patentConnectivity',1)
		# connectivityFeatureFile = './feature/connectivity_'+trendName+'.txt'
		connectivityFeatureFile = os.path.join(subdirectory,'connectivity.txt')
		# store_dictionary(trendconnectivity,'./feature/trend_connectivity_'+trendName+'.csv')
		store_dictionary(trendconnectivity,os.path.join(subdirectory,'trend_connectivity_'+trendName+'.csv'))
		writefeature(patentConnectivity,patentidlist,connectivityFeatureFile,5,'0')
		print 

		# -------------------------------
		# the trendslope feature
		# calculate the number of patents in all trend
		logging.info('***trend slope***')
		totall = 0
		for label, patentlist in Trend.iteritems():
			totall += len(patentlist)
		logging.info('number of toall patents,including duplicates: '+str(totall))
		TrendShpes = {}
		for label, patentlist in Trend.iteritems():
			Shape = drawTrend(patentlist,Date) 
			TrendShpes[label] = Shape
			# assume each patent in one trend
		Slope = calculateSlope(Trend,TrendShpes,Date,windowSize)
		testDic(Slope,'Slope',1)
		# slopeFeaturefile = './feature/slope_'+trendName+'.txt'
		slopeFeaturefile = os.path.join(subdirectory,'slope.txt')
		writefeature(Slope,patentidlist,slopeFeaturefile)
		print 

		# ---------------------------------
		# the position feature for each patent
		logging.info('***patent position***')
		Position = Position_feature(Trend,Date,patentidlist)
		testDic(Position,'Position',1)
		# featurefile = './feature/position_'+trendName+'.txt'
		positionfile = os.path.join(subdirectory,'position.txt')
		writefeature(Position,patentidlist,positionfile,3,'0')
		print

		# -----------------------------
		# the renew feature for each patent
		logging.info('***trend renew feature***')
		# renewfeaturefile = './feature/renew_percenage_'+trendName+'.txt'
		renewfeaturefile = os.path.join(subdirectory,'renew.txt')
		RenewFeature = Renew_feature(Trend,RenewInfo,patentidlist)
		testDic(RenewFeature,'RenewFeature',1)
		writefeature(RenewFeature,patentidlist,renewfeaturefile,10,'0')
	return 0



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
		numberOfPatent = float(len(patentlist))
		if numberOfPatent == 0:
			logging.info('trend %s have 0 patents' %trend)
			continue
		# if (InTrendCitation+outTrendCitation) == 0:
		# 	print patentlist
		# 	sys.exit()
		InOverAllCitation=(float(InTrendCitation)/(InTrendCitation+outTrendCitation)) if (InTrendCitation+outTrendCitation)!=0 else 0
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
	miss = 0
	for patent, connectivitylist in Connectivity4patent.iteritems():
		if len(connectivitylist) == 1:
			Connectivity4patent[patent] = connectivitylist[0]
			continue
		elif len(connectivitylist) == 0:
			miss += 1
		else:
			groupFeatures = zip(*connectivitylist)
			patentconnectivity = [sum(x)/float(len(x)) for x in groupFeatures]
			Connectivity4patent[patent] = patentconnectivity
	if miss:
		logging.warning('%s patents do not have connectivity feature possible because they do not belong to any trends'%miss)
	logging.info('finished connectivity which has %s patents'%(len(Connectivity4patent)))
	return Connectivity4patent


def testDic(Dic,name = 'Nonename',n = 20):
	logging.info('Dictionary %s (%s elements) %s examples:'%(name,len(Dic),n)) 
	for i,key in enumerate(Dic):
		logging.info('\t%s: %s'%(key, Dic[key]))
		if i == n-1:
			break
def averageTrendAttribute(TrendDic,attributeIndex,featureName):
	'given a dictionary of {trend : [trend features]}, calculate the average of features specified by attributeIndex'
	trendAttributeList = [x[attributeIndex] for trend,x in TrendDic.iteritems()]
	average = sum(trendAttributeList)/float(len(trendAttributeList))
	logging.info('The average value of all trends %s is %s'%(featureName,average))
def Position_feature(TrendDic, DateDic, patentidlist):
	'''for each trend, sort the patent
		calculate the numberOfPatentInTrend, Before, Position for each patent 
		append the feature into each patent 
		average the patent feature if one patent belong to multiple trends
	'''
	PositionDic = {patent:[] for patent in patentidlist}
	for Trend in TrendDic:
		patentsInATrend = TrendDic[Trend]

		patentDatePairs = []
		for patent in patentsInATrend:
			try:
				patentDatePairs.append((patent,DateDic[patent]))
			except KeyError:
				logging.info('patent %s do not have date information'%patent)
				continue

		patentDatePairs = sorted(patentDatePairs,key = lambda e:e[1])# a sorted trend
		for index,(patent,date) in enumerate(patentDatePairs):
			numberOfPatentInTrend = len(patentDatePairs)
			before = index+1
			position = float(before)/numberOfPatentInTrend
			try:
				PositionDic[patent].append([numberOfPatentInTrend,before,position])
			except KeyError:
				logging.info('patent %s from trend file not in patent id list' %patent)
				continue
	# do the average for each patent since one patent may belong to multiple trends
	miss = 0
	for patent, featurelist in PositionDic.iteritems():
		if len(featurelist) > 1:
			threefeaturelist = zip(*featurelist) # three lists in threefeaturelist are number, before, and position list
			numberofTrends = float(len(featurelist))
			averageNumber = sum(threefeaturelist[0])/numberofTrends
			averageBefore = sum(threefeaturelist[1])/numberofTrends
			averagePosition = sum(threefeaturelist[2])/numberofTrends

			PositionDic[patent] = [averageNumber,averageBefore,averagePosition]
		elif len(featurelist) == 1:
			PositionDic[patent] = featurelist[0]
		else:
			miss += 1
	logging.warning('%s patent has no position feature, possible because they do not belong to any trend'%miss)
	return PositionDic
def Renew_feature(TrendDic,RenewDic,patentidlist):
	'''calculate the renew percentage for '0','1','2' and '3' in every trend, and assign the \
		trend feature into each patent
		Firstly, for each trend, calculate the renew percentage.
		patents never renewed contains all with label 0
		patents has renewed at least once contains all with label 3, 2 and 1.
		patents has renewed at least twice contains all with label 3, 2.
		patents has renewed at least three times contains all with label 3
		for each patent assign the renew feture to them
		for each patent average the feature if one patent belong to multiple trends
	'''
	RenewFeature = {patent:[] for patent in patentidlist}
	for trend in TrendDic:
		patentsInATrend = TrendDic[trend]
		x = 0 # number of all valid patent in the trend
		x0 = 0  # number of patents that didn't renewed onece
		x1 = 0
		x2 = 0
		x3 = 0
		for patent in TrendDic[trend]:
			try:
				re = RenewDic[patent]
				x += 1
				if re == '0':
					x0 += 1
				elif re == '1':
					x1 += 1
				elif re == '2':
					x2 += 1
				elif re == '3':
					x3 += 1
				else:
					logging.info( '%s not 0,1,2,3 in patent status for patent %s in cluster %s'\
						  %(re, patent, trend))
			except KeyError:
				logging.info('patent %s not in renew file'%(patent))
				continue
		zero_ = x0
		one_ = x1+x2+x3
		two_ = x2+x3
		three_ = x3
		ave_ = x0+2*x1+3*x2+4*x3
		zero = float(zero_)/x
		one = float(one_)/x
		two = float(two_)/x
		three = float(three_)/x
		ave = float(ave_)/x
		lack = 0
		for patent in TrendDic[trend]:
			try:
				RenewFeature[patent].append([zero_,one_,two_,three_,ave_,zero,one,two,three,ave])
			except KeyError:
				lack += 1
				continue
		if lack:
			logging.info('%s patent from trend file not in patent id list' %lack)
	# do the average for renew feature if one patent belong to multiple trends
	miss = 0
	for patent,featurelist in RenewFeature.iteritems():
		if len(featurelist) > 1:
			numberofTrends = float(len(featurelist))
			tenfeaturelist = zip(*featurelist)
			feature = [sum(x)/numberofTrends for x in tenfeaturelist]
			RenewFeature[patent] = feature
		elif len(featurelist) == 1:
			RenewFeature[patent] = featurelist[0]
		else:
			miss += 1
			continue
	if miss:
		logging.warning(' %s patent have do not belong to any trend'%miss)
	return RenewFeature

def addIntoDic(key,val, dic):
		if key in dic:
				dic[key].append(val)
		else:
				dic[key]=[val]
def average(Dic):
	for patent in Dic:
		s = 0
		l = len(Dic[patent])
		for val in range(0,l):
			s = s + Dic[patent][val]
		s = float(s)/l
		Dic[patent] = s
if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)

	parser.add_option('-w','--window',action = 'store',\
		type = 'int',dest = 'windowSize',default = 10,\
		help = 'specify the window size ')

	options,args = parser.parse_args()

	if len(args) < 4:
	  print 'arguments are the <citationFile> <patentidfile> <TrnedFile1> <TrnedFile2>...'
	  sys.exit()
	directory = './feature'
	logging.basicConfig(filename = os.path.join(directory,'featurelog.txt'),format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	if 0==main(options,args):
	# print 'finished',__file__
		logging.info('finished %s'%__file__)