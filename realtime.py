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

for filename in os.listdir('./raw/set-a'):
    # the patient data in PhysioNet contains 6-digits
    match = re.search('\d{6}', filename)
    if match:
        id_ = match.group()
        patient_ids.append(id_)

#Window 0
counter = 0
args = 'py main.py --epochs 1 --batch_size 32 --model brits'
print("Loading Data")
os.system('py input_process.py')
os.system(args)
print("Running reverse_input_process_temp")
os.system('py reverse_input_process_temp.py')

outfile = "./raw/set-a/combined.txt"

headerName = "./imputed/000000.csv"
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

os.remove("./raw/set-a/000000.txt")
os.rename(r"./raw/set-a/combined.txt",r"./raw/set-a/000000.txt")
os.remove("./imputed/000000.csv")
os.system('py random_forest.py')
print("Window " + str(counter) + " Complete")
counter += 1

watchdir = './raw/set-a'
contents = os.listdir(watchdir)
count = len(watchdir)
dirmtime = os.stat(watchdir).st_mtime

while True:
    newmtime = os.stat(watchdir).st_mtime
    if newmtime != dirmtime:
        dirmtime = newmtime
        newcontents = os.listdir(watchdir)
        added = set(newcontents).difference(contents)
        if added:
            print ("Files added: %s" %(" ".join(added)))
            for temp in added:
                break
            #Assumption the name becomes ... - Copy
            #Append Copy data to original
            fileName1 = "./raw/set-a/000000.txt"
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
            os.remove(fileName1)
            os.remove(fileName2)
            os.rename(r"./raw/set-a/combined.txt",r"./raw/set-a/000000.txt")
            print("Loading Data")
            os.system('py input_process.py')
            print("Training Network")
            os.system(args)
            print("Running reverse_input_process")
            os.system('py reverse_input_process_temp.py')

            outfile = "./raw/set-a/combined.txt"

            headerName = "./imputed/000000.csv"
            headerFile = open(headerName,"r")
            x = open(outfile, "a", newline='')
            csv_writer = csv.writer(x)
            for i in range (7):
                header_line = headerFile.readline().replace("\n","").split(",")
                csv_writer.writerow(header_line)
             
            for i in range ((counter+1) * 35):
                header_line = headerFile.readline().replace("\n","").split(",")
                csv_writer.writerow(header_line)


            x.close()
            headerFile.close()

            os.remove("./raw/set-a/000000.txt")
            os.rename(r"./raw/set-a/combined.txt",r"./raw/set-a/000000.txt")
            os.remove("./imputed/000000.csv")
            os.system('py random_forest.py')
            print("Window " + str(counter) + " Complete")

            counter += 1
            newcontents = os.listdir(watchdir)
            added = set(newcontents).difference(contents)           
            contents = newcontents
            #ADD CODE TO TO AUTOMATICALLY COLLECT HOURS




        removed = set(contents).difference(newcontents)
        
        if removed:
            print ("Files removed: %s" %(" ".join(removed)))

        contents = newcontents
    time.sleep(1)