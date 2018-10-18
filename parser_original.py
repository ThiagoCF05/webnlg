__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 18/10/2018
Description:
    Parser for the WebNLG corpus in the INLG hackathon

    PYTHON VERSION: 2.7
"""

import os
import json
import xml.etree.ElementTree as ET

from entry import *

def parse(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    entries = root.find('entries')

    dataset = []

    for entry in entries:
        eid = entry.attrib['eid']
        size = entry.attrib['size']
        category = entry.attrib['category']

        originaltripleset = []
        otripleset = entry.find('originaltripleset')
        for otriple in otripleset:
            e1, pred, e2 = otriple.text.split(' | ')
            originaltripleset.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))

        modifiedtripleset = []
        mtripleset = entry.find('modifiedtripleset')
        for mtriple in mtripleset:
            e1, pred, e2 = mtriple.text.split(' | ')

            modifiedtripleset.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))

        lexList = []
        lexEntries = entry.findall('lex')
        for lex in lexEntries:
            comment = lex.attrib['comment']
            lid = lex.attrib['lid']
            text = lex.text
            template = ''

            lexList.append(Lex(comment=comment, lid=lid, text=text, template=template))

        dataset.append(Entry(eid=eid, size=size, category=category, originaltripleset=originaltripleset, modifiedtripleset=modifiedtripleset, entitymap={}, lexEntries=lexList))
    return dataset

def parse_json(json_file):
    dataset = []
    entries = json.load(open(json_file))['entries']
    for entry in entries:
        key = list(entry.keys())[0]
        eid = entry[key]['xml_id']
        size = entry[key]['size']
        category = entry[key]['category']

        originaltripleset = []
        otripleset = entry[key]['originaltriplesets']['originaltripleset'][0]
        for otriple in otripleset:
            e1 = otriple['subject']
            pred = otriple['property']
            e2 = otriple['object']
            originaltripleset.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))

        modifiedtripleset = []
        mtripleset = entry[key]['modifiedtripleset']
        for mtriple in mtripleset:
            e1 = mtriple['subject']
            pred = mtriple['property']
            e2 = mtriple['object']
            modifiedtripleset.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))

        lexList = []
        lexEntries = entry[key]['lexicalisations']
        for lex in lexEntries:
            comment = lex['comment']
            lid = lex['xml_id']
            text = lex['lex']
            lexList.append(Lex(comment=comment, lid=lid, text=text, template=''))

        dataset.append(Entry(eid=eid, size=size, category=category, originaltripleset=originaltripleset, modifiedtripleset=modifiedtripleset, entitymap={}, lexEntries=lexList))
    return dataset

def run_parser(set_path):
    entryset = []
    dirtriples = filter(lambda item: not str(item).startswith('.'), os.listdir(set_path))
    for dirtriple in dirtriples:
        fcategories = filter(lambda item: not str(item).startswith('.'), os.listdir(os.path.join(set_path, dirtriple)))
        for fcategory in fcategories:
            entryset.extend(list(parse(os.path.join(set_path, dirtriple, fcategory))))

    return entryset