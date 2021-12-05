import copy
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

import numpy as np

import time
import utils
import models
import argparse
import data_loader
import pandas as pd
import ujson as json

from sklearn import metrics

from ipdb import set_trace

import sys
import time
import os
import csv

import re

import shutil

time = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
		"12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", 
		"24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", 
		"36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47"]

types = ["1-hourly", "2-hourly", "4-hourly", "8-hourly", "16-hourly", "24-hourly", "48-hourly"]
counters = [48, 24, 12, 6, 3, 2, 1]
multiplier = [1, 2, 4, 8, 16, 24, 48]
# CREATES HOURLY DIRECTORY
newpath = r"hours"
#print(newpath)
for obj in types:
	temp = newpath + r"/" + obj
	if not os.path.exists(temp):
	    os.makedirs(temp)
	temp = ""

parent = './raw/set-a'
patient_ids = []
for filename in os.listdir(parent):
    # The patient data in PhysioNet contains 6-digits
    match = re.search('\d{6}', filename)
    if match:
        id_ = match.group()
        patient_ids.append(id_)

choose = 0
filename = patient_ids[choose] + ".txt"
filepath = parent + r"/" + filename
transitionCondition = False
fakeTransitionCondition = False
if os.path.isfile(filepath):
	print("Processing " + filename)
	for i in range(7):
		temp = newpath + r"/" + types[i]
		# READ FILE
		file = open(filepath,"r")
		headerState = True
		temptime = []
		for j in range(counters[i]):
			# CREATE OUTFILE
			outfile = temp + r"/" + str(j) + "_" + filename
			#print(outfile) # WRITE ALL HOURLY DATA
			# WRITE HEADER
			x = open(outfile, "a", newline='')
			csv_writer = csv.writer(x)
			# WRITE HEADER + PATIENT SPECIFIC CLASSIFIERS
			headerFile = open(filepath,"r")
			for w in range (7):
				header_line = headerFile.readline().replace("\n","").split(",")
				csv_writer.writerow(header_line)
				continue
			# WRITE ROWS
			# SKIP HEADER
			if (headerState):
				for w in range (7):
					line = file.readline()
					headerState = False
			# WRITE BODY
			line = file.readline()

			if (transitionCondition): # HOUR TRANSITION
				csv_writer.writerow(transition.replace("\n","").split(","))
				transitionCondition = False

			
			temptime = temptime + [time[j]]
			print(temptime)
			while line:
				print("STATE: " + line.replace("\n","").split(",")[0].split(":")[0])
				print("CONDITION: " + str(temptime))
				if (line.replace("\n","").split(",")[0].split(":")[0] in temptime):
					csv_writer.writerow(line.replace("\n","").split(","))
					line = file.readline()
				else:
					line = file.readline()
		temptime = []
								
	headerFile.close()
	file.close()
	x.close()
# Removes entire directory "hours"
# shutil.rmtree(newpath)
