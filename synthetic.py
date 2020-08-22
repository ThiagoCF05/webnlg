__author__='thiagocastroferreira'

import os
import parser
import json

from SPARQLWrapper import SPARQLWrapper, JSON

# LOAD
PATH = 'data/v1.5/en/train'
entryset = parser.run_parser(PATH)

PATH = 'data/v1.5/en/dev'
entryset.extend(parser.run_parser(PATH))

PATH = 'data/v1.5/en/test'
entryset.extend(parser.run_parser(PATH))

# SELECT TEMPLATES OF SIZE 1
entryset1 = [entry for entry in entryset if entry.size == "1"]

pred2modpred = {}
templates = {}
for entry in entryset1:
    category = entry.category
    if category not in templates:
        templates[category] = {}
        pred2modpred[category] = {}

    for i, triple in enumerate(entry.originaltripleset):
        pred2modpred[category][triple.predicate] = entry.modifiedtripleset[i].predicate

    triple = entry.modifiedtripleset[0]
    entitymap = {}
    entitymap['AGENT-1'] = triple.subject
    entitymap['PATIENT-1'] = triple.object
    triple = ('AGENT-1', entry.originaltripleset[0].predicate, 'PATIENT-1')
    if triple not in templates[category]:
        templates[category][triple] = []

    for lexEntry in entry.lexEntries:
        templates[category][triple].append(lexEntry.template)

for category in templates:
    for triple in templates[category]:
        templates[category][triple] = list(set(templates[category][triple]))


# VERBALIZE TEMPLATES OF SIZE 1
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

new_entryset = []
for category in templates:
    print(category)
    for triple in templates[category]:
        pred = triple[1]
        try:
            sparql.setQuery("""
                SELECT ?subj ?obj
                WHERE { ?subj dbo:PREDICATE ?obj . }
                LIMIT 10
            """.replace('PREDICATE', pred))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                subj_uri = result['subj']['value']
                subj = subj_uri.split('/')[-1]
                obj_uri = result['obj']['value']
                obj = obj_uri.split('/')[-1]
                new_triple = (subj, pred, obj)

                new_entry = {
                    'category': category,
                    'triples': new_triple,
                    'size': "1",
                    'templates': []
                }

                # TEMPLATE GENERATION
                for template in templates[category][triple]:
                    ref = subj.replace('_', ' ').strip()
                    template = template.replace('AGENT-1', ref)
                    ref = obj.replace('_', ' ').strip()
                    template = template.replace('PATIENT-1', ref)
                    new_entry['templates'].append(template)
                new_entryset.append(new_entry)
        except:
            print('ERROR')

json.dump(new_entryset, open('data/1triples.json', 'w'), separators=(',', ':'), sort_keys=True, indent=4)


sparql = SPARQLWrapper("http://dbpedia.org/sparql")

new_entryset = json.load(open('data/1triples.json'))
# SELECT TEMPLATES OF SIZE 2

for size in range(2, 8):
    data = []
    fentryset = [entry for entry in entryset if entry.size == str(size)]
    for i, entry in enumerate(fentryset):
        print('Progress: ', round(i / len(fentryset), 2), i, end='\r')
        category = entry.category

        # delexicalized triples: get the triples in a delexicalized form
        entitymap = entry.entitymap_to_dict()
        entity2tag = { item[1]:item[0] for item in entitymap.items() }

        try:
            delexicalized = []
            select = []
            for i, triple in enumerate(entry.modifiedtripleset):
                subj = entity2tag[triple.subject].replace('-', '_')

                pred = entry.originaltripleset[i].predicate
                obj = entity2tag[triple.object].replace('-', '_')
                delexicalized.append((subj, pred, obj))

            delexicalized = tuple(sorted(delexicalized))

            # select first triple based on the verbalizations of 1 triple
            first_triple = delexicalized[0]
            pred = first_triple[1]
            f = [w for w in new_entryset if w['triples'][1] == pred and w['category'] == category]
            for ftriple in f:
                entitymap = { first_triple[0]: ftriple['triples'][0], first_triple[2]: ftriple['triples'][2] }
                triples = [ftriple['triples']] + list(delexicalized)[1:]

                # entitymap complete
                for i, triple in enumerate(triples):
                    if triple[0] in entitymap:
                        triples[i] = (entitymap[triple[0]], triple[1], triple[2])
                    elif triple[2] in entitymap:
                        triples[i] = (triple[0], triple[1], entitymap[triple[2]])

                # SPARQL complete
                select, where = [], []
                for triple in triples:
                    subj, pred, obj = triple

                    sparql_subj = '<http://dbpedia.org/resource/'+subj+ '>'
                    sparql_obj = '<http://dbpedia.org/resource/'+obj+ '>'
                    if subj.split('_')[0] in ['AGENT', 'BRIDGE']:
                        select.append('?' + subj)
                        sparql_subj = '?' + subj
                    if obj.split('_')[0] in ['PATIENT', 'BRIDGE']:
                        select.append('?' + obj)
                        sparql_obj = '?' + obj

                    where.append(' '.join([sparql_subj, 'dbo:' + pred, sparql_obj, '.']))
                where = '\n'.join(where)

                select = ', '.join(list(set(select)))
                query = """SELECT _SELECT_ WHERE { _WHERE_ }""".replace('_SELECT_', select).replace('_WHERE_', where)
                try:
                    sparql.setQuery(query)
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                    for result in results["results"]["bindings"]:
                        for tag in result:
                            entity = result[tag]['value'].split('/')[-1]
                            entitymap[tag] = entity
                            for i, triple in enumerate(triples):
                                if tag == triple[0]:
                                    triples[i] = (entity, triple[1], triple[2])
                                elif tag == triple[2]:
                                    triples[i] = (triple[0], triple[1], entity)

                    new_entry = {
                        'category': category,
                        'triples': tuple(triples),
                        'size': str(size),
                        'templates': []
                    }

                    # For the triples completed, verbalize the templates
                    if len(results["results"]["bindings"]) > 0:
                        for lexEntry in entry.lexEntries:
                            template = lexEntry.template

                            for reference in sorted(lexEntry.references, key= lambda x: x.number):
                                tag = reference.tag
                                entity = entitymap[tag.replace('-', '_')]
                                reftype = reference.reftype
                                regex = reference.refex

                                if reftype in ['name', 'description']:
                                    ref = entity.replace('_', ' ').strip()
                                    template = template.replace(tag, ref, 1)
                                elif reftype == 'pronoun':
                                    if regex.lower().strip() in ['he', 'she']:
                                        pronoun = 'he'
                                        sparql.setQuery("""
                                            SELECT ?gender
                                            WHERE { dbr:ENTITY foaf:gender ?gender . }
                                        """.replace('ENTITY', entity))
                                        sparql.setReturnFormat(JSON)
                                        results = sparql.query().convert()
                                        for result in results["results"]["bindings"]:
                                            if 'gender' in result:
                                                if result['gender']['value'] == 'female':
                                                    pronoun = 'she'
                                        template = template.replace(tag, pronoun, 1)
                                    elif regex.lower().strip() in ['it']:
                                        template = template.replace(tag, 'it', 1)
                                    elif regex.lower().strip() in ['his', 'her']:
                                        pronoun = 'his'
                                        sparql.setQuery("""
                                            SELECT ?gender
                                            WHERE { dbr:ENTITY foaf:gender ?gender . }
                                        """.replace('ENTITY', entity))
                                        sparql.setReturnFormat(JSON)
                                        results = sparql.query().convert()
                                        for result in results["results"]["bindings"]:
                                            if 'gender' in result:
                                                if result['gender']['value'] == 'female':
                                                    pronoun = 'her'
                                        template = template.replace(tag, pronoun, 1)
                                    elif regex.lower().strip() in ['its']:
                                        template = template.replace(tag, 'its', 1)
                            new_entry['templates'].append(template)
                except:
                    print('ERROR')
            if len(new_entry['templates']) > 0:
                data.append(new_entry)
        except:
            print('INITIAL ERROR')

    json.dump(data, open('data/' + str(size) + 'triples.json', 'w'), separators=(',', ':'), sort_keys=True, indent=4)