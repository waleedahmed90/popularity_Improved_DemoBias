#PEN = /Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats pen
#COMP = /Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats comp
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



def LoadFile(filePath):
	with gzip.open(filePath,'rt') as Temp:
		temp = Temp.read()
	Temp.close()

	statsDictionary = json.loads(temp)

	return statsDictionary


def popularity_popularity(dictionaryPop):

	indvd_pop_sum = 0.0

	for h in dictionaryPop.keys():
		tempList = dictionaryPop[h]
		#print(tempList)
		if tempList[1]!=0:
			indvd_pop_sum = indvd_pop_sum + (tempList[0]/tempList[1])
		#print(tempList)

	print("total hashtags: ", len(dictionaryPop))
	return round((indvd_pop_sum/len(dictionaryPop)), 3)

def clusterPopularities(clusterDict, popularityDictionary):
	#indvd_pop_sum = 0

	for c in clusterDict:
		hashList = clusterDict[c]
		indvd_pop_sum = 0
		countHashtags = 0
		for h in hashList:
			if h in popularityDictionary.keys():
				countHashtags = countHashtags + 1
				tempList = popularityDictionary[h]
				if tempList[1]!=0:
					indvd_pop_sum = indvd_pop_sum + (tempList[0]/tempList[1])

		print(c, ": ", round((indvd_pop_sum/countHashtags), 3))


###########FLOW BEGINS HERE##########

pop_pen_normal_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats pen/normal_trends.gz'
pop_pen_normal = LoadFile(pop_pen_normal_path)

pop_pen_gender_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats pen/gend_trends.gz'
pop_pen_gender = LoadFile(pop_pen_gender_path)

pop_pen_race_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats pen/race_trends.gz'
pop_pen_race = LoadFile(pop_pen_race_path)

pop_pen_age_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats pen/age_trends.gz'
pop_pen_age = LoadFile(pop_pen_age_path)


pop_comp_normal_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats comp/normal_trends.gz'
pop_comp_normal = LoadFile(pop_comp_normal_path)

pop_comp_gender_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats comp/gend_trends.gz'
pop_comp_gender = LoadFile(pop_comp_gender_path)

pop_comp_race_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats comp/race_trends.gz'
pop_comp_race = LoadFile(pop_comp_race_path)

pop_comp_age_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Popularity/popularity stats comp/age_trends.gz'
pop_comp_age = LoadFile(pop_comp_age_path)



#Penalties Clusters
norm_gend_path_p = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details/normal_gend_details.gz'
clus_norm_gend_p = LoadFile(norm_gend_path_p) 

norm_race_path_p = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details/normal_race_details.gz'
clus_norm_race_p = LoadFile(norm_race_path_p)

norm_age_path_p  = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details/normal_age_details.gz'
clus_norm_age_p = LoadFile(norm_age_path_p)


pen_gend_path_p = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details/balanced_gend_details.gz'
clus_pen_gend = LoadFile(pen_gend_path_p)

pen_race_path_p = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details/balanced_race_details.gz'
clus_pen_race = LoadFile(pen_race_path_p)

pen_age_path_p = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details/balanced_age_details.gz'
clus_pen_age = LoadFile(pen_age_path_p)


#Compensation Clusters
norm_gend_path_c = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details_comp/normal_gend_details.gz'
clus_norm_gend_c = LoadFile(norm_gend_path_c)

norm_race_path_c = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details_comp/normal_race_details.gz'
clus_norm_race_c = LoadFile(norm_race_path_c)

norm_age_path_c  = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details_comp/normal_age_details.gz'
clus_norm_age_c = LoadFile(norm_age_path_c)


comp_gend_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details_comp/balanced_gend_details.gz'
clus_comp_gend = LoadFile(comp_gend_path)

comp_race_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details_comp/balanced_race_details.gz'
clus_comp_race = LoadFile(comp_race_path)

comp_age_path = '/Users/WaleedAhmed/Documents/THESIS_DS_CODE/Additional Work/Cluster_Details_comp/balanced_age_details.gz'
clus_comp_age = LoadFile(comp_age_path)




#total:
print("PENALTIES ONLY")
print("Normal All: ", popularity_popularity(pop_pen_normal))
print("Gender All: ", popularity_popularity(pop_pen_gender))
print("Race All: ", popularity_popularity(pop_pen_race))
print("Age All: ", popularity_popularity(pop_pen_age))


print("\n\nPENALTIES & COMPENSATION")
print("Normal All: ", popularity_popularity(pop_comp_normal))
print("Gender All: ", popularity_popularity(pop_comp_gender))
print("Race All: ", popularity_popularity(pop_comp_race))
print("Age All: ", popularity_popularity(pop_comp_age))







#Across Clusters Penalties
print("\n Normal Gender")
clusterPopularities(clus_norm_gend_c, pop_pen_normal)
print("Penalized Gender")
clusterPopularities(clus_pen_gend, pop_pen_gender)

print("\n Normal Race")
clusterPopularities(clus_norm_race_p, pop_pen_normal)
print("Penalized Race")
clusterPopularities(clus_pen_race, pop_pen_race)


print("\n Normal Age")
clusterPopularities(clus_norm_age_p, pop_pen_normal)
print("Penalized Age")
clusterPopularities(clus_pen_age, pop_pen_age)


#Across Clusters Compensation
print("\n Normal Gender")
clusterPopularities(clus_norm_gend_c, pop_comp_normal)
print("Compensated Gender")
clusterPopularities(clus_comp_gend, pop_comp_gender)

print("\n Normal Race")
clusterPopularities(clus_norm_race_c, pop_comp_normal)
print("Compensated Race")
clusterPopularities(clus_comp_race, pop_comp_race)


print("\n Normal Age")
clusterPopularities(clus_norm_age_c, pop_comp_normal)
print("Compensated Age")
clusterPopularities(clus_comp_age, pop_comp_age)





# pop_pen_normal
# clus_norm_gend_p



#pen only










