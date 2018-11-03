__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 03/11/2018
Description:
    Extract templates based on sentence segmentation and the ordering script

    PYTHON VERSION: 2.7
"""

import cPickle as p
import collections
import copy
import json
import order

from stanfordcorenlp import StanfordCoreNLP

STANFORD_PATH=r'/home/tcastrof/workspace/stanford/stanford-corenlp-full-2018-02-27'
props = {'annotators': 'tokenize,ssplit','pipelineLanguage':'en','outputFormat':'json'}

def format(tripleset, template, tagentity):
    entitytag = dict(map(lambda x: (x[1], x[0]), tagentity.items()))

    triples = []
    entitymap = {}
    entities = 1
    for triple in tripleset:
        subject = entitytag[triple.subject]
        if triple.subject not in entitymap:
            entitymap[triple.subject] = 'ENTITY-' + str(entities)
            entities += 1
        new_subject = entitymap[triple.subject]

        object_ = entitytag[triple.object]
        if triple.object not in entitymap:
            entitymap[triple.object] = 'ENTITY-' + str(entities)
            entities += 1
        new_object = entitymap[triple.object]
        triples.append(new_subject + ' | ' + triple.predicate + ' | ' + new_object)

        template = template.replace(subject, new_subject).replace(object_, new_object)

    return triples, template

def extract(tripleset, template, entitymap, corenlp):
    sentences = []
    try:
        out = corenlp.annotate(template.strip(), properties=props)
        out = json.loads(out)

        for snt in out['sentences']:
            sentence = ' '.join(map(lambda w: w['originalText'], snt['tokens']))
            sentences.append(sentence)
    except:
        print('Parsing error...')

    templates = []
    for i in range(len(sentences)):
        idx = i+1

        for j, snt in enumerate(sentences):
            snts = sentences[j:j+idx]
            if len(snts) == idx:
                template_ = ' '.join(snts)
                orderedset = order.order(copy.deepcopy(tripleset), template_, entitymap)

                orderedset_, template_ = format(orderedset, template_, entitymap)
                templates.append((orderedset_, template_))

    return templates

def group(templates):
    result = {}

    for template in templates:
        tripleset = template[0]
        idx = len(tripleset)
        if idx not in result:
            result[idx] = {}
        text = template[1]
        if tuple(tripleset) not in result[idx]:
            result[idx][tuple(tripleset)] = []
        result[idx][tuple(tripleset)].append(text)

    fjson = {'sizes': {}}
    for idx in result:
        fjson['sizes'][idx] = {'entries':[]}
        for tripleset in result[idx]:
            templates = map(lambda x: dict([('template', x[0]), ('frequency', x[1])]), collections.Counter(result[idx][tripleset]).items())
            fjson['sizes'][idx]['entries'].append({
                'orderedset': list(tripleset),
                'templates': templates
            })

    return fjson

def run(entryset, lng='en'):
    corenlp = StanfordCoreNLP(STANFORD_PATH)

    templates = []
    for i, entry in enumerate(entryset):
        if i % 100 == 0:
            print('Progress: ', round((float(i) / len(entryset)) * 100, 2))
        for lex in entry.lexEntries:
            if lng == 'en':
                 t = extract(copy.deepcopy(entry.modifiedtripleset), lex.template, entry.entitymap_to_dict(), corenlp)
            else:
                t = extract(copy.deepcopy(entry.modifiedtripleset), lex.template_de, entry.entitymap_to_dict(), corenlp)

            templates.extend(t)

    corenlp.close()

    return group(templates)

if __name__ == '__main__':
    entryset = p.load(open('corpus/dev.cPickle', 'rb'))
    run(entryset)