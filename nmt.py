__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 28/06/2018
Description:
    Prepare lexical entries to be translated to German (preprocess method) and treat the translations later
    (postprocess method)

    PYTHON VERSION: 2.7
"""

import os
from nltk.tokenize import sent_tokenize
import re

class NMT():
    def __init__(self, entryset, _set):
        self.entryset = entryset
        self._set = _set

        self.tmp = 'tmp/'
        if not os.path.exists(self.tmp):
            os.mkdir(self.tmp)

    def preprocess(self):
        self.prepare_filenames()
        print('Preparing input for translation...')
        self.prepare_input()

    def postprocess(self):
        self.prepare_filenames()
        print('Preparing output to be converted in XML...')
        self.prepare_output()
        # self.delete_tempfiles()
        return self.entryset

    def prepare_filenames(self):
        self.en_template_fname = os.path.join(self.tmp, '.'.join(['temp', self._set, 'en']))
        self.de_template_fname = os.path.join(self.tmp, '.'.join(['temp', self._set, 'de']))
        self.templateinfo_fname = os.path.join(self.tmp, ''.join(['template', self._set, 'info']))

        self.en_text_fname = os.path.join(self.tmp, '.'.join(['text', self._set, 'en']))
        self.de_text_fname = os.path.join(self.tmp, '.'.join(['text', self._set, 'de']))
        self.pt_text_fname = os.path.join(self.tmp, '.'.join(['text', self._set, 'pt']))
        self.textinfo_fname = os.path.join(self.tmp, ''.join(['text', self._set, 'info']))

    def prepare_input(self):
        ftext = open(self.en_text_fname, 'w')
        ftextinfo = open(self.textinfo_fname, 'w')
        ftemplate = open(self.en_template_fname, 'w')
        ftemplateinfo = open(self.templateinfo_fname, 'w')

        for entry in self.entryset:
            for lex in entry.lexEntries:
                for sent_id, sent in enumerate(sent_tokenize(lex.text)):
                    ftextinfo.write(','.join([entry.eid, entry.category, entry.size, lex.lid, self._set, str(sent_id+1), '\n']))
                    ftext.write(sent.strip().encode('utf-8'))
                    ftext.write('\n'.encode('utf-8'))

                for sent_id, sent in enumerate(sent_tokenize(lex.template)):
                    ftemplateinfo.write(','.join([entry.eid, entry.category, entry.size, lex.lid, self._set, str(sent_id+1), '\n']))
                    ftemplate.write(sent.strip().encode('utf-8'))
                    ftemplate.write('\n'.encode('utf-8'))

        ftext.close()
        ftemplate.close()
        ftextinfo.close()
        ftemplateinfo.close()

    def prepare_output(self):
        ftextinfo = open(self.textinfo_fname)
        ftext_de = open(self.de_text_fname)
        ftext_pt = open(self.pt_text_fname)

        textinfo = ftextinfo.read().decode('utf-8').split('\n')
        text_de = ftext_de.read().decode('utf-8').split('\n')
        text_pt = ftext_pt.read().decode('utf-8').split('\n')
        for i, entryinfo in enumerate(textinfo[:-1]):
            entryinfo = entryinfo.split(',')
            eid = entryinfo[0]
            category = entryinfo[1]
            size = entryinfo[2]
            lid = entryinfo[3]

            for j, entry in enumerate(self.entryset):
                if entry.eid==eid and entry.size==str(size) and entry.category==category:
                    for z, lexEntry in enumerate(entry.lexEntries):
                        if lexEntry.lid==lid:
                            self.entryset[j].lexEntries[z].text_de = self.entryset[j].lexEntries[z].text_de + text_de[i] + ' '
                            self.entryset[j].lexEntries[z].text_pt = self.entryset[j].lexEntries[z].text_pt + text_pt[i] + ' '

        ftemplateinfo = open(self.templateinfo_fname)
        ftemplate = open(self.de_template_fname)

        templateinfo = ftemplateinfo.read().decode('utf-8').split('\n')
        template = ftemplate.read().decode('utf-8').split('\n')

        for i, entryinfo in enumerate(templateinfo[:-1]):
            entryinfo = entryinfo.split(',')
            eid = entryinfo[0]
            category = entryinfo[1]
            size = entryinfo[2]
            lid = entryinfo[3]

            # formatted template to fix truecasing
            formated_template = re.sub('[Aa]gent-', 'AGENT-', template[i])
            formated_template = re.sub('[Bb]ridge-', 'BRIDGE-', formated_template)
            formated_template = re.sub('[Pp]atient-', 'PATIENT-', formated_template)
            for j, entry in enumerate(self.entryset):
                if entry.eid==eid and entry.size==str(size) and entry.category==category:
                    for z, lexEntry in enumerate(entry.lexEntries):
                        if lexEntry.lid==lid:
                            self.entryset[j].lexEntries[z].template_de = self.entryset[j].lexEntries[z].template_de + formated_template + ' '


        ftextinfo.close()
        ftext_de.close()
        ftext_pt.close()
        ftemplateinfo.close()
        ftemplate.close()

    def delete_tempfiles(self):
        os.remove(self.textinfo_fname)
        os.remove(self.templateinfo_fname)
        os.remove(self.en_template_fname)
        os.remove(self.en_text_fname)
        os.remove(self.pt_text_fname)
        os.remove(self.de_template_fname)
        os.remove(self.de_text_fname)