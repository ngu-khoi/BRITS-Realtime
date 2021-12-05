import os
import time
import csv

start_time1 = time.time() # TRACKS LOADING
elapsed_time1 = time.time() - start_time1
start_time2 = time.time()
os.system('py main.py --epochs 1 --batch_size 32 --model brits')
elapsed_time2 = time.time() - start_time2
start_time3 = time.time()
os.system('py random_forest.py')
elapsed_time3 = time.time() - start_time3


# OUTFILE FOR ELAPSED TIMES - LOADING, TRAINING, AND CLASSIFYING
outfile = "./result/data3.csv"
print("Processing data")
x = open(outfile, "a", newline='')
csv_writer = csv.writer(x)
csv_writer.writerow([elapsed_time1, elapsed_time2, elapsed_time3])
x.close()


os.system('py data_combiner.py')