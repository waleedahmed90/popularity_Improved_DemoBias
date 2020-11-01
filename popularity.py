import gzip
import json
import glob
import itertools
from pandas import DataFrame
#import matplotlib.pyplot as plt
import ntpath
import time
import os
import shutil
import operator
import sys




def take(tempDict, n):
	return {A:N for (A,N) in [x for x in tempDict.items()][:n]}

def countTweets(dictTemp):
	sumTweets = 0
	for t in dictTemp:
		sumTweets = sumTweets + sum(dictTemp[t])

	return sumTweets

def countPromotersOneStamp(dailyUsage, usageInfoList):
	
	total_Stamps = len(usageInfoList)-1


	for s in range(total_Stamps):
		stamp = usageInfoList[s].split("\t")
		timeStamp = stamp[0]
		Usage = json.loads(stamp[1])

		for t in Usage:
			try:
				tempList = dailyUsage[t]
				tempList[s] = len(Usage[t])
				dailyUsage[t] = tempList
			except KeyError:
				pass

	
	return dailyUsage



def timeSeriesGenerator(countFile, usageFile):
	

	with gzip.open(countFile, 'rt') as f:
		countInfo = f.read()
	f.close()

	#Demographics of available hashtags
	HashtagCounts = json.loads(countInfo)
		
	dayDetail = {}

	with gzip.open(usageFile, 'rt') as f1:
		usageInfo = f1.read()
	f1.close()


	usageInfoList = usageInfo.split("\n")
	total_Stamps = len(usageInfoList)-1

	dailyUsage = {}
	count_trend = 0
	count_tweet = 0

	for s in range(total_Stamps):
		stamp = usageInfoList[s].split("\t")
		timeStamp = stamp[0]
		Usage = json.loads(stamp[1])

		for t in Usage.keys():
			if t in HashtagCounts:
				dailyUsage[t] = [0]*96
			count_trend = count_trend + 1
			count_tweet = count_tweet + len(Usage[t])


	dayDetail = countPromotersOneStamp(dailyUsage, usageInfoList)



	usage_threshold = round((count_tweet/count_trend), 3)


	return usage_threshold, dayDetail

def adjustedTrendsGender(surge_dict, Demo_Gend):

	weight_male = 0.463
	weight_female = 0.537

	new_Surges = {}

	# surgeValues = surge_dict.values()
	# maxSurge = max(surgeValues)
	# minSurge = min(surgeValues)

	for t in surge_dict.keys():
		surge = surge_dict[t]
		[M,F] = Demo_Gend[t]

		contrb_f = (F * surge) / 100
		contrb_m = (M * surge) / 100
		
		if (M>F):
			revised_surge = contrb_f / weight_female

			new_Surges[t] = round(revised_surge, 3)
		
		else:

# ###############
			edge = (F-M)/100
# ###############

			revised_surge = (contrb_m / weight_male)

			# #
			# compensation = revised_surge * edge
			# #
			# revised_surge = revised_surge + compensation


			new_Surges[t] = round(revised_surge, 3)

	#sorting them in descending order
	sorted_surges = dict(sorted(new_Surges.items(), key=operator.itemgetter(1),reverse=True))

	top_10 = take(sorted_surges, 10)

	return top_10


def	adjustedTrendsRace(surge_dict, Demo_Race):
	
	weight_white = 0.2364
	weight_black = 0.4694
	weight_asian = 0.2943

	new_Surges = {}

	for t in surge_dict.keys():
		surge = surge_dict[t]
		[W,B,A] = Demo_Race[t]

		contrb_w = ( W * surge ) / 100
		contrb_b = ( B * surge ) / 100
		contrb_a = ( A * surge ) / 100

		if (W>(B+A)):

			revised_surge = (contrb_b + contrb_a) / (weight_black + weight_asian)

			new_Surges[t] = round(revised_surge, 3)
		
		else:
	
###############
			edge = ((B+A)-W)/100
###############

			revised_surge = (contrb_w / weight_white)


			# #	
			# compensation = revised_surge * edge
			# #
			# revised_surge = revised_surge + compensation



			new_Surges[t] = round(revised_surge, 3)


	#sorting them in descending order
	sorted_surges = dict(sorted(new_Surges.items(), key=operator.itemgetter(1),reverse=True))

	top_10 = take(sorted_surges, 10)

	return top_10

def	adjustedTrendsAge(surge_dict, Demo_Age):

	weight_ado = 0.2819			#(less than 20 years of age) 		#(adolescent)
	weight_old = 0.0546			#(above 65 years of age) 	 		#(old)
	weight_yng = 0.3753			#(between 20 and 40 years of age)	#(young)
	weight_mid = 0.2896 		#(between 40 and 65 years of age)	#(mid-aged)


	new_Surges = {}

	# surgeValues = surge_dict.values()
	# maxSurge = max(surgeValues)
	# minSurge = min(surgeValues)

	for t in surge_dict.keys():
		surge = surge_dict[t]
		[A,O,Y,M] = Demo_Age[t]

		contrb_o_y = ( (O+Y) * surge ) / 100
		contrb_a_m = ( (A+M) * surge ) / 100


		if ((O+Y)>(A+M)):

			revised_surge = contrb_a_m / (weight_ado + weight_mid)

			new_Surges[t] = round(revised_surge, 3)

		else:

###############
			edge = ((A+M)-(O+Y))/100
###############

			revised_surge = (contrb_o_y / (weight_old + weight_yng))


			# #
			# compensation = revised_surge * edge
			# #
			# revised_surge = revised_surge + compensation




			new_Surges[t] = round(revised_surge, 3)



	#sorting them in descending order
	sorted_surges = dict(sorted(new_Surges.items(), key=operator.itemgetter(1),reverse=True))

	top_10 = take(sorted_surges, 10)

	return top_10



def initPopDict(dictTempPop, top10):

	for k in top10:
		if k not in dictTempPop:
			#'hashtag_name': [tweetsTotal, count of timestamps the hastag was used in]
			dictTempPop[k] = [0, 0]

	return dictTempPop



def calculateSurge(dailyUsage, use_thresH, genDemo, racDemo, ageDemo, count_pop_norm, count_pop_gen, count_pop_rac, count_pop_age):
	Lambda = 0.25 # one eighth (1/8)th

	TOP_GENDER = {}
	TOP_RACE = {}
	TOP_AGE = {}

	TOP_10 = {}

	#how many times it was used after it became trending
	# count_pop_norm = {}
	# count_pop_gen = {}
	# count_pop_rac = {}
	# count_pop_age = {}

	temp_pop_norm = {}
	temp_pop_gen = {}
	temp_pop_race = {}
	temp_pop_age = {}

	exponent = 0
	for s in range(1, 96):

		singleStampSurge = {}

		for t in dailyUsage.keys():
			

			use_list = dailyUsage[t]

			tot_tweets = sum(use_list[:s])

			#how many times it has been used 
			current_tweets = use_list[s]


			if t in count_pop_norm.keys():
				tempList1 = count_pop_norm[t]

				tempList1[0] = tempList1[0] + current_tweets
				tempList1[1] = tempList1[1] + 1

				count_pop_norm[t] = tempList1

			if t in count_pop_gen.keys():
				tempList2 = count_pop_gen[t]

				tempList2[0] = tempList2[0] + current_tweets
				tempList2[1] = tempList2[1] + 1
				count_pop_gen[t] = tempList2

			if t in count_pop_rac.keys():
				tempList3 = count_pop_rac[t]

				tempList3[0] = tempList3[0] + current_tweets
				tempList3[1] = tempList3[1] + 1
				count_pop_rac[t] = tempList3

			if t in count_pop_age.keys():
				tempList4 = count_pop_age[t]

				tempList4[0] = tempList4[0] + current_tweets
				tempList4[1] = tempList4[1] + 1
				count_pop_age[t] = tempList4


			t_1 = use_list[s]
			t_0 = use_list[s-1]

			if t_0 == 0:
				ratioSurge = t_1
			else:
				ratioSurge = t_1/t_0


			if t_1!=0:
				exponent = 0
			else:
				exponent = exponent + 1

			surge = (ratioSurge) + ( ( tot_tweets / s ) * ( (use_thresH) ** ( - ( Lambda * exponent ) ) ) )


			singleStampSurge[t] = surge

		
		sorted_d = dict(sorted(singleStampSurge.items(), key=operator.itemgetter(1),reverse=True))
		
		# #Removing the values with zero surges
		new_surges = {x:y for x,y in sorted_d.items() if y!=0}

		temp_top_10 = take(new_surges, 10)
		#these topics became trending

		#initialize the popularity dictionary with new hashtags with value zero 
		temp_pop_norm = initPopDict(count_pop_norm, temp_top_10)
		count_pop_norm.update(temp_pop_norm)

		##
		temp_top_10_gend = adjustedTrendsGender(new_surges, genDemo)

		temp_pop_gen = initPopDict(count_pop_gen, temp_top_10_gend)
		count_pop_gen.update(temp_pop_gen)
		##

		##
		temp_top_10_race = adjustedTrendsRace(new_surges, racDemo)

		temp_pop_race = initPopDict(count_pop_rac, temp_top_10_race)
		count_pop_rac.update(temp_pop_race)
		##

		##
		temp_top_10_age = adjustedTrendsAge(new_surges, ageDemo)

		temp_pop_age = initPopDict(count_pop_age, temp_top_10_age)
		count_pop_age.update(temp_pop_age)
		##

		# print("\n\n NORMAL\n")
		# print(count_pop_norm)

		# print("\n\n GENDER")
		# print(count_pop_gen)

		# print("\n\n RACE")
		# print(count_pop_rac)

		# print("\n\n AGE")
		# print(count_pop_age)
		# #input("ctrl c ...")

		TOP_10.update(temp_top_10)
		TOP_GENDER.update(temp_top_10_gend)
		TOP_RACE.update(temp_top_10_race)
		TOP_AGE.update(temp_top_10_age)

	
	return TOP_10, TOP_GENDER, TOP_RACE, TOP_AGE, count_pop_norm, count_pop_gen, count_pop_rac, count_pop_age




if __name__== "__main__":
	start_time = time.time()

	glob_gend = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Demographics_Percentages/Gender_Percentage_User_Demographics.gz'

	glob_race = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Demographics_Percentages/Race_Percentage_User_Demographics.gz'

	glob_age = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Demographics_Percentages/Age_Percentage_User_Demographics.gz'

	with gzip.open(glob_gend, 'rt') as g:
		GENDERInfo = g.read()
	g.close()

	#Demographics of available hashtags
	GLOBAL_GENDER = json.loads(GENDERInfo)

	with gzip.open(glob_race, 'rt') as r:
		RACEInfo = r.read()
	r.close()

	#Demographics of available hashtags
	GLOBAL_RACE = json.loads(RACEInfo)

	with gzip.open(glob_age, 'rt') as a:
		AGEInfo = a.read()
	a.close()

	#Demographics of available hashtags
	GLOBAL_AGE = json.loads(AGEInfo)


	
	path_usage = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/hashtag_Usage_Info/*.gz'
	usage_files =  sorted(glob.glob(path_usage))

	path_userCount = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/UserCountDailyDemographics/*.gz'
	count_files = sorted(glob.glob(path_userCount))


	path_gen_demo = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/GenderDailyDemographics/*.gz'
	gen_files = sorted(glob.glob(path_gen_demo))

	path_rac_demo = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/RaceDailyDemographics/*.gz'
	race_files = sorted(glob.glob(path_rac_demo))

	path_age_demo = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/AgeDailyDemographics/*.gz'
	age_files = sorted(glob.glob(path_age_demo))
	
	GENDER_TRENDING = {}
	RACE_TRENDING = {}
	AGE_TRENDING = {}

	TOP_TRENDS_NORMAL = {}

	
	#Calculating popularity
	#Usage after they became trending
	norm_pop = {}
	gen_pop = {}
	race_pop = {}
	age_pop = {}


	for fn in range(len(usage_files)):

		temp_norm_pop = {}
		temp_gen_pop = {}
		temp_race_pop = {}
		temp_age_pop = {}

		countFile = count_files[fn]
		usageFile = usage_files[fn]

		genFile = gen_files[fn]
		raceFile = race_files[fn]
		ageFile = age_files[fn]

		with gzip.open(genFile, 'rt') as f1:
			countInfoGen = f1.read()
		f1.close()
		genDemoToday = json.loads(countInfoGen)

		with gzip.open(raceFile, 'rt') as f2:
			countInfoRace = f2.read()
		f2.close()
		raceDemoToday = json.loads(countInfoRace)

		with gzip.open(ageFile, 'rt') as f3:
			countInfoAge = f3.read()
		f3.close()
		ageDemoToday = json.loads(countInfoAge)

		usage_threshold, daily_TimeSeries_Detail = timeSeriesGenerator(countFile ,usageFile)
####################here
		
		top10_today, top_10_GENDER, top_10_RACE, top_10_AGE, temp_norm_pop, temo_gen_pop, temp_race_pop, temp_age_pop = calculateSurge(daily_TimeSeries_Detail, usage_threshold, genDemoToday, raceDemoToday, ageDemoToday, norm_pop, gen_pop, race_pop, age_pop)

		#print(top_10_GENDER)

		#input("yakhbakh...")

		##here calcualte popularity

		print("\nDay: ",fn,"\n")
		print(len(top10_today))
		print(len(top_10_GENDER))
		print(len(top_10_RACE))
		print(len(top_10_AGE))
		print("\n")

		TOP_TRENDS_NORMAL.update(top10_today)
		GENDER_TRENDING.update(top_10_GENDER)
		RACE_TRENDING.update(top_10_RACE)
		AGE_TRENDING.update(top_10_AGE)

		norm_pop.update(temp_norm_pop)
		gen_pop.update(temp_gen_pop)
		race_pop.update(temp_race_pop)
		age_pop.update(temp_age_pop)


	print("\n\nfinalized")
	print(len(TOP_TRENDS_NORMAL))
	print(len(norm_pop))

	print(len(GENDER_TRENDING))
	print(len(gen_pop))

	print(len(RACE_TRENDING))
	print(len(race_pop))

	print(len(AGE_TRENDING))
	print(len(age_pop))

	#input("ctrl c ...")

	trending_demographics = './popularity stats pen/'

#	trending_demographics = './popularity stats comp/'
	
	


	try:
		os.mkdir(trending_demographics)
	except:
		shutil.rmtree(trending_demographics, ignore_errors=True)
		os.mkdir(trending_demographics)


	#Normal
	with gzip.open(trending_demographics+'normal_trends.gz', 'wb') as g1:
		g1.write(json.dumps(norm_pop).encode('utf-8'))
	g1.close()

	#Gender
	with gzip.open(trending_demographics+'gend_trends.gz', 'wb') as g2:
		g2.write(json.dumps(gen_pop).encode('utf-8'))
	g2.close()

	#Race
	with gzip.open(trending_demographics+'race_trends.gz', 'wb') as r1:
		r1.write(json.dumps(race_pop).encode('utf-8'))
	r1.close()

	#Age
	with gzip.open(trending_demographics+'age_trends.gz', 'wb') as r2:
		r2.write(json.dumps(age_pop).encode('utf-8'))
	r2.close()


	print("Elapsed Time")
	print("--- %s seconds ---" % (time.time() - start_time))

