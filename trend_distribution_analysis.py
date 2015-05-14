#!/usr/bin/python
# -*- encoding: utf8 -*-
# input trend position feature or renew feature or trend
# output the distribution of different trend porperty
# size, trend value, trend connectivity

import csv,sys,os,math
from scipy.stats.stats import pearsonr

csv.field_size_limit(sys.maxsize)

__author__ = 'Leon'

def main():
	# input
	renewfile = '/Users/Leon/Documents/Research/Data/USPCMainAssg1981_2006Drug'
	RenewInfo = read_renew_file(renewfile)

	patentfile = '/Users/Leon/Documents/Research/Data/DrugPatent.csv'
	print 'begin to read citation file'
	# Citation = read_citation(patentfile)
	citationFile = '/Users/Leon/Documents/Research/Data/citation.csv'
	
	Citation = load_dictionary(citationFile)
	datefile = '/Users/Leon/Documents/Research/Data/grantDate'
	Date = load_dateFile(datefile)
	directory = './topic_cluster'
	# directory = './USclass'
	filenames = [x for x in os.listdir(directory) if '30Trend' in x]
	for filename in filenames:
		cluster_number = ''.join([x for x in filename if x.isdigit()])
		distributionfile = './data_analysis/topic_cluster/'+cluster_number+'trends_size_value_connectivity.csv'
		print filename
		Trend = load_dictionary(directory+'/'+filename)
		Trend = filter_By_Year(Trend,Date,1981,1998)
		Trend = filter_By_Number(Trend,100)
		print 'number of qualified trend ',len(Trend)
		# calculate the number of patents in all trend
		totall = 0
		for label, patentlist in Trend.items():
			totall += len(patentlist)
		write_distribution(['number of toall patents '+str(totall)],distributionfile)
		write_distribution(['number of toall trends '+str(len(Trend))],distributionfile)
		# ----------
		# output
		# Label = readlabel('/Users/Leon/Documents/Research/Code/trend_analysis/30clusters/30cluster_DrugPatents.csv')
		# Trend = label2trend(Label)

		# trend value
		# renewfile = '/Users/Leon/Documents/Research/Data/USPCMainAssg1981_2006Drug'
		# RenewInfo = read_renew_file(renewfile)
# ------------
		Value,AveValue,Renew0,Renew1,Renew2,Renew3 = calculate_trend_value(Trend, RenewInfo)
		write_distribution(['Trend sum value distribution'],distributionfile)
		interval, amount,percentage = distribution2(Value,10)
		# print interval
		# print amount
		# print percentage
		# sys.exit()
		write_distribution(interval,distributionfile)
		write_distribution(amount,distributionfile)
		write_distribution(percentage,distributionfile)
		write_distribution('\n',distributionfile)
		interval, amount,percentage = distribution2(AveValue,10)
		write_distribution(['Trend average value distribution'],distributionfile)
		write_distribution(interval,distributionfile)
		write_distribution(amount,distributionfile)
		write_distribution(percentage,distributionfile)
		write_distribution('\n',distributionfile)
		# trend size
		TrendSize = trendsize(Trend)
		# print sorted(TrendSize.items(), key = lambda e:e[1])
		interval, amount,percentage = distribution2(TrendSize,10)
		write_distribution(['Trend size distribution'],distributionfile)
		write_distribution(interval,distributionfile)
		write_distribution(amount,distributionfile)
		write_distribution(percentage,distributionfile)

		coefficient,x,y = correlation(TrendSize,AveValue)
		write_distribution(['correlation with average trend value',str(coefficient)],distributionfile)
		a0,a1,a2,a3,x0,y0,y1,y2,y3 = correlation_with_renew(TrendSize,Renew0,Renew1,Renew2,Renew3)
		write_distribution(['correlation with renew ratio',a0,a1,a2,a3],distributionfile)
		write_distribution(x0,distributionfile)
		write_distribution(y0,distributionfile)
		write_distribution(y1,distributionfile)
		write_distribution(y2,distributionfile)
		write_distribution(y3,distributionfile)
		write_distribution('\n',distributionfile)


		# # trend connectivity
		Edeges, Connectivity = calculate_connectivity(Trend,Citation)
		edegefile = '/Users/Leon/Documents/Research/Code/trend_analysis/30clusters/edegefile.csv'
		connectivityFile = '/Users/Leon/Documents/Research/Code/trend_analysis/30clusters/connectivity.csv'
		store_dictionary(Edeges,edegefile)
		store_dictionary(Connectivity,connectivityFile)
		interval, amount,percentage = distribution2(Edeges,10)
		write_distribution(['edge amount distribution'],distributionfile)
		write_distribution(interval,distributionfile)
		write_distribution(amount,distributionfile)
		write_distribution(percentage,distributionfile)
		write_distribution('\n',distributionfile)

		interval, amount,percentage = distribution3(Connectivity,10)
		write_distribution(['connectivity distribution'],distributionfile)
		write_distribution(interval,distributionfile)
		write_distribution(amount,distributionfile)
		write_distribution(percentage,distributionfile)
		coefficient,x,y = correlation(Connectivity,AveValue)
		write_distribution(['correlation with average trend value',str(coefficient)],distributionfile)
		a0,a1,a2,a3,x0,y0,y1,y2,y3 = correlation_with_renew(Connectivity,Renew0,Renew1,Renew2,Renew3)
		write_distribution(['correlation with renew ratio',a0,a1,a2,a3],distributionfile)
		write_distribution(x0,distributionfile)
		write_distribution(y0,distributionfile)
		write_distribution(y1,distributionfile)
		write_distribution(y2,distributionfile)
		write_distribution(y3,distributionfile)
		write_distribution('\n',distributionfile)
		# break
def load_dateFile(datefile):
	# load the dateFile
	f = open(datefile, 'r')
	# initailize a dictionary for patent and their grant date
	Date = {}
	# read file line by line
	for line in f:
			line = line.split()
			Date[line[0]] = int(line[1])
	print ( 'the number of patent in date file: %s' %(len(Date)))
	f.close()
	return Date
def filter_By_Year(Trend,Date,begin_year,end_year):
	'''including begin_year and end_year'''
	newTrend = {}
	begintime = (begin_year)*12
	endtime = (end_year+1)*12
	for label,patentlist in Trend.items():
		newpatentlist = [patent for patent in patentlist if int(Date[patent])>=begintime and int(Date[patent])<endtime]
		newTrend[label] = newpatentlist
	return newTrend
def readlabel(labelfile):
	'''each line is a patent ID with its label,return a
	dictionary of patentID:label '''
	file1 = open(labelfile,'r')
	reader = csv.reader(file1)
	# initailize a dictionary for patent and their cluster number
	Cluster = {}
	n = 0
	for key, val in reader:
		Cluster[key]=int(val)
		n += 1
		# if n == 10000:
			# break
		# break
	# print Cluster
	file1.close()
	return Cluster

def label2trend(LabelDic):
	'''given a dictionary of patentID:label,
		return a dictionary of label:[patentID]
	'''
	TrendDic = {}
	for ID,label in LabelDic.items():
		addintoTrendDic(ID,label,TrendDic)
	return TrendDic

def addintoTrendDic(key,value,TrendDic):
	'''reverse the key and value of Dic and put it into 
		another dictionary and return it '''
	if value not in TrendDic:
		TrendDic[value] = [key]
	else:
		TrendDic[value].append(key)
	return TrendDic
def trendsize(trendDic):
	'''given a trend dictionary label:[patentID],
		return a dictionary label:length of patentID list'''
	Size = {}
	for label,patentlist in trendDic.items():
		Size[label] = len(patentlist)
	# print 'the trend and its size is', Size
	return Size
def distribution2(Property,division):
	'''given a Dic of trend property(size,value,connectivity),
		division is how many part we want to seperate the whole range
		Dic trendlabel:property
		output the distribution of property
	'''
	# sort the Dic based on property
	sortlist = sorted(Property.items(), key = lambda a:a[1],reverse = False)
	# print 'sortlist',sortlist
	length = float(len(sortlist))
	# a new list of list(result) to seperate sortlist
	result = []
	seperatedlist = []
	minimum_property = float(sortlist[0][1])
	maximum_property = float(sortlist[-1][1])+0.1
	range_value = ((maximum_property-minimum_property)/division)
	seperatedrange = [minimum_property]
	range_end = minimum_property+range_value
	for i in range(0,division):
		seperatedrange.append(seperatedrange[-1]+range_value)
	# print 'seperatedrange',seperatedrange

	result = [[] for x in range(0,division)]
	# print 'result',result
	result[0] = [sortlist[0]]
	for i,seperator in enumerate(seperatedrange[:-1]):
		for trend in sortlist:
			if trend[1]>seperator and trend[1] <=(seperator+range_value):
				result[i].append(trend)
	# print 'result',result
	batch = []
	batch2 = []
	for trends in result:
		batch.append(len(trends))
		batch2.append(len(trends)/length)

	return seperatedrange, batch, batch2
def distribution3(Property,division):
	'''given a Dic of trend property(size,value,connectivity),
		division is how many part we want to seperate the whole range
		Dic trendlabel:property
		output the distribution of property
	'''
	# sort the Dic based on property
	sortlist = sorted(Property.items(), key = lambda a:a[1],reverse = False)
	# print 'sortlist',sortlist
	length = float(len(sortlist))
	# a new list of list(result) to seperate sortlist
	result = []
	seperatedlist = []
	minimum_property = float(sortlist[0][1])
	maximum_property = float(sortlist[-1][1])+0.000001
	range_value = ((maximum_property-minimum_property)/division)
	seperatedrange = [minimum_property]
	range_end = minimum_property+range_value
	for i in range(0,division):
		seperatedrange.append(seperatedrange[-1]+range_value)
	# print 'seperatedrange',seperatedrange

	result = [[] for x in range(0,division)]
	# print 'result',result
	result[0] = [sortlist[0]]
	for i,seperator in enumerate(seperatedrange[:-1]):
		for trend in sortlist:
			if trend[1]>seperator and trend[1] <=(seperator+range_value):
				result[i].append(trend)
	# print 'result',result
	batch = []
	batch2 = []
	for trends in result:
		batch.append(len(trends))
		batch2.append(len(trends)/length)

	return seperatedrange, batch, batch2
def write_distribution(value,writefile):
	'''append the value in a line'''
	with open(writefile,'a') as f:
		writer = csv.writer(f)
		writer.writerow(value)

def calculate_trend_value(Trend, Renew):
	'''given a dictionary of trend label:patentlist,
		for each trend:
		calculate 1.the number of 0-renew and ratio
				  2.the number of 1-renew and ratio
				  3.the number of 2-renew and ratio
				  4.the number of 3-renew and ratio
				  5.the totall value of a trend
	'''
	Renew0, Renew1, Renew2, Renew3, Value, AveValue= {},{},{},{},{},{}
	for label,patentlist in Trend.items():
		# if len(patentlist) == 0:
		# 	print 'label,0-patentlist',label,patentlist
		# 	continue
		x0,x1,x2,x3=0,0,0,0
		for patent in patentlist:
			try:
				if Renew[patent] == '0':
					x0 += 1
				elif Renew[patent] == '1':
					x1 += 1
				elif Renew[patent] == '2':
					x2 += 1
				elif Renew[patent] == '3':
					x3 += 1
				else:
					print 'patent %s did not equal to any renew'%patent
			except KeyError:
				print 'patent %s did not exits in renew file'%patent
		value = x0 + 2*x1 + 3*x2 + 4*x3
		Value[label] = value
		length = len(patentlist)
		AveValue[label] = float(value)/length
		Renew0[label] = float(x0)/length
		Renew1[label] = float(x1)/length
		Renew2[label] = float(x2)/length
		Renew3[label] = float(x3)/length
	return Value, AveValue,Renew0,Renew1,Renew2,Renew3

def read_renew_file(renewfile):
	'''read the drug-related patents renew information'''
	drug = open(renewfile,'r')
	# initialize a dictionary for all drug patent and their renew status
	renew = {}
	for line in drug:
	    patentInfo = line.split()
	    renew[patentInfo[0]] = patentInfo[2]
	drug.close()
	return renew
def read_citation(rawfile):
	Citation = {}
	readfile = open(rawfile,'r')
	reader = csv.reader(readfile,delimiter = '\t')
	for patent in reader:
		flag = True
		cite = patent[5].split()
		# for number in cite:
			# if not number.isdigit():
				# print 'patent %s citation is not valid:%s' %(patent[0],cite)
				# flag = False
				# break
		if flag:
			Citation[patent[0]] = cite
	readfile.close()
	return Citation
def calculate_connectivity(TrendDic,CitationDic):
	Edeges = {}
	Con = {}
	for label,patentlist in TrendDic.items():
		cite_count = 0
		for patent in patentlist:
			citelist = CitationDic[patent]
			in_trend_citelist = []
			for cite in citelist:
				if cite in patentlist:
					in_trend_citelist.append(cite)
			cite_count += len(in_trend_citelist)
		Edeges[label] = cite_count
		length = float(len(patentlist))
		Con[label] = float(cite_count)/(length*(length-1)/2)
		print 'finish trend %s connectivity' %label
	return Edeges, Con
def store_dictionary(dictionary, writefile):
	with open(writefile, 'w') as f:
		writer = csv.writer(f)
		for key, value in dictionary.items():
			writer.writerow([key,value])
def load_dictionary(readfile):
	dictionary = {}
	with open(readfile,'r') as f:
		reader = csv.reader(f)
		for key,value in reader:
			dictionary[key] = eval(value)
	return dictionary
def correlation(dictionary1,dictionary2):
	'''given two dictionary, calculate the pearson correlation coefficient'''
	a = sorted(dictionary1.items(),key = lambda e:e[0])
	b = sorted(dictionary2.items(),key = lambda e:e[0])
	x = [e[1] for e in a]
	y = [e[1] for e in b]
	# z = zip(x,y)
	# print x
	# print y
	return pearsonr(x,y),x,y
def correlation_with_renew(dictionary,Renew0,Renew1,Renew2,Renew3):
	a0,x0,y0 = correlation(dictionary,Renew0)
	a1,x1,y1 = correlation(dictionary,Renew1)
	a2,x2,y2 = correlation(dictionary,Renew2)
	a3,x3,y3 = correlation(dictionary,Renew3)
	return a0,a1,a2,a3,x0,y0,y1,y2,y3
def filter_By_Number(TrendDic, number):
	dictionary = {}
	for label, patentlist in TrendDic.items():
		if len(patentlist) >= number:
			dictionary[label] = patentlist
	return dictionary

if __name__ == '__main__':
	main()