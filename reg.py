__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 15/07/2018
Description:
    Extract referring expressions by overlapping texts and their respective delexicalized templates.
    For English and German.

    PYTHON VERSION: 2.7
"""

import nltk
import re

from entry import Reference

def process_template(template):
    '''
    Return previous and subsequent tokens from a specific tag in a template
    :param template:
    :return:
    '''
    stemplate = template.split()

    tag = ''
    pre_tag, pos_tag, i = [], [], 0
    for token in stemplate:
        i += 1
        if token.split('-')[0] in ['AGENT', 'PATIENT', 'BRIDGE']:
            tag = token
            for pos_token in stemplate[i:]:
                if pos_token.split('-')[0] in ['AGENT', 'PATIENT', 'BRIDGE']:
                    break
                else:
                    pos_tag.append(pos_token)
            break
        else:
            pre_tag.append(token)
    return pre_tag, tag, pos_tag

def extract_references(text, template, entitymap):
    text = re.sub(r'([.,;:?!\'\(\)])', r' \1', text)
    text = re.sub(r'(.+)-([1-9]+)-(.+)', r'\1-\2 -\3', text, flags=re.U)

    template = re.sub(r'([.,;:?!\'\(\)])', r' \1', template)
    template = re.sub(r'(.+)-([1-9]+)-(.+)', r'\1-\2 -\3', template, flags=re.U)

    refexes = []

    isOver = False
    number = 0
    while not isOver:
        pre_tag, tag, pos_tag = process_template(template)
        number += 1

        if tag == '':
            isOver = True
        else:
            # Look for reference from 5-gram to 2-gram
            i, f = 5, []
            while i > 1:
                begin = ' '.join(i * ['BEGIN'])
                text = begin + ' ' + text
                template = begin + ' ' + template
                pre_tag, tag, pos_tag = process_template(template)

                regex = re.escape(' '.join(pre_tag[-i:]).strip()) + ' (.+?) ' + re.escape(' '.join(pos_tag[:i]).strip())
                f = re.findall(regex, text)

                template = template.replace('BEGIN', '').strip()
                text = text.replace('BEGIN', '').strip()
                i -= 1

                if len(f) == 1:
                    break

            if len(f) > 0:
                # DO NOT LOWER CASE HERE!!!!!!
                template = template.replace(tag, f[0], 1)
                refex = f[0]

                # Do not include literals
                try:
                    entity = entitymap[tag]
                except:
                    entity = ''
                    print('entity map exception...', tag)

                refex = refex.split()
                refexes.append(Reference(tag=tag, entity=entity, refex=' '.join(refex), number=number))
            else:
                template = template.replace(tag, ' ', 1)
    return refexes

def run(entryset, lng='en'):
    for entry in entryset:
        for lex in entry.lexEntries:
            if lng == 'en':
                lex.references = extract_references(lex.text, lex.template, entry.entitymap_to_dict())
            else:
                lex.references_de = extract_references(lex.text_de, lex.template_de, entry.entitymap_to_dict())

    return entryset