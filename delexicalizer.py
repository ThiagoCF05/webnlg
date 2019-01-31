__author__='thiagocastroferreira'

import copy
import nltk
import os
import parser_original as parser

from entry import *

def get_entitymap(triples):
    agents = []
    bridges = []
    patients = []
    visited = []

    for triple in triples:
        if triple.subject not in visited:
            agents.append(triple.subject)
            visited.append(triple.subject)
        else:
            if triple.subject in patients and triple.subject not in bridges:
                bridges.append(triple.subject)
                patients.remove(triple.subject)

        if triple.object not in visited:
            patients.append(triple.object)
            visited.append(triple.object)
        else:
            if triple.object in agents and triple.object not in bridges:
                bridges.append(triple.object)
                agents.remove(triple.object)

    entitymap = []
    for i, agent in enumerate(agents):
        tagentity = TagEntity(tag='AGENT-'+str(i+1), entity=agent)
        entitymap.append(tagentity)
    for i, bridge in enumerate(bridges):
        tagentity = TagEntity(tag='BRIDGE-'+str(i+1), entity=bridge)
        entitymap.append(tagentity)
    for i, patient in enumerate(patients):
        tagentity = TagEntity(tag='PATIENT-'+str(i+1), entity=patient)
        entitymap.append(tagentity)

    return entitymap

def delexicalize(entry):
    for lexEntry in entry.lexEntries:
        template = copy.copy(lexEntry.substring)
        template = ' '.join(nltk.word_tokenize(template))

        entitymap = entry.entitymap_to_dict()
        for tag in entitymap:
            refex = entitymap[tag].replace('_', ' ')
            template = template.replace(refex, tag)
        lexEntry.template = template
    return entry

if __name__ == '__main__':
    path = 'corpus/original/test/testdata_with_lex.xml'

    entryset = parser.parse(path)

    for i, entry in enumerate(entryset):
        entryset[i].entitymap = get_entitymap(entry.modifiedtripleset)

        entryset[i] = delexicalize(entryset[i])

        for lexEntry in entryset[i].lexEntries:
            print(lexEntry.substring)
            print(lexEntry.template)
            print(10 * '-')

    path = 'corpus/delexicalized/v1.2/test'
    if not os.path.exists(path):
        os.mkdir(path)

    sizes = set([entry.size for entry in entryset])
    categories = set([entry.category for entry in entryset])
    for size in sizes:
        ppath = os.path.join(path, str(size)+'triples')
        if not os.path.exists(ppath):
            os.mkdir(ppath)

        size_entries = [entry for entry in entryset if entry.size == size]

        for category in categories:
            category_entries = [entry for entry in size_entries if entry.category == category]

            if len(category_entries) > 0:
                fname = category + '.xml'
                parser.generate(entries=category_entries, fname=os.path.join(ppath, fname))
