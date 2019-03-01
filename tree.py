__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 03/11/2018
Description:
    Extract templates based on sentence segmentation and the ordering script

    PYTHON VERSION: 3
"""

import copy
import json
import os
import parser
import reg

from stanfordcorenlp import StanfordCoreNLP

STANFORD_PATH=r'/home/tcastrof/workspace/stanford/stanford-corenlp-full-2018-02-27'

class Tree:
    def __init__(self, tree, tokens, lemmas, references=[], dependencies=[]):
        self.tokens = tokens
        self.lemmas = lemmas
        self.token2lemma = dict(zip(tokens, lemmas))
        self.nodes, self.edges, self.root = self.parse(tree)
        self.references = references
        self.dependencies = dependencies


    def parse(self, tree):
        tree = tree.replace('\n', '').replace('(ROOT', '')[:-1]
        nodes, edges, root = {}, {}, 1
        node_id = 1
        prev_id = 0
        terminalidx = 1

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


    def substring(self, root, string):
        type_ = self.nodes[root]['type']
        if type_ == 'terminal':
            string.append(self.nodes[root]['name'])
        else:
            for edge in self.edges[root]:
                self.substring(edge, string)

        return string


    def substrings(self):
        sub = []
        for node in self.nodes:
            type_ = self.nodes[node]['type']
            if type_ != 'terminal':
                sub.append((node, ' '.join(self.substring(node, []))))

        return sub


    def span(self):
        terminals = []
        for node in self.nodes:
            type_ = self.nodes[node]['type']
            if type_ == 'terminal':
                terminals.append(node)

        terminals = sorted(terminals)
        spans = []
        for i in range(len(terminals)):
            for j, terminal in enumerate(terminals):
                idxs = terminals[j:j+i+1]

                string, subtree = [], []
                for node in idxs:
                    string.append(self.nodes[node]['name'])
                    parent = self.nodes[node]['parent']
                    subtree.append('({0} {1})'.format(self.nodes[parent]['name'], self.nodes[node]['name']))

                string = ' '.join(string)
                subtree = ' '.join(subtree)
                spans.append((string, subtree))
        return spans


    def classify_syntax(self):
        def terminalidx_found(root, terminalidx, result=False):
            type_ = self.nodes[root]['type']

            if not result:
                if type_ == 'terminal':
                    if self.nodes[root]['idx'] == terminalidx:
                        result = True
                else:
                    for edge in self.edges[root]:
                        result = terminalidx_found(edge, terminalidx, result)
                        if result:
                            break
            return result

        governor, subj, obj, subjpass = -1, -1, -1, -1
        for edge in self.dependencies:
            if 'subjpass' in edge['dep']:
                subjpass = edge['dependent']
                governor = edge['governor']
            elif 'subj' in edge['dep']:
                subj = edge['dependent']
                governor = edge['governor']
            elif 'obj' in edge['dep']:
                obj = edge['dependent']
                governor = edge['governor']

        # take care of special case of passive voice
        if subjpass > -1:
            obj = subjpass
            for edge in self.dependencies:
                if 'nmod' in edge['dep'] and edge['governor'] == governor:
                    subj = edge['dependent']

        if subj > -1:
            for node in self.nodes:
                if self.nodes[node]['parent'] > 0:
                    parent_tag = self.nodes[self.nodes[node]['parent']]['name']
                else:
                    parent_tag = 'X'
                tag = self.nodes[node]['name']

                found = terminalidx_found(node, subj)
                if tag == 'NP' and parent_tag != 'NP' and found:
                    self.nodes[node]['name'] = 'NP-SUBJ'
                    break

        if obj > -1:
            for node in self.nodes:
                if self.nodes[node]['parent'] > 0:
                    parent_tag = self.nodes[self.nodes[node]['parent']]['name']
                else:
                    parent_tag = 'X'
                tag = self.nodes[node]['name']

                found = terminalidx_found(node, obj)
                if tag == 'NP' and parent_tag != 'NP' and found:
                    self.nodes[node]['name'] = 'NP-OBJ'
                    break


    def delexicalize(self, str_tree):
        # delexicalize subtrees
        substrings = self.substrings()
        for reference in self.references:
            refex = ' '.join(reference.refex.split())

            for substring in substrings:
                root, text = substring

                if refex == text.strip():
                    subtree = self.__print__(root).strip()
                    str_tree = str_tree.replace(subtree, '({0} (TAG {1}))'.format(self.nodes[root]['name'], reference.tag))
                    break

        # delexicalize spans
        spans = self.span()
        for reference in self.references:
            refex = ' '.join(reference.refex.split())

            for span in spans:
                if refex == span[0].strip():
                    str_tree.replace(span[1].strip(), '{0} '.format(reference.tag))
                    break

        return str_tree


    # TO DO: treat modals would, should, might to, must, etc.
    def verb_info(self, lemmas, pos):
        voice, aspect, tense = 'active', 'simple', 'present'
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

        return tense, aspect, voice


    def classify_verbs(self):
        def get_info(root, lemmas, pos, head, vps):
            type_ = self.nodes[root]['type']
            if type_ == 'preterminal':
                pos.append(self.nodes[root]['name'])
                for edge in self.edges[root]:
                    lemmas, pos, head, vps = get_info(edge, lemmas, pos, head, vps)
            elif type_ == 'terminal':
                head = root
                lemmas.append(self.nodes[root]['lemma'])
            else:
                tag = self.nodes[root]['name']
                if tag == 'VP':
                    vps.append(root)
                    for edge in self.edges[root]:
                        lemmas, pos, head, vps = get_info(edge, lemmas, pos, head, vps)

            return lemmas, pos, head, vps

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
        while continue_:
            i = 0
            for i, node in enumerate(self.nodes):
                parent = self.nodes[node]['parent']
                if parent > 0:
                    parent_tag = self.nodes[parent]['name']
                else:
                    parent_tag = 'X'
                tag = self.nodes[node]['name']

                if tag == 'VP' and parent_tag != 'VP':
                    lemmas, pos, head, vps = get_info(node, [], [], 0, [])
                    tense, aspect, voice = self.verb_info(lemmas, pos)

                    head_parent = self.nodes[head]['parent']
                    self.nodes[node]['name'] = 'VP[aspect={0}, tense={1}, voice={2}]'.format(aspect, tense, voice)
                    self.nodes[head_parent]['name'] = 'VB'
                    self.nodes[head]['name'] = self.nodes[head]['lemma']

                    if node != vps[-1]:
                        self.edges[node] = delete(node, vps[-1])
                        for edge in self.edges[node]:
                            self.nodes[edge]['parent'] = node
                    break

            continue_ = False if i == len(self.nodes)-1 else True


    def __call__(self, root, nodes, edges, references, dependencies):
        self.root = root
        self.nodes = nodes
        self.edges = edges
        self.references = references
        self.dependencies = dependencies

        # point coordinations
        for node in self.nodes:
            for edge in self.edges[node]:
                if self.nodes[edge]['name'] == 'CC':
                    self.nodes[node]['name'] += '-COORDINATION'
                    break

        self.classify_syntax()
        self.classify_verbs()

        str_tree = self.__print__(self.root)
        str_tree = self.delexicalize(str_tree)

        return str_tree


    def prettify(self, str_tree):
        nodes, edges, root = self.parse(str_tree)

        return self.__print__(root, indent=True)

    def __print__(self, root, tree='', depth=0, indent=False):
        type_ = self.nodes[root]['type']
        name = self.nodes[root]['name']

        if type_ == 'terminal':
            tree += name
        else:
            tab = '\n' + (depth * '  ') if type_ == 'nonterminal' or name in ['CC', '.', ','] else ''
            if indent:
                tree += tab + '(' + name + ' '
            else:
                tree += '(' + name + ' '

            for edge in self.edges[root]:
                tree = self.__print__(edge, tree, depth+1, False)

            tree = tree.strip() + ') '
        return tree


class TreeExtraction:
    def __init__(self):
        self.corenlp = StanfordCoreNLP(STANFORD_PATH)


    def close(self):
        self.corenlp.close()


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


    def __call__(self, entryset, lng='en'):
        num, errors = 0, 0
        for entry in entryset:
            for lex in entry.lexEntries:
                num += 1
                print('Entry ID:', entry.eid, 'Lex ID: ', lex.lid, 'Errors: ', round(float(errors) / num, 2))
                try:
                    if lng == 'en':
                        _, lex.tree, _ = self.extract(text=lex.text, template=lex.template, entitymap=entry.entitymap_to_dict())
                    else:
                        _, lex.tree_de, _ = self.extract(text=lex.text_de, template=lex.template_de, entitymap=entry.entitymap_to_dict())
                except:
                    errors += 1

        return entryset


    def extract(self, text, template, entitymap):
        references = reg.extract_references(text, template, entitymap)

        text = text.replace('@', '')

        # sentence tokenization
        text = self.tokenize(text)

        props = {'annotators': 'tokenize,ssplit,pos,lemma,parse','pipelineLanguage':'en','outputFormat':'json'}

        deps, trees, delex = [], '(SENTENCES ', '(SENTENCES '
        for i, snt in enumerate(text):
            out = self.corenlp.annotate(snt, properties=props)
            out = json.loads(out)

            snt = out['sentences'][0]
            strtree = snt['parse']
            dep = snt['enhancedPlusPlusDependencies']
            tokens = [w['originalText'] for w in snt['tokens']]
            lemmas = [w['lemma'] for w in snt['tokens']]

            trees += strtree + ' '
            deps.append(dep)

            tree = Tree(tree=strtree, tokens=tokens, lemmas=lemmas)

            template = tree(tree.root, tree.nodes, tree.edges, references, dep)
            delex += template + ' '

        trees = trees.strip() + ')'
        delex = delex.strip() + ')'

        return trees, delex, deps


if __name__ == '__main__':
    template = TreeExtraction()

    FINAL_PATH = 'versions/v2.0'
    if not os.path.exists(FINAL_PATH):
        os.mkdir(FINAL_PATH)

    EN_PATH = 'versions/v2.0/en'
    if not os.path.exists(EN_PATH):
        os.mkdir(EN_PATH)

    # TRAINSET
    print('Preparing trainset...')
    TRAIN_PATH = 'versions/v1.4/en/train'
    _set = 'train'

    EN_TRAIN_PATH = 'versions/v2.0/en/train'
    if not os.path.exists(EN_TRAIN_PATH):
        os.mkdir(EN_TRAIN_PATH)

    entryset = parser.run_parser(TRAIN_PATH)
    # tree extraction
    entryset = template(entryset, 'en')
    # generate
    parser.run_generator(entryset=entryset, input_dir=TRAIN_PATH, output_dir=EN_TRAIN_PATH, lng='en')

    # DEVSET
    print('Preparing devset...')
    DEV_PATH = 'versions/v1.4/en/dev'
    _set = 'train'

    EN_DEV_PATH = 'versions/v2.0/en/dev'
    if not os.path.exists(EN_DEV_PATH):
        os.mkdir(EN_DEV_PATH)

    entryset = parser.run_parser(DEV_PATH)
    # tree extraction
    entryset = template(entryset, 'en')
    # generate
    parser.run_generator(entryset=entryset, input_dir=DEV_PATH, output_dir=EN_DEV_PATH, lng='en')

    # TESTSET
    print('Preparing test...')
    TEST_PATH = 'versions/v1.4/en/test'
    _set = 'train'

    EN_TEST_PATH = 'versions/v2.0/en/test'
    if not os.path.exists(EN_TEST_PATH):
        os.mkdir(EN_TEST_PATH)

    entryset = parser.run_parser(TEST_PATH)
    # tree extraction
    entryset = template(entryset, 'en')
    # generate
    parser.run_generator(entryset=entryset, input_dir=TEST_PATH, output_dir=EN_TEST_PATH, lng='en')

    template.close()