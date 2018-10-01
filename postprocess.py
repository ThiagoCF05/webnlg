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
import stats
from nmt import NMT

def run(entry_path, set_path, en_path, de_path, _set):
    entryset = p.load(open(entry_path))
    nmt = NMT(entryset, _set) # translate to german
    entryset = nmt.postprocess()
    entryset = order.run(entryset, 'de') # order german

    # referring expressions
    entryset = reg.run(entryset, 'en')

    lexsize, templates, templates_de, entities, references = stats.run(entryset)

    # run xml generator
    parser.run_generator(entryset=entryset, input_dir=set_path, output_dir=en_path, lng='en')
    parser.run_generator(entryset=entryset, input_dir=set_path, output_dir=de_path, lng='de')
    return lexsize, templates, templates_de, entities, references

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
    lexsize, templates, templates_de, entities, references = run(entry_path=ENTRY_PATH, set_path=TRAIN_PATH, en_path=EN_TRAIN_PATH, de_path=DE_TRAIN_PATH, _set=_set)

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
    lexsize2, templates2, templates_de2, entities2, references2 = run(entry_path=ENTRY_PATH, set_path=DEV_PATH, en_path=EN_DEV_PATH, de_path=DE_DEV_PATH, _set=_set)
    lexsize += lexsize2
    templates.extend(templates2)
    templates_de.extend(templates_de2)
    entities.extend(entities2)
    references.extend(references2)

    print('Number of texts: ', lexsize)
    print('English Templates: ', len(set(templates)))
    print('German Templates:', len(set(templates_de)))

    print('Number of Entities: ', len(set(entities)))
    print('References:', len(references))
    names = len(filter(lambda reference: reference.reftype == 'name', references))
    print('Names: ', names)
    pronouns = len(filter(lambda reference: reference.reftype == 'pronoun', references))
    print('Pronouns: ', pronouns)
    descriptions = len(filter(lambda reference: reference.reftype == 'description', references))
    print('Descriptions: ', descriptions)
    demonstratives = len(filter(lambda reference: reference.reftype == 'demonstrative', references))
    print('Demonstratives: ', demonstratives)