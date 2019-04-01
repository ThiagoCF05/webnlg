__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 28/06/2018
Description:
    Order the triples according to the respective delexicalized template

    PYTHON VERSION: 2.7
"""

import copy
import nltk
import re

def order(tripleset, template, entitymap):
    template = re.sub(r'(.+)-([1-9]+)-(.+)', r'\1-\2 -\3', template, flags=re.U)

    entitytag = dict(map(lambda item: (item[1], item[0]), entitymap.items()))
    tags = entitymap.keys()
    orderedtripleset = []

    antecedents = []
    for snt in nltk.sent_tokenize(template):
        orderedtripleset_snt = []
        for token in nltk.word_tokenize(snt):
            if token in tags:
                for antecedent in antecedents:
                    try:
                        candidates = list(filter(lambda triple: (entitytag[triple.subject].strip() == token.strip()
                                                            and entitytag[triple.object].strip() == antecedent.strip())
                                                            or (entitytag[triple.subject].strip() == antecedent.strip()
                                                            and entitytag[triple.object].strip() == token.strip()), tripleset))
                    except Exception as e:
                        print(e.message)
                        print(entitytag)
                        print(10 * '-')
                        candidates = []
                    if len(candidates) > 0:
                        candidate = candidates[0]
                        orderedtripleset_snt.append(candidate)
                        tripleset.remove(candidate)
                antecedents.append(token)
        orderedtripleset.append(orderedtripleset_snt)

    return orderedtripleset

def run(entryset, lng='en'):
    for entry in entryset:
        for lex in entry.lexEntries:
            if lng == 'en':
                lex.orderedtripleset = order(copy.deepcopy(entry.modifiedtripleset), lex.template, entry.entitymap_to_dict())
            else:
                lex.orderedtripleset_de = order(copy.deepcopy(entry.modifiedtripleset), lex.template_de, entry.entitymap_to_dict())

    return entryset