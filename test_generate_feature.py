#!/usr/bin/python
# -*- encoding: utf8 -*-

__author__ = 'Leon'
from random import randint
# from generate_feature import Position_feature,Renew_feature,testDic
from generate_feature import testDic,addIntoDic,average
from optparse import OptionParser
import csv, sys, logging, os, math
from trend_distribution_analysis import write_distribution,filter_By_Year,read_renew_file,filter_By_Number,addintoTrendDic,distribution2,store_dictionary
from with_in_trend_analysis import load_renewfile,load_dateFile,load_dictionary,renew_ratio,nth_renew_average
from scipy.stats.stats import pearsonr
from trendslope import load_trendFile,calculateSlope,drawTrend,correlation,correlation2,readPatentIDList,writefeature
csv.field_size_limit(sys.maxsize)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def main(options,args):
	'''\
	%prog [options]<renewfile> <datefile>  <citationFile> <patentidfile> <TrnedFile1> <TrnedFile2>...
	'''

	# if not os.path.exists(directory):
	# 	os.makedirs(directory)
	# patentidfile = '/Users/Leon/Documents/Research/Code/TrendCode/testdata/patent_id_list.txt'
	# patentidlist = readPatentIDList(patentidfile)
	# # random renew information based on pa
	# RenewInfo = {patent:str(randint(0,3)) for patent in patentidlist}
	# # testDic(RenewInfo,'renew dictionary')
	# # random date information
	# Date = {patent:randint(0,1000) for patent in patentidlist}
	# # testDic(Date,'date dictionary')

	# trendFile = '/Users/Leon/Documents/Research/Code/TrendCode/testdata/LDA_TopicTrend/20TopicTrend.csv'
	# Trend = load_trendFile(trendFile)
	# logging.info(os.path.basename(trendFile))
	# logging.info( 'number of qualified trend '+str(len(Trend)))
	# name = os.path.basename(trendFile)[:-4]+'test'
	# # Renew_feature(Trend,RenewInfo,patentidlist,name)
	# Position_feature(Trend,Date,RenewInfo,patentidlist,name)
	# # -------------------

	# test
	patentidlist = [str(i) for i in range(10)]
	Renew = {'1': '2', '0': '3', '3': '1', '2': '2', '5': '0', '4': '3', '7': '2', '6': '1', '9': '3', '8': '3'}
	Date = {'1': 123, '0': 401, '3': 542, '2': 423, '5': 338, '4': 492, '7': 484, '6': 356, '9': 451, '8': 242}
	Trend = {'0':['0','1','2','3','4'],
			'1':['5','6','7','8','9'],
			'2':['3','7','9']}
	trendName = 'test'
	Citation = {'1':['2','3','6','8'],
				'2':['5','6','9'],
				'3':['9'],
				'4':['8'],
				'5':[],
				'7':['11'],
				'8':['7'],
				'9':[]}

	# Position = Position_feature(Trend,Date,patentidlist)
	# featurefile = './feature/position_'+trendName+'.csv'
	# writefeature(Position,patentidlist,featurefile,3,'0')
	# renewfeaturefile = './feature/renew_percenage_'+trendName+'.csv'
	# RenewFeature = Renew_feature(Trend,Renew,patentidlist)
	# writefeature(RenewFeature,patentidlist,renewfeaturefile,10,'0')
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
	connectivityFeatureFile = './feature/connectivity_'+trendName+'.txt'
	store_dictionary(trendconnectivity,'./feature/trend_connectivity_'+trendName+'.csv')
	writefeature(patentConnectivity,patentidlist,connectivityFeatureFile,5,'0')
	print 
	# -------------------------------
def calculate_connectivity(TrendDic,CitationDic):
	Connectivity4trend = {} #{trend:connectivity}
	InOverAllCitation = []
	missCitation = 0
	for trend,patentlist in TrendDic.iteritems():
		currentpatents = set(patentlist)
		InTrendCitation = 0
		outTrendCitation = 0
		for patent in patentlist:
			if CitationDic.get(patent):
				for citedPatent in CitationDic[patent]:
					if citedPatent in currentpatents:
						InTrendCitation += 1
					else:
						outTrendCitation += 1
			else:
				missCitation += 1

		numberOfPatent = float(len(patentlist))
		if numberOfPatent == 0:
			logging.info('trend %s have 0 patents' %trend)
			continue
		InOverAllCitation=(float(InTrendCitation)/(InTrendCitation+outTrendCitation))
		connectivity = float(InTrendCitation)/(numberOfPatent**2/2)
		outconnectivity = float(outTrendCitation)/(numberOfPatent**2/2)
		Connectivity4trend[trend] = [InTrendCitation,connectivity,outTrendCitation,outconnectivity,InOverAllCitation]
	# testDic(Connectivity4trend,'connectivity')
	logging.warning('%s patents lack citation information'%missCitation)
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
			patentconnectivity = []
			for i in range(len(connectivitylist[0])):
				# try:
				conn = [x for x in zip(*connectivitylist)[i] if x]
				# except TypeError:
				# 	print zip(*connectivitylist)
				# 	print zip(*connectivitylist)[i][0]
				# 	sys.exit()
				
				if len(conn) == 0:
					print 'connectivity list is zero'
					
				conn = 0 if len(conn) == 0 else sum(conn)/float(len(conn))
				patentconnectivity.append(conn)
			Connectivity4patent[patent] = patentconnectivity
	logging.warning('%s patents do not have connectivity feature possible because they do not belong to any trends'%miss)
	logging.info('finished connectivity which has %s patents'%(len(Connectivity4patent)))
	return Connectivity4patent

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
	for patent, featurelist in PositionDic.items():
		if len(featurelist) > 1:
			threefeaturelist = zip(*featurelist) # three lists in threefeaturelist are number, before, and position list
			numberofTrends = float(len(featurelist))
			averageNumber = sum(threefeaturelist[0])/numberofTrends
			averageBefore = sum(threefeaturelist[1])/numberofTrends
			averagePosition = sum(threefeaturelist[2])/numberofTrends

			PositionDic[patent] = [averageNumber,averageBefore,averagePosition]
		else:
			PositionDic[patent] = featurelist[0]
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
		for patent in TrendDic[trend]:
			try:
				RenewFeature[patent].append([zero_,one_,two_,three_,ave_,zero,one,two,three,ave])
			except KeyError:
				logging.info('patent %s from trend file not in patent id list' %patent)
				continue
	# do the average for renew feature if one patent belong to multiple trends
	for patent,featurelist in RenewFeature.items():
		if len(featurelist) > 1:
			numberofTrends = float(len(featurelist))
			tenfeaturelist = zip(*featurelist)
			feature = [sum(x)/numberofTrends for x in tenfeaturelist]
			RenewFeature[patent] = feature
		elif len(featurelist) == 1:
			RenewFeature[patent] = featurelist[0]
		else:
			logging.info('patent %s have do not belong to any trend'%patent)
			continue
	return RenewFeature


if __name__ == '__main__':
	parser = OptionParser(usage=main.__doc__)

	parser.add_option('-n','--******',action = 'store',\
		type = 'int',dest = '******',default = 10,\
		help = '*********')

	options,args = parser.parse_args()

	# if len(args) < 3:
	# 	print 'arguments are the trend file, date file original data, renewfile'
	# 	sys.exit()
	directory = './feature'
	a = 1
	main(options,args)
	logging.info('finished %s' %__file__)