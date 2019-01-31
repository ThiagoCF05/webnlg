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
from xml.dom import minidom

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
            e1, pred, e2 = otriple.substring.split(' | ')
            originaltripleset.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))

        modifiedtripleset = []
        mtripleset = entry.find('modifiedtripleset')
        for mtriple in mtripleset:
            e1, pred, e2 = mtriple.substring.split(' | ')

            modifiedtripleset.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))

        lexList = []
        lexEntries = entry.findall('lex')
        for lex in lexEntries:
            comment = lex.attrib['comment']
            lid = lex.attrib['lid']
            text = lex.substring
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

def generate(entries, fname):
    root = ET.fromstring('<?xml version="1.0" ?><benchmark><entries></entries></benchmark>')

    xml_entries = root.find('entries')
    for entry in entries:
        attrib = {'category': entry.category, 'eid': entry.eid, 'size': entry.size}
        xml_entry = ET.SubElement(xml_entries, 'entry', attrib)

        xml_original = ET.SubElement(xml_entry, 'originaltripleset')
        for triple in entry.originaltripleset:
            xml_triple = ET.SubElement(xml_original, 'otriple')
            xml_triple.substring = triple.subject + ' | ' + triple.predicate + ' | ' + triple.object

        xml_modified = ET.SubElement(xml_entry, 'modifiedtripleset')
        for triple in entry.modifiedtripleset:
            xml_triple = ET.SubElement(xml_modified, 'otriple')
            xml_triple.substring = triple.subject + ' | ' + triple.predicate + ' | ' + triple.object

        xml_entitymap = ET.SubElement(xml_entry, 'entitymap')
        for tagentity in entry.entitymap:
            xml_tagentity = ET.SubElement(xml_entitymap, 'entity')
            xml_tagentity.substring = tagentity.tag + ' | ' + tagentity.entity


        for lexEntry in entry.lexEntries:
            attrib = { 'comment': 'good', 'lid': lexEntry.lid}
            xml_lex = ET.SubElement(xml_entry, 'lex', attrib)

            xml_text = ET.SubElement(xml_lex, 'text')
            xml_text.substring = lexEntry.substring

            xml_template = ET.SubElement(xml_lex, 'template')
            xml_template.substring = lexEntry.template

    rough_string = ET.tostring(root, encoding='utf-8', method='xml')
    xml = minidom.parseString(rough_string).toprettyxml(indent="\t")

    with open(fname, 'w') as f:
        f.write(xml.encode('utf-8'))