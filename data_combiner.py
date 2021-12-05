import csv
import os

# PREPARE FILE WRITERS
fileName1 = "./result/data1.csv"
fileName2 = "./result/data2.csv"
fileName3 = "./result/data3.csv"
outfile = "./result/finaldata.csv"

x = open(outfile, "a", newline='')
csv_writer = csv.writer(x)

# WRITE HEADER
csv_writer.writerow(["WINDOW TYPE","AUC", "MAE", "MRE", "RANDOM_FOREST: Label 0 Prediction", "RANDOM_FOREST: Label 1 Prediction", "RANDOM_FOREST: AUC", "ELAPSED_TIME: Loading Data", "ELAPSED_TIME: BRITS Training + Imputation of data", "ELAPSED_TIME: Random Forest"])

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


file1 = open(fileName1,"r")
file2 = open(fileName2,"r")
file3 = open(fileName3,"r")
line1 = file1.readline()
line2 = file2.readline()
line3 = file3.readline()
line_details = []

counter = 0
while line1:
	rows = [[hourly_directories[counter]] + line1.replace("\n","").split(",") + line2.replace("\n","").split(",") + line3.replace("\n","").split(",")]
	for row in rows:
		csv_writer.writerow(row)
	line1 = file1.readline()
	line2 = file2.readline()
	line3 = file3.readline()
	counter += 1
x.close()
file1.close()
file2.close()
file3.close()