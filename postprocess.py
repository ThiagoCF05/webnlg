__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 15/07/2018
Description:
    Postprocessing script: for train and dev sets, postprocess after translation, create xml final file
    and extract referring expressions

    PYTHON VERSION: 2.7
"""

import cPickle as p
import order
import os
import parser
import reg
from nmt import NMT

def run(entry_path, set_path, en_path, de_path, _set):
    entryset = p.load(open(entry_path))
    nmt = NMT(entryset, _set) # translate to german
    entryset = nmt.postprocess()
    entryset = order.run(entryset, 'de') # order german

    # referring expressions
    entryset = reg.run(entryset, 'en')
    # entryset = reg.run(entryset, 'de')

    # run xml generator
    parser.run_generator(entryset=entryset, input_dir=set_path, output_dir=en_path, lng='en')
    parser.run_generator(entryset=entryset, input_dir=set_path, output_dir=de_path, lng='de')

if __name__ == '__main__':
    DEV_PATH = 'corpus/delexicalized/dev'

    FINAL_PATH = 'final'
    if not os.path.exists(FINAL_PATH):
        os.mkdir(FINAL_PATH)

    EN_PATH = 'final/en'
    if not os.path.exists(EN_PATH):
        os.mkdir(EN_PATH)

    DE_PATH = 'final/de'
    if not os.path.exists(DE_PATH):
        os.mkdir(DE_PATH)

    # TRAINSET
    print 'Preparing trainset...'
    TRAIN_PATH = 'corpus/delexicalized/train'
    ENTRY_PATH = 'corpus/train.cPickle'
    _set = 'train'

    EN_TRAIN_PATH = 'final/en/train'
    if not os.path.exists(EN_TRAIN_PATH):
        os.mkdir(EN_TRAIN_PATH)

    DE_TRAIN_PATH = 'final/de/train'
    if not os.path.exists(DE_TRAIN_PATH):
        os.mkdir(DE_TRAIN_PATH)
    run(entry_path=ENTRY_PATH, set_path=TRAIN_PATH, en_path=EN_TRAIN_PATH, de_path=DE_TRAIN_PATH, _set=_set)

    # DEVSET
    print 'Preparing devset...'
    DEV_PATH = 'corpus/delexicalized/dev'
    ENTRY_PATH = 'corpus/dev.cPickle'
    _set = 'dev'

    EN_DEV_PATH = 'final/en/dev'
    if not os.path.exists(EN_DEV_PATH):
        os.mkdir(EN_DEV_PATH)

    DE_DEV_PATH = 'final/de/dev'
    if not os.path.exists(DE_DEV_PATH):
        os.mkdir(DE_DEV_PATH)
    run(entry_path=ENTRY_PATH, set_path=DEV_PATH, en_path=EN_DEV_PATH, de_path=DE_DEV_PATH, _set=_set)

    # os.remove(ENTRY_PATH)