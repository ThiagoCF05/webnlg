__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 15/07/2018
Description:
    Script to provide statistics about the dataset and the extracted information

    PYTHON VERSION: 2.7
"""

def run(entryset):
    print(10 * '*')
    print('Number of Sets: ', len(entryset))

    lexsize = 0
    templates, templates_de = [], []
    references, references_de = [], []
    entities = []
    for entry in entryset:
        lexsize += len(entry.lexEntries)

        for lex in entry.lexEntries:
            templates.append(lex.template)
            templates_de.append(lex.template_de)

            references.extend(lex.references)
            # references_de.extend(lex.references_de)

            entities.extend(list(map(lambda reference: reference.entity, lex.references)))

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