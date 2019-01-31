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
import json
import order
import os
import parser
import reg
import stats
# import template
from nmt import NMT

def run(entry_path, set_path, en_path, de_path, _set):
    entryset = p.load(open(entry_path))
    if de_path != '':
        nmt = NMT(entryset, _set) # translate to german
        entryset = nmt.postprocess()
        entryset = order.run(entryset, 'de') # order german

    # referring expressions
    entryset = reg.run(entryset, 'en')

    lexsize, templates, templates_de, entities, references = stats.run(entryset)

    # run xml generator
    parser.run_generator(entryset=entryset, input_dir=set_path, output_dir=en_path, lng='en')
    if de_path != '':
        parser.run_generator(entryset=entryset, input_dir=set_path, output_dir=de_path, lng='de')

    # extract and generate templates based on sentence segmentation
    # en_temp = template.run(entryset)
    # json.dump(en_temp, open(os.path.join(en_path, 'templates.json'), 'w'), indent=4, separators=(',', ': '))
    #
    # de_temp = template.run(entryset, 'de')
    # json.dump(de_temp, open(os.path.join(de_path, 'templates.json'), 'w'), indent=4, separators=(',', ': '))
    return lexsize, templates, templates_de, entities, references

if __name__ == '__main__':
    FINAL_PATH = 'final/v1.2'
    if not os.path.exists(FINAL_PATH):
        os.mkdir(FINAL_PATH)

    EN_PATH = 'final/v1.2/en'
    if not os.path.exists(EN_PATH):
        os.mkdir(EN_PATH)

    DE_PATH = 'final/v1.2/de'
    if not os.path.exists(DE_PATH):
        os.mkdir(DE_PATH)

    # TRAINSET
    print 'Preparing trainset...'
    TRAIN_PATH = 'corpus/delexicalized/v1.2/train'
    ENTRY_PATH = 'corpus/train.cPickle'
    _set = 'train'

    EN_TRAIN_PATH = 'final/v1.2/en/train'
    if not os.path.exists(EN_TRAIN_PATH):
        os.mkdir(EN_TRAIN_PATH)

    DE_TRAIN_PATH = 'final/v1.2/de/train'
    if not os.path.exists(DE_TRAIN_PATH):
        os.mkdir(DE_TRAIN_PATH)
    lexsize, templates, templates_de, entities, references = run(entry_path=ENTRY_PATH, set_path=TRAIN_PATH, en_path=EN_TRAIN_PATH, de_path=DE_TRAIN_PATH, _set=_set)

    # DEVSET
    print 'Preparing devset...'
    DEV_PATH = 'corpus/delexicalized/v1.2/dev'
    ENTRY_PATH = 'corpus/dev.cPickle'
    _set = 'dev'

    EN_DEV_PATH = 'final/v1.2/en/dev'
    if not os.path.exists(EN_DEV_PATH):
        os.mkdir(EN_DEV_PATH)

    DE_DEV_PATH = 'final/v1.2/de/dev'
    if not os.path.exists(DE_DEV_PATH):
        os.mkdir(DE_DEV_PATH)
    lexsize2, templates2, templates_de2, entities2, references2 = run(entry_path=ENTRY_PATH, set_path=DEV_PATH, en_path=EN_DEV_PATH, de_path=DE_DEV_PATH, _set=_set)
    lexsize += lexsize2
    templates.extend(templates2)
    templates_de.extend(templates_de2)
    entities.extend(entities2)
    references.extend(references2)

    # TESTSET
    print 'Preparing testset...'
    TEST_PATH = 'corpus/delexicalized/v1.2/test'
    ENTRY_PATH = 'corpus/test.cPickle'
    _set = 'test'

    EN_TEST_PATH = 'final/v1.2/en/test'
    if not os.path.exists(EN_TEST_PATH):
        os.mkdir(EN_TEST_PATH)

    DE_TEST_PATH = ''
    lexsize3, templates3, templates_de3, entities3, references3 = run(entry_path=ENTRY_PATH, set_path=TEST_PATH, en_path=EN_TEST_PATH, de_path=DE_TEST_PATH, _set=_set)
    lexsize += lexsize3
    templates.extend(templates3)
    templates_de.extend(templates_de3)
    entities.extend(entities3)
    references.extend(references3)

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
