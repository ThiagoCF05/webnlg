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

    return lexsize, templates, templates_de, entities, references
