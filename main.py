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

import csv
import os

parser = argparse.ArgumentParser()
parser.add_argument('--epochs', type = int, default = 1000)
parser.add_argument('--batch_size', type = int, default = 32)
parser.add_argument('--model', type = str)
args = parser.parse_args()

def train(model):
    optimizer = optim.Adam(model.parameters(), lr = 1e-3)
    #Call dataloader
    data_iter = data_loader.get_loader(batch_size = args.batch_size)
    #print(data_iter)

    for epoch in range(args.epochs):
        model.train()

        run_loss = 0.0

        for idx, data in enumerate(data_iter):
            data = utils.to_var(data)
            ret = model.run_on_batch(data, optimizer)

            run_loss += ret['loss'].data

            print ('\r Progress epoch {}, {:.2f}%, average loss {}'.format(epoch, (idx + 1) * 100.0 / len(data_iter), run_loss / (idx + 1.0)))
            

        if epoch % 1 == 0:
            #evaluate(model, data_iter)
            preds, labels, eval_data, imputation_data = evaluate(model, data_iter)
            #print(len(eval_data)) #EVAL_DATA LENGTH IS 29
            #print(len(data_iter))
    #added code by soheil to save the imputed data

    #end added code by soheil

def evaluate(model, val_iter):
    model.eval()

    labels = []
    preds = []

    evals = []
    imputations = []

    eval_data = []
    imputation_data = []

    label_data = []
    pred_data = []

    for idx, data in enumerate(val_iter):
        data = utils.to_var(data)
        ret = model.run_on_batch(data, None)

        pred = ret['predictions'].data.cpu().numpy()
        label = ret['labels'].data.cpu().numpy()
        is_train = ret['is_train'].data.cpu().numpy()

        eval_masks = ret['eval_masks'].data.cpu().numpy()
        eval_ = ret['evals'].data.cpu().numpy()
        imputation = ret['imputations'].data.cpu().numpy()

        evals += eval_[np.where(eval_masks == 1)].tolist()
        imputations += imputation[np.where(eval_masks == 1)].tolist()

        label_data += label.tolist()
        pred_data += pred.tolist()
        
        # collect test label & prediction
        pred = pred[np.where(is_train == 0)]
        label = label[np.where(is_train == 0)]

        labels += label.tolist()
        preds += pred.tolist()
        
        #added code by soheil to save the imputed data
        eval_data += eval_.tolist()
        imputation_data += imputation.tolist()
        
        #print(len(eval_data))
    with open('./json/data.txt', 'w') as data_file:
        for item in eval_data:
            data_file.write("%s\n" % item)
    #    data_file.write("%s\n" % eval_)
    with open('./json/imputations.txt', 'w') as imputed_file:
        for item in imputation_data:
            imputed_file.write("%s\n" % item)
        #imputed_file.write("%s\n" % imputation)
    with open('./json/predictions.txt', 'w') as predicted_file:
        predicted_file.write("%s\n" % preds)
    with open('./json/labels.txt', 'w') as labels_file:
        labels_file.write("%s\n" % labels)

    np.save('./brits_label.npy', label_data)
    np.save('./brits_data.npy', imputation_data)

    labels = np.asarray(labels).astype('int32')
    preds = np.asarray(preds)
    print ('AUC {}'.format(metrics.roc_auc_score(labels, preds)))
    evals = np.asarray(evals)
    imputations = np.asarray(imputations)
    print ('MAE', np.abs(evals - imputations).mean())
    print ('MRE', np.abs(evals - imputations).sum() / np.abs(evals).sum())

    #Create outfile
    outfile = "./result/data1.csv"
    print("Processing data")
    x = open(outfile, "a", newline='')
    csv_writer = csv.writer(x)
    #Write header + patient specific classifiers
    csv_writer.writerow([metrics.roc_auc_score(labels, preds), np.abs(evals - imputations).mean(), np.abs(evals - imputations).sum() / np.abs(evals).sum()] )
    x.close()
    return preds, labels, eval_data, imputation_data

def run():
    model = getattr(models, args.model).Model()

    if torch.cuda.is_available():
        model = model.cuda()

    train(model)

if __name__ == '__main__':
    run()
