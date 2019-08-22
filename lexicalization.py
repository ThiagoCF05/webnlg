__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 26/03/2019
Description:
    This script aims to extract the gold-standard templates for the lexicalization step.

    ARGS:
        [1] Path to the folder where WebNLG corpus is available (data/v1.4/en)
        [2] Path to the folder where the data will be saved (Folder will be created in case it does not exist)
        [3] Path to the stanford parser (which can be downloaded here: https://stanfordnlp.github.io/CoreNLP/)

    EXAMPLE:
        python3 preprocess.py ../data/v1.4/en lexicalization stanford_path
"""


import copy
import json
import parser
import os

from stanfordcorenlp import StanfordCoreNLP

STANFORD_PATH=r'/home/tcastrof/workspace/stanford/stanford-corenlp-full-2018-02-27'

class Tree:
    def __init__(self, tree, tokens, lemmas):
        self.tokens = tokens
        self.lemmas = lemmas
        self.token2lemma = dict(zip(tokens, lemmas))
        self.nodes, self.edges, self.root = self.parse(tree)


    def parse(self, tree):
        tree = tree.replace('\n', '').replace('(ROOT', '')[:-1]
        nodes, edges, root = {}, {}, 1
        node_id = 1
        prev_id = 0
        terminalidx = 0

        for child in tree.split():
            closing = list(filter(lambda x: x == ')', child))
            if child[0] == '(':
                nodes[node_id] = {
                    'id': node_id,
                    'name': child[1:],
                    'parent': prev_id,
                    'type': 'nonterminal',
                }
                edges[node_id] = []

                if prev_id > 0:
                    edges[prev_id].append(node_id)
                prev_id = copy.copy(node_id)
            else:
                terminal = child.replace(')', '')
                nodes[prev_id]['type'] = 'preterminal'

                try:
                    lemma = self.token2lemma[terminal]
                except:
                    lemma = ''

                nodes[node_id] = {
                    'id': node_id,
                    'name': terminal,
                    'parent': prev_id,
                    'type': 'terminal',
                    'idx': terminalidx,
                    'lemma': lemma
                }

                terminalidx += 1
                edges[node_id] = []
                edges[prev_id].append(node_id)

            node_id += 1
            for i in range(len(closing)):
                prev_id = nodes[prev_id]['parent']

        return nodes, edges, root


    def verb_parent(self, terminalidx):
        def search(root):
            parent = self.nodes[root]['parent']
            if self.nodes[parent]['name'] == 'VP':
                return search(parent)
            return root

        terminal_node = -1
        for node in self.nodes:
            type = self.nodes[node]['type']
            if type == 'terminal':
                if terminalidx == self.nodes[node]['idx']:
                    terminal_node = node
                    break
        return search(self.nodes[terminal_node]['parent'])


    # TO DO: treat modals would, should, might to, must, etc.
    def verb_info(self, tokens, lemmas, pos):
        voice, aspect, tense, person, number = 'active', 'simple', 'present', 'null', 'null'
        # person
        if pos[0] == 'VBZ':
            person = '3rd'
        elif pos[0] == 'VBP':
            person = 'non-3rd'

        # number
        if lemmas[0] == 'be':
            if tokens[0] in ['am', 'is', 'was']:
                number = 'singular'
            elif tokens[0] in ['are', 'were']:
                number = 'plural'

        if len(pos) == 1:
            if pos[0] == 'VB':
                aspect = 'simple'
                tense = 'infinitive'
            elif pos[0] in ['VBP', 'VBZ']:
                aspect = 'simple'
                tense = 'present'
            elif pos[0] in ['VBD', 'VBN']:
                aspect = 'simple'
                tense = 'past'
            elif pos[0] == 'VBG':
                aspect = 'progressive'
                tense = 'present'
        elif len(pos) == 2:
            if pos[0] in ['VB', 'VBP', 'VBZ']:
                if lemmas[0] == 'be' and pos[1] == 'VBG':
                    aspect = 'progressive'
                    tense = 'present'
                elif lemmas[0] == 'have' and pos[1] == 'VBN':
                    aspect = 'perfect'
                    tense = 'present'
                elif lemmas[0] == 'be' and pos[1] == 'VBN':
                    aspect = 'simple'
                    tense = 'present'
                    voice = 'passive'
            elif pos[0] == 'VBD':
                if lemmas[0] == 'be' and pos[1] == 'VBG':
                    aspect = 'progressive'
                    tense = 'past'
                elif lemmas[0] == 'have' and pos[1] == 'VBN':
                    aspect = 'perfect'
                    tense = 'past'
                elif lemmas[0] == 'be' and pos[1] == 'VBN':
                    aspect = 'simple'
                    tense = 'past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                aspect = 'simple'
                tense = 'future'
        elif len(pos) == 3:
            if pos[0] in ['VB', 'VBP', 'VBZ']:
                if lemmas[0] == 'have' and pos[1] == 'VBN' and lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        aspect = 'perfect-progressive'
                        tense = 'present'
                    elif pos[2] == 'VBN':
                        aspect = 'perfect'
                        tense = 'present'
                        voice = 'passive'
                elif lemmas[0] == 'be' and pos[1] == 'VBN' and lemmas[1] == 'be' and pos[2] == 'VBN':
                    aspect = 'progressive'
                    tense = 'present'
                    voice = 'passive'
            elif pos[0] == 'VBD':
                if lemmas[0] == 'have' and pos[1] == 'VBN' and lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        aspect = 'perfect-progressive'
                        tense = 'past'
                    elif pos[2] == 'VBN':
                        tense = 'past perfect'
                        voice = 'passive'
                elif lemmas[0] == 'be' and pos[1] == 'VBN' and lemmas[1] == 'be' and pos[2] == 'VBN':
                    aspect = 'progressive'
                    tense = 'past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                if lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        aspect = 'progressive'
                        tense = 'future'
                    elif pos[2] == 'VBN':
                        aspect = 'simple'
                        tense = 'future'
                        voice = 'passive'
                elif lemmas[1] == 'have' and pos[2] == 'VBN':
                    aspect = 'perfect'
                    tense = 'future'
        elif len(pos) == 4:
            if pos[1] == 'VBN' and lemmas[1] == 'be' \
                    and pos[2] == 'VBG' and lemmas[2] == 'be' and pos[3] == 'VBN':
                if pos[0] in ['VB', 'VBP', 'VBZ'] and lemmas[0] == 'have':
                    aspect = 'perfect-progressive'
                    tense = 'present'
                    voice = 'passive'
                elif pos[0] == 'VBD' and lemmas[0] == 'have':
                    aspect = 'perfect-progressive'
                    tense = 'past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                if lemmas[1] == 'have' and pos[2] == 'VBN' and lemmas[2] == 'be':
                    if pos[3] == 'VBG':
                        aspect = 'perfect-progressive'
                        tense = 'future'
                    elif pos[3] == 'VBN':
                        aspect = 'perfect'
                        tense = 'future'
                        voice = 'passive'
                elif lemmas[1] == 'be' and pos[2] == 'VBG' and lemmas[2] == 'be' and lemmas[3] == 'VBN':
                    aspect = 'progressive'
                    tense = 'future'
                    voice = 'passive'
        elif len(pos) == 5:
            if lemmas[0] == 'will' and lemmas[1] == 'have' \
                    and pos[2] == 'VBN' and lemmas[2] == 'be' \
                    and pos[3] == 'VBG' and lemmas[3] and pos[4] == 'VBN':
                aspect = 'perfect-progressive'
                tense = 'future'
                voice = 'passive'

        return tense, aspect, voice, person, number


    def classify_verbs(self):
        def get_info(root, tokens, lemmas, pos, head, vps):
            type_ = self.nodes[root]['type']
            if type_ == 'preterminal':
                pos.append(self.nodes[root]['name'])
                for edge in self.edges[root]:
                    lemmas, tokens, pos, head, vps = get_info(edge, tokens, lemmas, pos, head, vps)
            elif type_ == 'terminal':
                head = root
                tokens.append(self.nodes[root]['name'])
                lemmas.append(self.nodes[root]['lemma'])
            else:
                tag = self.nodes[root]['name']
                if tag == 'VP':
                    vps.append(root)
                    for edge in self.edges[root]:
                        lemmas, tokens, pos, head, vps = get_info(edge, tokens, lemmas, pos, head, vps)

            return lemmas, tokens, pos, head, vps

        def delete(root, end, children=[]):
            if root == end:
                children = copy.copy(self.edges[root])
            else:
                edges = self.edges[root]
                for edge in edges:
                    children = delete(edge, end, children)
                    del self.nodes[edge]
                    del self.edges[edge]

            return children

        continue_ = True
        dictionary = []
        while continue_:
            i = 0
            for i, node in enumerate(self.nodes):
                parent = self.nodes[node]['parent']
                if parent > 0:
                    parent_tag = self.nodes[parent]['name']
                else:
                    parent_tag = 'X'
                tag = self.nodes[node]['name']

                # verb phrase with at least a verb structure child
                regular_vp = False
                for edge in self.edges[node]:
                    if len(self.nodes[edge]['name'].strip()) > 0:
                        if self.nodes[edge]['name'][0] == 'V':
                            regular_vp = True
                            break

                if tag == 'VP' and parent_tag != 'VP' and regular_vp:
                    lemmas, tokens, pos, head, vps = get_info(node, [], [], [], 0, [])
                    tense, aspect, voice, person, number = self.verb_info(tokens, lemmas, pos)

                    head_parent = self.nodes[head]['parent']
                    self.nodes[node]['name'] = 'VP[aspect={0},tense={1},voice={2},person={3},number={4}]'.format(aspect, tense, voice, person, number)
                    self.nodes[head_parent]['name'] = 'VB'
                    self.nodes[head]['name'] = self.nodes[head]['lemma']

                    key = self.nodes[node]['name'] + ' ' + self.nodes[head]['name']
                    value = ' '.join(tokens).lower()
                    dictionary.append((key, value))

                    if node != vps[-1]:
                        self.edges[node] = delete(node, vps[-1])
                        for edge in self.edges[node]:
                            self.nodes[edge]['parent'] = node
                    break

            continue_ = False if i == len(self.nodes)-1 else True
        return dictionary


    def classify_determiners(self):
        dictionary = []
        continue_ = True
        while continue_:
            i = 0
            for i, node in enumerate(self.nodes):
                tag = self.nodes[node]['name']

                if tag == 'DT':
                    terminal = self.edges[node][0]
                    token, lemma = self.nodes[terminal]['name'], self.nodes[terminal]['lemma']

                    form = 'defined'
                    if token.lower() in ['a', 'an']:
                        form = 'undefined'
                    elif token.lower() == 'the':
                        form = 'defined'
                    elif token.lower() in ['this', 'that', 'these', 'those']:
                        form = 'demonstrative'

                    self.nodes[node]['name'] = 'DT[form={0}]'.format(form)
                    self.nodes[terminal]['name'] = self.nodes[terminal]['lemma']
                    dictionary.append((self.nodes[node]['name'], token.lower()))
                    break

            continue_ = False if i == len(self.nodes)-1 else True
        return dictionary


    def annotate(self):
        dictionary = []
        d = self.classify_verbs()
        dictionary.extend(d)
        d = self.classify_determiners()
        dictionary.extend(d)

        template = self.flat(self.root, [])

        return template, dictionary


    def flat(self, root, text):
        type_ = self.nodes[root]['type']
        name = self.nodes[root]['name']

        if type_ == 'terminal':
            text.append(name)
        else:
            if name[:2] in ['VP', 'DT']:
                text.append(name)

            for edge in self.edges[root]:
                text = self.flat(edge, text)
        return text


class TemplateExtraction:
    def __init__(self):
        self.corenlp = StanfordCoreNLP(STANFORD_PATH)


    def close(self):
        self.corenlp.close()


    def classify_verb(self, tokens, lemmas, pos):
        voice, aspect, tense, person, number = 'active', 'simple', 'present', 'null', 'null'
        # person
        if pos[0] == 'VBZ':
            person = '3rd'
        elif pos[0] == 'VBP':
            person = 'non-3rd'

        # number
        if lemmas[0] == 'be':
            if tokens[0] in ['am', 'is', 'was']:
                number = 'singular'
            elif tokens[0] in ['are', 'were']:
                number = 'plural'

        if len(pos) == 1:
            if pos[0] == 'VB':
                aspect = 'simple'
                tense = 'infinitive'
            elif pos[0] in ['VBP', 'VBZ']:
                aspect = 'simple'
                tense = 'present'
            elif pos[0] in ['VBD', 'VBN']:
                aspect = 'simple'
                tense = 'past'
            elif pos[0] == 'VBG':
                aspect = 'progressive'
                tense = 'present'
        elif len(pos) == 2:
            if pos[0] in ['VB', 'VBP', 'VBZ']:
                if lemmas[0] == 'be' and pos[1] == 'VBG':
                    aspect = 'progressive'
                    tense = 'present'
                elif lemmas[0] == 'have' and pos[1] == 'VBN':
                    aspect = 'perfect'
                    tense = 'present'
                elif lemmas[0] == 'be' and pos[1] == 'VBN':
                    aspect = 'simple'
                    tense = 'present'
                    voice = 'passive'
            elif pos[0] == 'VBD':
                if lemmas[0] == 'be' and pos[1] == 'VBG':
                    aspect = 'progressive'
                    tense = 'past'
                elif lemmas[0] == 'have' and pos[1] == 'VBN':
                    aspect = 'perfect'
                    tense = 'past'
                elif lemmas[0] == 'be' and pos[1] == 'VBN':
                    aspect = 'simple'
                    tense = 'past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                aspect = 'simple'
                tense = 'future'
        elif len(pos) == 3:
            if pos[0] in ['VB', 'VBP', 'VBZ']:
                if lemmas[0] == 'have' and pos[1] == 'VBN' and lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        aspect = 'perfect-progressive'
                        tense = 'present'
                    elif pos[2] == 'VBN':
                        aspect = 'perfect'
                        tense = 'present'
                        voice = 'passive'
                elif lemmas[0] == 'be' and pos[1] == 'VBN' and lemmas[1] == 'be' and pos[2] == 'VBN':
                    aspect = 'progressive'
                    tense = 'present'
                    voice = 'passive'
            elif pos[0] == 'VBD':
                if lemmas[0] == 'have' and pos[1] == 'VBN' and lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        aspect = 'perfect-progressive'
                        tense = 'past'
                    elif pos[2] == 'VBN':
                        tense = 'past perfect'
                        voice = 'passive'
                elif lemmas[0] == 'be' and pos[1] == 'VBN' and lemmas[1] == 'be' and pos[2] == 'VBN':
                    aspect = 'progressive'
                    tense = 'past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                if lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        aspect = 'progressive'
                        tense = 'future'
                    elif pos[2] == 'VBN':
                        aspect = 'simple'
                        tense = 'future'
                        voice = 'passive'
                elif lemmas[1] == 'have' and pos[2] == 'VBN':
                    aspect = 'perfect'
                    tense = 'future'
        elif len(pos) == 4:
            if pos[1] == 'VBN' and lemmas[1] == 'be' \
                    and pos[2] == 'VBG' and lemmas[2] == 'be' and pos[3] == 'VBN':
                if pos[0] in ['VB', 'VBP', 'VBZ'] and lemmas[0] == 'have':
                    aspect = 'perfect-progressive'
                    tense = 'present'
                    voice = 'passive'
                elif pos[0] == 'VBD' and lemmas[0] == 'have':
                    aspect = 'perfect-progressive'
                    tense = 'past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                if lemmas[1] == 'have' and pos[2] == 'VBN' and lemmas[2] == 'be':
                    if pos[3] == 'VBG':
                        aspect = 'perfect-progressive'
                        tense = 'future'
                    elif pos[3] == 'VBN':
                        aspect = 'perfect'
                        tense = 'future'
                        voice = 'passive'
                elif lemmas[1] == 'be' and pos[2] == 'VBG' and lemmas[2] == 'be' and lemmas[3] == 'VBN':
                    aspect = 'progressive'
                    tense = 'future'
                    voice = 'passive'
        elif len(pos) == 5:
            if lemmas[0] == 'will' and lemmas[1] == 'have' \
                    and pos[2] == 'VBN' and lemmas[2] == 'be' \
                    and pos[3] == 'VBG' and lemmas[3] and pos[4] == 'VBN':
                aspect = 'perfect-progressive'
                tense = 'future'
                voice = 'passive'

        w = 'VP[aspect={0},tense={1},voice={2},person={3},number={4}] {5}'.format(aspect, tense, voice, person, number, lemmas[-1])
        return w


    def classify_determiner(self, token, lemma):
        form = 'defined'
        if token.lower() in ['a', 'an']:
            form = 'undefined'
        elif token.lower() == 'the':
            form = 'defined'
        elif token.lower() in ['this', 'that', 'these', 'those']:
            form = 'demonstrative'

        return 'DT[form={0}] {1}'.format(form, lemma)


    def tokenize(self, text):
        props = {'annotators': 'tokenize,ssplit','pipelineLanguage':'en','outputFormat':'json'}
        sentences = []
        # tokenizing text
        try:
            out = self.corenlp.annotate(text.strip(), properties=props)
            out = json.loads(out)

            for snt in out['sentences']:
                sentence = ' '.join(map(lambda w: w['originalText'], snt['tokens']))
                sentences.append(sentence)
        except:
            print('Parsing error...')

        return sentences


    def extract(self, template):
        text = template.replace('@', '')
        dictionary = []

        props = {'annotators': 'tokenize,ssplit,pos,lemma,parse','pipelineLanguage':'en','outputFormat':'json'}

        delex = []
        sentences = self.tokenize(text)
        for sentence in sentences:
            out = self.corenlp.annotate(sentence, properties=props)
            out = json.loads(out)

            snt = out['sentences'][0]

            tree = Tree(tree=snt['parse'], tokens=[], lemmas=[])
            pos = [token['pos'] for token in snt['tokens']]
            verb = []
            for i, p in enumerate(pos):
                if 'VB' in p:
                    if len(verb) > 0:
                        if tree.verb_parent(i) == tree.verb_parent(verb[-1]):
                            verb.append(i)
                        else:
                            tokens = [snt['tokens'][j]['originalText'] for j in verb]
                            lemmas = [snt['tokens'][j]['lemma'] for j in verb]
                            pos = [snt['tokens'][j]['pos'] for j in verb]
                            key = self.classify_verb(tokens=tokens, pos=pos, lemmas=lemmas)
                            delex.append(key)

                            value = ' '.join(tokens).lower()
                            dictionary.append((key, value))
                            verb = []
                    else:
                        verb.append(i)
                else:
                    if len(verb) > 0:
                        tokens = [snt['tokens'][j]['originalText'] for j in verb]
                        lemmas = [snt['tokens'][j]['lemma'] for j in verb]
                        pos = [snt['tokens'][j]['pos'] for j in verb]
                        key = self.classify_verb(tokens=tokens, pos=pos, lemmas=lemmas)
                        delex.append(key)

                        value = ' '.join(tokens).lower()
                        dictionary.append((key, value))
                        verb = []
                    if p == 'DT':
                        token = snt['tokens'][i]['originalText']
                        lemma = snt['tokens'][i]['lemma']
                        delex.append(self.classify_determiner(token, lemma))
                    else:
                        token = snt['tokens'][i]['originalText']
                        delex.append(token)

                        # snt = out['sentences'][0]
                        # strtree = snt['parse']
                        # tokens = [w['originalText'] for w in snt['tokens']]
                        # lemmas = [w['lemma'] for w in snt['tokens']]
                        #
                        # tree = Tree(tree=strtree, tokens=tokens, lemmas=lemmas)
                        # temp, d = tree.annotate()
                        # dictionary.extend(d)
                        # delex.extend(temp)

        return delex, dictionary


    def __call__(self, entryset, lng='en'):
        num, errors = 0, 0
        for entry in entryset:
            for lex in entry.lexEntries:
                num += 1
                print('Entry ID:', entry.eid, 'Lex ID: ', lex.lid, 'Errors: ', round(float(errors) / num, 2))
                try:
                    if lng == 'en':
                        lex.lex_template, d = self.extract(template=lex.template)
                        lex.lex_template = ' '.join(lex.lex_template)
                except:
                    errors += 1

        return entryset


    def close(self):
        self.corenlp.close()


if __name__ == '__main__':
    template = TemplateExtraction()

    FINAL_PATH = 'data/v1.5'
    if not os.path.exists(FINAL_PATH):
        os.mkdir(FINAL_PATH)

    EN_PATH = 'data/v1.5/en'
    if not os.path.exists(EN_PATH):
        os.mkdir(EN_PATH)

    # TRAINSET
    print('Preparing trainset...')
    TRAIN_PATH = 'data/v1.4/en/train'
    _set = 'train'

    EN_TRAIN_PATH = 'data/v1.5/en/train'
    if not os.path.exists(EN_TRAIN_PATH):
        os.mkdir(EN_TRAIN_PATH)

    entryset = parser.run_parser(TRAIN_PATH)
    # tree extraction
    entryset = template(entryset, 'en')
    # generate
    parser.run_generator(entryset=entryset, input_dir=TRAIN_PATH, output_dir=EN_TRAIN_PATH, lng='en')

    # DEVSET
    print('Preparing devset...')
    DEV_PATH = 'data/v1.4/en/dev'
    _set = 'train'

    EN_DEV_PATH = 'data/v1.5/en/dev'
    if not os.path.exists(EN_DEV_PATH):
        os.mkdir(EN_DEV_PATH)

    entryset = parser.run_parser(DEV_PATH)
    # tree extraction
    entryset = template(entryset, 'en')
    # generate
    parser.run_generator(entryset=entryset, input_dir=DEV_PATH, output_dir=EN_DEV_PATH, lng='en')

    # TESTSET
    print('Preparing test...')
    TEST_PATH = 'data/v1.4/en/test'
    _set = 'train'

    EN_TEST_PATH = 'data/v1.5/en/test'
    if not os.path.exists(EN_TEST_PATH):
        os.mkdir(EN_TEST_PATH)

    entryset = parser.run_parser(TEST_PATH)
    # tree extraction
    entryset = template(entryset, 'en')
    # generate
    parser.run_generator(entryset=entryset, input_dir=TEST_PATH, output_dir=EN_TEST_PATH, lng='en')

    template.close()