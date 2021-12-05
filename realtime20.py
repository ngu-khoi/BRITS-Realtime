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
import shutil


#Window 0
types = ["1 hourly", "2 hourly", "4 hourly", "8 hourly", "16 hourly", "24 hourly", "48 hourly"]
counter = 0
args = 'py main.py --epochs 1 --batch_size 32 --model brits'

#CHOOSE PATIENT (CHANGE INDEX IN random_forest.py, hours.py, and reverse_input_process_temp.py)
filename = "132602"

# LOAD DATA
print("Loading Data")
start_time1 = time.time() # TRACKS LOADING
shutil.copy2("./hours/" + types[0] + "/10 " + filename + ".txt", "./raw/set-a/" + filename + ".txt") # complete target filename given
os.system('py input_process.py')
elapsed_time1 = time.time() - start_time1
# TRAIN DATA
start_time2 = time.time() # TRACKS TRAINING
os.system(args)
elapsed_time2 = time.time() - start_time2


# RETURN IMPUTED DATASET
print("Running reverse_input_process_temp")
os.system('py reverse_input_process_temp.py')
outfile = "./raw/set-a/combined.txt"

headerName = "./imputed/" + filename + ".csv"
headerFile = open(headerName,"r")
x = open(outfile, "a", newline='')
csv_writer = csv.writer(x)
for i in range (7):
    header_line = headerFile.readline().replace("\n","").split(",")
    csv_writer.writerow(header_line)
for i in range (counter * 35, (counter+1) * 35):
    header_line = headerFile.readline().replace("\n","").split(",")
    csv_writer.writerow(header_line)
x.close()
headerFile.close()


os.remove("./raw/set-a/" + filename + ".txt") # remove old dataset
os.rename(r"./raw/set-a/combined.txt",r"./raw/set-a/" + filename + ".txt") # renames imputed data
os.remove("./imputed/" + filename + ".csv") # removes imputed CSV
start_time3 = time.time() # TRACKS CLASSIFICATION
os.system('py random_forest.py')
elapsed_time3 = time.time() - start_time3
print("Window " + str(counter) + " Complete")
counter += 1

# OUTFILE FOR ELAPSED TIMES - LOADING, TRAINING, AND CLASSIFYING
outfile = "./result/data3.csv"
print("Processing data")
x = open(outfile, "a", newline='')
csv_writer = csv.writer(x)
csv_writer.writerow([elapsed_time1, elapsed_time2, elapsed_time3])
x.close()



# HOUR DIRECTORIES *NEED TO FIX NAMING ORDER*
hourly_directories = []
hourly_filenames = []
# Collect 
for folder_name in os.listdir('./hours'):
    print(folder_name)
    for hourly_filename in os.listdir('./hours' + "/" + folder_name):
        print (hourly_filename)
        hourly_directories.append('./hours' + "/" + folder_name + "/" + hourly_filename)
        hourly_filenames.append(hourly_filename)

watchdir = './raw/set-a'
contents = os.listdir(watchdir)
count = len(watchdir)
dirmtime = os.stat(watchdir).st_mtime
# INDEX AND COUNTER SHOULD ESSENTIALLY BE THE SAME
#multiplier = [1, 2, 4, 8, 16, 24, 48]
multiplier = [12, 24, 48]
index = counter
index2 = 0
while (index<7): #*READJUST WHILE LOOP EVENTUALLY*
    print(hourly_filenames[index])
    print(hourly_filenames[index][0])
    print(hourly_filenames[index][1])
    if (hourly_filenames[index][0]=="1" and hourly_filenames[index][1]=="0"):
        os.remove(r"./raw/set-a/" + filename + ".txt") # remove completed window
        shutil.copy2(hourly_directories[index], r"./raw/set-a/" + filename + ".txt")
        shutil.copy2("./temp/000000.txt", "./raw/set-a/000000.txt")
        print("WINDOW CHANGE")
        index2 += 1
        counter = 0
    else:
        shutil.copy2(hourly_directories[index], "./raw/set-a/000000.txt")

    newmtime = os.stat(watchdir).st_mtime
    if newmtime != dirmtime:
        dirmtime = newmtime
        newcontents = os.listdir(watchdir)
        added = set(newcontents).difference(contents)
        if added:
            print ("Files added: %s" %(" ".join(added)))
            for temp in added:
                break
            # CONCATS NEW HOUR OF DATA ONTO EXISTING DATASET
            fileName1 = "./raw/set-a/"+ filename + ".txt"
            fileName2 = "./raw/set-a/" + str(temp)
            outfile = "./raw/set-a/combined.txt"
            x = open(outfile, "a", newline='')
            csv_writer = csv.writer(x)
            file1 = open(fileName1,"r")
            line1 = file1.readline()
            while line1:
                csv_writer.writerow(line1.replace("\n","").split(","))
                line1 = file1.readline()
            file2 = open(fileName2,"r")
            for i in range (7):
                line2 = file2.readline().replace("\n","").split(",")
            line2 = file2.readline()
            while line2:
                csv_writer.writerow(line2.replace("\n","").split(","))
                line2 = file2.readline()
            file1.close()
            file2.close()
            x.close()

            # RENAMES CONCAT DATASET TO REPLACE EXISTING DATASET
            os.remove(fileName1)
            os.remove(fileName2)
            os.rename(r"./raw/set-a/combined.txt",r"./raw/set-a/" + filename + ".txt")
            print("Loading Data")
            start_time1 = time.time() # TRACKS LOADING
            os.system('py input_process.py')
            elapsed_time1 = time.time() - start_time1
            print("Training Network")
            start_time2 = time.time() # TRACKS TRAINING
            os.system(args)
            elapsed_time2 = time.time() - start_time2


            # RETURN IMPUTED DATASET
            print("Running reverse_input_process")
            os.system('py reverse_input_process_temp.py')
            outfile = "./raw/set-a/combined.txt"
            headerName = "./imputed/" + filename + ".csv"
            headerFile = open(headerName,"r")
            x = open(outfile, "a", newline='')
            csv_writer = csv.writer(x)
            for i in range (7):
                header_line = headerFile.readline().replace("\n","").split(",")
                csv_writer.writerow(header_line)
             
            for i in range ((counter+1) * multiplier[index2] * 35):
                header_line = headerFile.readline().replace("\n","").split(",")
                csv_writer.writerow(header_line)
            x.close()
            headerFile.close()

            os.remove("./raw/set-a/" + filename +  ".txt")
            os.rename(r"./raw/set-a/combined.txt",r"./raw/set-a/" + filename + ".txt")
            os.remove("./imputed/" + filename + ".csv")
            start_time3 = time.time() # TRACKS CLASSIFICATION
            os.system('py random_forest.py')
            elapsed_time3 = time.time() - start_time3
            print("Window " + str(index) + " Complete")

            # OUTFILE FOR ELAPSED TIMES - LOADING, TRAINING, AND CLASSIFYING
            outfile = "./result/data3.csv"
            print("Processing data")
            x = open(outfile, "a", newline='')
            csv_writer = csv.writer(x)
            csv_writer.writerow([elapsed_time1, elapsed_time2, elapsed_time3])
            x.close()

            counter += 1
            newcontents = os.listdir(watchdir)
            added = set(newcontents).difference(contents)           
            contents = newcontents
            index += 1
            #ADD CODE TO TO AUTOMATICALLY COLLECT HOURS

        contents = newcontents
    time.sleep(1)
os.system("py data_combiner.py")