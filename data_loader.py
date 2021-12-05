#Necessary packages
import os
import time

import ujson as json
import numpy as np
import pandas as pd

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

class MySet(Dataset):
    """Load complete data
    Args:
        --epochs 1 --batch_size 32 --model brits
    Returns:
        - rec
    """
    def __init__(self):
        super(MySet, self).__init__()
        self.content = open('./json/json').readlines()
        #Return evenly spaced values of the length of the dataset
        indices = np.arange(len(self.content))
        #Generate a uniform random sample from indices of size = length of dataset
        val_indices = np.random.choice(indices, len(self.content) // 5)

        self.val_indices = set(val_indices.tolist())

    #Helper method for length
    def __len__(self):
        return len(self.content)
    #Loads JSON data
    def __getitem__(self, idx):
        rec = json.loads(self.content[idx])
        #Masking vector to determine not observed/otherwise instance of data
        if idx in self.val_indices:
            rec['is_train'] = 0
        else:
            rec['is_train'] = 1
        return rec

def collate_fn(recs):
    forward = list(map(lambda x: x['forward'], recs))
    backward = list(map(lambda x: x['backward'], recs))

    def to_tensor_dict(recs):
        values = torch.FloatTensor(list(map(lambda r: list(map(lambda x: x['values'], r)), recs)))
        masks = torch.FloatTensor(list(map(lambda r: list(map(lambda x: x['masks'], r)), recs)))
        deltas = torch.FloatTensor(list(map(lambda r: list(map(lambda x: x['deltas'], r)), recs)))
        #forwards = torch.FloatTensor(list(map(lambda r: list(map(lambda x: x['forwards'], r)), recs)))

        evals = torch.FloatTensor(list(map(lambda r: list(map(lambda x: x['evals'], r)), recs)))
        eval_masks = torch.FloatTensor(list(map(lambda r: list(map(lambda x: x['eval_masks'], r)), recs)))

        #return {'values': values, 'forwards': forwards, 'masks': masks, 'deltas': deltas, 'evals': evals, 'eval_masks': eval_masks}
        return {'values': values, 'masks': masks, 'deltas': deltas, 'evals': evals, 'eval_masks': eval_masks}
    ret_dict = {'forward': to_tensor_dict(forward), 'backward': to_tensor_dict(backward)}

    ret_dict['labels'] = torch.FloatTensor(list(map(lambda x: x['label'], recs)))
    ret_dict['is_train'] = torch.FloatTensor(list(map(lambda x: x['is_train'], recs)))

    return ret_dict

def get_loader(batch_size = 64, shuffle = True):
    #Returns a batched and shuffled dataset
    data_set = MySet()
    data_iter = DataLoader(dataset = data_set, \
                              batch_size = batch_size, \
                              num_workers = 4, \
                              shuffle = shuffle, \
                              pin_memory = True, \
                              collate_fn = collate_fn
    )

    return data_iter
