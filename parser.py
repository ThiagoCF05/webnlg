__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 24/07/2017
Description:
    Parse and generate the corpus in the xml format

    PYTHON VERSION: 2.7
"""

import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

from entry import *

def parse(in_file):
    tree = ET.parse(in_file)
    root = tree.getroot()

    entries = root.find('entries')

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

        entitymap = []
        mapping= entry.find('entitymap')
        for entitytag in mapping:
            tag, entity = entitytag.text.split(' | ')
            entitymap.append(TagEntity(tag=tag, entity=entity))

        lexList = []
        lexEntries = entry.findall('lex')
        for lex in lexEntries:
            comment = lex.attrib['comment']
            lid = lex.attrib['lid']

            try:
                orderedtripleset = []
                otripleset = lex.find('sortedtripleset')
                for snt in otripleset:
                    orderedtripleset_snt = []
                    for otriple in snt:
                        e1, pred, e2 = otriple.text.split(' | ')

                        orderedtripleset_snt.append(Triple(subject=e1.replace('\'', ''), predicate=pred, object=e2.replace('\'', '')))
                    orderedtripleset.append(orderedtripleset_snt)
            except:
                orderedtripleset = []

            try:
                text = lex.find('text').text
                if not text:
                    print('error text')
                    text = ''
            except:
                print('exception text')
                text = ''

            try:
                template = lex.find('template').text
                if not template:
                    print('error template')
                    template = ''
            except:
                print('exception template')
                template = ''

            lexList.append(Lex(comment=comment, lid=lid, text=text, template=template, orderedtripleset=orderedtripleset))

        yield Entry(eid=eid, size=size, category=category, originaltripleset=originaltripleset, \
                    modifiedtripleset=modifiedtripleset, entitymap=entitymap, lexEntries=lexList)

def run_parser(set_path):
    entryset = []
    dirtriples = filter(lambda item: not str(item).startswith('.'), os.listdir(set_path))
    for dirtriple in dirtriples:
        fcategories = filter(lambda item: not str(item).startswith('.'), os.listdir(os.path.join(set_path, dirtriple)))
        for fcategory in fcategories:
            entryset.extend(list(parse(os.path.join(set_path, dirtriple, fcategory))))

    return entryset

def generate(entryset, in_file, out_file, lng):
    tree = ET.parse(in_file)
    root = tree.getroot()

    entries = root.find('entries')

    for entry_xml in entries:
        eid = entry_xml.attrib['eid']
        size = int(entry_xml.attrib['size'])
        category = entry_xml.attrib['category']

        entitymap = entry_xml.find('entitymap')
        entry_xml.remove(entitymap)
        entitymap = ET.SubElement(entry_xml, 'entitymap')

        # remove double entries
        originaltriplesets = entry_xml.findall('originaltripleset')
        for originaltripleset in originaltriplesets[1:]:
            entry_xml.remove(originaltripleset)

        # remove double entries
        modifiedtriplesets = entry_xml.findall('modifiedtripleset')
        triples = [mtriple.text for mtriple in modifiedtriplesets[0]]
        for modifiedtripleset in modifiedtriplesets[1:]:
            entry_xml.remove(modifiedtripleset)
        modifiedtripleset = modifiedtriplesets[0]
        otriples = modifiedtripleset.findall('otriple')
        if len(otriples) > 0:
            for triple in triples:
                mtriple = ET.SubElement(modifiedtripleset, 'mtriple')
                mtriple.text = triple
            for otriple in modifiedtripleset.findall('otriple'):
                modifiedtripleset.remove(otriple)

        entry = list(filter(lambda entry: entry.eid==eid and entry.size==str(size) and entry.category==category, entryset))[0]

        tagentity = entry.entitymap_to_dict()
        for tag in sorted(tagentity.keys()):
            entity = tagentity[tag]
            entity_xml = ET.SubElement(entitymap, 'entity')
            entity_xml.text = tag + ' | ' + entity

        # process lexical entries
        lexEntries = entry_xml.findall('lex')
        for i, lexEntry_xml in enumerate(lexEntries):
            lexEntry_xml.text = ''
            text_xml = lexEntry_xml.find('text')
            if text_xml is not None:
                lexEntry_xml.remove(text_xml)
            template_xml = lexEntry_xml.find('template')
            if template_xml is not None:
                lexEntry_xml.remove(template_xml)
            # remove sortedtripleset
            orderedtripleset_xml = lexEntry_xml.find('sortedtripleset')
            if orderedtripleset_xml is not None:
                lexEntry_xml.remove(orderedtripleset_xml)
            # remove references
            references_xml = lexEntry_xml.find('references')
            if references_xml is not None:
                lexEntry_xml.remove(references_xml)

            # ordered triple set
            if lng == 'en':
                orderedtripleset = entry.lexEntries[i].orderedtripleset
            else:
                orderedtripleset = entry.lexEntries[i].orderedtripleset_de

            orderedtripleset_xml = ET.SubElement(lexEntry_xml, 'sortedtripleset')
            for j, orderedtripleset_snt in enumerate(orderedtripleset):
                orderedtripleset_snt_xml = ET.SubElement(orderedtripleset_xml, 'sentence')
                orderedtripleset_snt_xml.attrib = { 'ID': str(j+1) }

                for triple in orderedtripleset_snt:
                    striple = ET.SubElement(orderedtripleset_snt_xml, 'striple')
                    striple.text = triple.subject + ' | ' + triple.predicate + ' | ' + triple.object

            if lng == 'en':
                references_xml = ET.SubElement(lexEntry_xml, 'references')
                references = entry.lexEntries[i].references
                for reference in references:
                    reference_xml = ET.SubElement(references_xml, 'reference')
                    reference_xml.attrib['tag'] = reference.tag
                    reference_xml.attrib['entity'] = reference.entity
                    reference_xml.attrib['number'] = str(reference.number)
                    reference_xml.attrib['type'] = str(reference.reftype)
                    reference_xml.text = reference.refex

            if lng == 'en':
                text = entry.lexEntries[i].text
                template = entry.lexEntries[i].template
                lex_template = entry.lexEntries[i].lex_template
                tree_ = entry.lexEntries[i].tree
            else:
                text = entry.lexEntries[i].text_de
                template = entry.lexEntries[i].template_de
                tree_ = entry.lexEntries[i].tree_de
                lex_template = ''

            text_xml = ET.SubElement(lexEntry_xml, 'text')
            text_xml.text = text

            template_xml = ET.SubElement(lexEntry_xml, 'template')
            template_xml.text = ' '.join(template.split())

            if lex_template.strip() != '':
                lex_xml = ET.SubElement(lexEntry_xml, 'lexicalization')
                lex_xml.text = lex_template.strip()

            if tree_.strip() != '':
                tree_xml = ET.SubElement(lexEntry_xml, 'tree')
                tree_xml.text = tree_

    rough_string = ET.tostring(tree.getroot(), encoding='utf-8', method='xml')
    rough_string = re.sub(">\n[\n \t]*<", '><', rough_string)
    xml = minidom.parseString(rough_string).toprettyxml(indent="\t")

    with open(out_file, 'wb') as f:
        f.write(xml.encode('utf-8'))

def run_generator(entryset, input_dir, output_dir, lng):
    sizedirs = filter(lambda item: not str(item).startswith('.'), os.listdir(input_dir))
    for sizedir in sizedirs:
        out_sizedir = os.path.join(output_dir, sizedir)
        if not os.path.exists(out_sizedir):
            os.mkdir(out_sizedir)

        xmlfiles = filter(lambda item: not str(item).startswith('.'), os.listdir(os.path.join(input_dir, sizedir)))
        for xmlfile in xmlfiles:
            input_file = os.path.join(input_dir, sizedir, xmlfile)
            output_file = os.path.join(output_dir, sizedir, xmlfile)
            generate(entryset, input_file, output_file, lng)
