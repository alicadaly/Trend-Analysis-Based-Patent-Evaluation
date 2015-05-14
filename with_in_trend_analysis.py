#!/usr/bin/python
# -*- encoding: utf8 -*-
# position  vs. renew

import csv,sys,os
from trend_distribution_analysis import readlabel,label2trend,write_distribution,filter_By_Year,filter_By_Number
from scipy.stats.stats import pearsonr

csv.field_size_limit(sys.maxsize)

__author__ = 'Leon'

def main():
	renewfile = '/Users/Leon/Documents/Research/Data/USPCMainAssg1981_2006Drug'
	Renewdictionary = load_renewfile(renewfile)
	datefile = '/Users/Leon/Documents/Research/Data/grantDate'
	Date = load_dateFile(datefile)
	directory = './USclass'
	filenames = [x for x in os.listdir(directory) if 'Trend' in x]
	for filename in filenames:
		cluster_number = ''.join([x for x in filename if x.isdigit()])
		print filename

		Trend = load_dictionary(directory+'/'+filename)
		Trend = filter_By_Year(Trend,Date,1981,1998)
		Trend = filter_By_Number(Trend,100)
		print 'number of qualified trend ',len(Trend)
		# for label,patentlist in Trend.items():
		# 	if len(patentlist)<=10:
		# 		del Trend[label]
		# 		print 'delete trend %s because it is smaller than 10'%(label)

		positionfile = './data_analysis/US/'+cluster_number+'trends_position_distribution.csv'
		
		
		# 0: ['4855911', '5656428', '6027445'...]
		positionFeature = position_feature_for_trend(Trend,Date)
		matrix,percentage = trend_distribution(positionFeature,0.1,Renewdictionary)
		# calculate the average
		average0 = nth_renew_average(matrix,0)
		average1 = nth_renew_average(matrix,1)
		average2 = nth_renew_average(matrix,2)
		average3 = nth_renew_average(matrix,3)
		percentage.append('correlation')
		head = percentage[1:]
		write_distribution(head,positionfile)
		write_distribution(['renew 0,1,2,3 ratio in different range'],positionfile)

		a = pearsonr(average0,head[0:-1])
		average0.extend(a)
		write_distribution(average0,positionfile)
		a = pearsonr(average1,head[0:-1])
		average1.extend(a)
		write_distribution(average1,positionfile)
		a = pearsonr(average2,head[0:-1])
		average2.extend(a)
		write_distribution(average2,positionfile)
		a = pearsonr(average3,head[0:-1])
		average3.extend(a)
		write_distribution(average3,positionfile)
		write_distribution('\n',positionfile)
		label = 0
		for trend in matrix:
			write_distribution(['trend '+str(label)],positionfile)
			for renew in trend:
				line = renew.extend(pearsonr(renew,head[0:-1]))
				write_distribution(renew,positionfile)
			write_distribution('\n',positionfile)
			label += 1
			
	# {'24': [['4404279', 0.0], ['4533635', 0.00024],...],...}
def load_dictionary(readfile):
	dictionary = {}
	with open(readfile,'r') as f:
		reader = csv.reader(f)
		for key,value in reader:
			dictionary[key] = eval(value)
	return dictionary
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
def position_feature_for_trend(Trend,Date):
	''' return a dictionary trend label: ordered patent list[(patentnumber,positon),...]'''
	Trend_Position = {}
	for label ,patentlist in Trend.items():
		DateinTrend = {}
		# print patentlist
		for patent in patentlist:
			try:
				DateinTrend[patent] = Date[patent]
			except KeyError:
				print 'no patent %s in Date data' %(patent)
		sortlist = sorted(DateinTrend.items(),key = lambda e:e[1], reverse= False)
		length = len(sortlist)
		patentlist = [[0,0] for x in range(0,length)]

		for x in range(0, length):
			patentlist[x][0] = sortlist[x][0]
			patentlist[x][1] = float(x)/length
		Trend_Position[label] = patentlist
	return Trend_Position
def trend_distribution(Trend_property,range_value,Renewdictionary):
	'''given patents of every trend and their property(position,diversity),
		calcuate the renew percentage of every range'''

	# ratio = [[] for x in range(0,len(Trend_property))] # a 3-D list: trend, renew, range
	ratio = []
	for label,patentlist in Trend_property.items():

		result = []
		seperatedlist = []
		minimum_property = float(patentlist[0][1])
		seperatedrange = [minimum_property]
		range_end = minimum_property+float(range_value)
		for patent in patentlist:
			if patent[1]< range_end:
				seperatedlist.append(patent)
			else:
				result.append(seperatedlist)
				# print result
				seperatedlist = [patent]
				# print seperatedlist
				seperatedrange.append(range_end)
				range_end += range_value
		result.append(seperatedlist)
		seperatedrange.append(range_end)
		# now we have result and seperatedrange 
		# for a trend, we have 4 list of renew ratio, each has several range
		x0=renew_ratio(result,'0',Renewdictionary)
		x1=renew_ratio(result,'1',Renewdictionary)
		x2=renew_ratio(result,'2',Renewdictionary)
		x3=renew_ratio(result,'3',Renewdictionary)
		ratio.append([x0,x1,x2,x3])
	return ratio,seperatedrange
def renew_ratio(listoflist,status,Renewdictionary):
	'''given a list of list of patentid, return a list of renew status ratio of sublist'''
	ratiolist = []
	for sublist in listoflist:
		count = 0
		for patent in sublist:
			if Renewdictionary[patent[0]] == status:
				count += 1
		if len(sublist)== 0:
			ratiolist.append(0)
		else:
			ratiolist.append(float(count)/len(sublist))
		
	return ratiolist
def load_renewfile(renewfile):
	# read the drug-related patents renew information
	drug = open(renewfile,'r')
	# initialize a dictionary for all drug patent and their renew status
	renew = {}
	for line in drug:
		patentInfo = line.split()
		renew[patentInfo[0]] = patentInfo[2]
	drug.close()
	return renew
def nth_renew_average(matrix,n):
	average = []
	# print 'matrix1',len(matrix)
	# print 'matrix2',len(matrix[0])
	# print 'matrix3',len(matrix[0][0])
	for i in range(0,len(matrix[0][0])):
		try:
			a = sum([matrix[x][n][i] for x in range(0,len(matrix))])
		except IndexError:
			print 'x=',x,' n=',n,' i=',i
			# print matrix[109]
			# print matrix[109][0]
			# print matrix[109][0][3]
			# sys.exit()
		b = float(a)/len(matrix)
		average.append(b)
	return average
		
if __name__ == '__main__':
	main()