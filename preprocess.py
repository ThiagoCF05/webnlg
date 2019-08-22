__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 15/07/2018
Description:
    Preprocessing script: for train and dev sets, parse files, order english part and preprocess to be translated it

    PYTHON VERSION: 2.7
"""

import order
import parser
from nmt import NMT

import cPickle as p

def run(set_path, entry_path, _set):
    entryset = parser.run_parser(set_path) # parse
    entryset = order.run(entryset, 'en') # order english part
    # nmt = NMT(entryset, _set) # translate to german
    # nmt.preprocess()

    p.dump(entryset, open(entry_path, 'w'))

if __name__ == '__main__':
    print('Preparing testset....')
    TRAIN_PATH = 'dependencies/delexicalized/v1.4/test'
    ENTRY_PATH = 'dependencies/test.cPickle'
    _set = 'test'
    run(TRAIN_PATH, ENTRY_PATH, _set)

    print('Preparing devset...')
    DEV_PATH = 'dependencies/delexicalized/v1.4/dev'
    ENTRY_PATH = 'dependencies/dev.cPickle'
    _set = 'dev'
    run(DEV_PATH, ENTRY_PATH, _set)

    print('Preparing trainset....')
    TRAIN_PATH = 'dependencies/delexicalized/v1.4/train'
    ENTRY_PATH = 'dependencies/train.cPickle'
    _set = 'train'
    run(TRAIN_PATH, ENTRY_PATH, _set)