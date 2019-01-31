__author__='thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 03/11/2018
Description:
    Extract templates based on sentence segmentation and the ordering script

    PYTHON VERSION: 2.7
"""

import _pickle as p
import collections
import copy
import json
import order
import reg

from stanfordcorenlp import StanfordCoreNLP

STANFORD_PATH=r'/home/tcastrof/workspace/stanford/stanford-corenlp-full-2018-02-27'

class Tree:
    def __init__(self, tree, tokens, lemmas, references=[], dependencies=[]):
        self.token2lemma = dict(zip(tokens, lemmas))
        self.nodes, self.edges, self.root = self.parse(tree)
        self.references= references
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

                nodes[node_id] = {
                    'id': node_id,
                    'name': terminal,
                    'parent': prev_id,
                    'type': 'terminal',
                    'idx': terminalidx,
                    'lemma': self.token2lemma[terminal],
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


    def delexicalize_references(self):
        substrings = self.substrings()

        for reference in self.references:
            refex = ' '.join(reference.refex.split())
            
            for i, substring in enumerate(substrings):
                root, text = substring

                if refex == text.strip():
                    for edge in self.edges[root]:
                        del self.nodes[edge]
                        del self.edges[edge]

                    node_id1 = max(list(self.nodes.keys())) + 1
                    self.nodes[node_id1] = {
                        'id': node_id1,
                        'name': 'TAG',
                        'parent': root,
                        'type': 'preterminal',
                    }
                    self.edges[node_id1] = []
                    self.edges[root] = [node_id1]

                    node_id2 = node_id1 + 1
                    self.nodes[node_id2] = {
                        'id': node_id2,
                        'name': reference.tag,
                        'parent': node_id1,
                        'type': 'terminal',
                    }
                    self.edges[node_id2] = []
                    self.edges[node_id1] = [node_id2]
                    break


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
                    for edge in self.edges[root]:
                        lemmas, pos, head, vps = get_info(edge, lemmas, pos, head, vps + [root])

            return lemmas, pos, head, vps


        def delete(root, end):
            children = []
            edges = self.edges[root]
            for edge in edges:
                if edge != end:
                    delete(edge, end)
                else:
                    children = self.edges[edge]

                del self.nodes[edge]
                del self.edges[edge]
            return children


        continue_ = True
        while continue_:
            i = 0
            for i, node in enumerate(self.nodes):
                if self.nodes[node]['parent'] > 0:
                    parent_tag = self.nodes[self.nodes[node]['parent']]['name']
                else:
                    parent_tag = 'X'
                tag = self.nodes[node]['name']

                if tag == 'VP' and parent_tag != 'VP':
                    lemmas, pos, head, vps = get_info(node, [], [], 0, [node])
                    tense, aspect, voice = self.verb_info(lemmas, pos)

                    self.nodes[node]['name'] = 'VP[aspect={0}, tense={1}, voice={2}]'.format(aspect, tense, voice)

                    self.nodes[head]['tag'] = 'VB'
                    self.nodes[head]['name'] = self.nodes[head]['lemma']
                    self.nodes[head]['parent'] = node
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

        self.classify_syntax()
        self.classify_verbs()
        self.delexicalize_references()

        return self.__print__(self.root, '')


    def __print__(self, root, tree=''):
        type_ = self.nodes[root]['type']
        name = self.nodes[root]['name']

        if type_ == 'terminal':
            tree += name
        else:
            tree += '(' + name + ' '

            for edge in self.edges[root]:
                tree = self.__print__(edge, tree)

            tree = tree.strip() + ') '
        return tree



class Template:
    def __init__(self):
        self.corenlp = StanfordCoreNLP(STANFORD_PATH)


    def close(self):
        self.corenlp.close()


    def __call__(self, entryset, lng='en'):
        templates = []
        for i, entry in enumerate(entryset):
            if i % 100 == 0:
                print('Progress: ', round((float(i) / len(entryset)) * 100, 2))
            for lex in entry.lexEntries:
                if lng == 'en':
                    t = self.extract(copy.deepcopy(entry.modifiedtripleset), lex.substring, lex.template, entry.entitymap_to_dict())
                else:
                    t = self.extract(copy.deepcopy(entry.modifiedtripleset), lex.text_de, lex.template_de, entry.entitymap_to_dict())

                templates.extend(t)

        return self.group(templates)


    def format(self, tripleset, template, tagentity):
        entitytag = dict(map(lambda x: (x[1], x[0]), tagentity.items()))

        triples = []
        entitymap = {}
        entities = 1
        for triple in tripleset:
            subject = entitytag[triple.subject]
            if triple.subject not in entitymap:
                entitymap[triple.subject] = 'ENTITY-' + str(entities)
                entities += 1
            new_subject = entitymap[triple.subject]

            object_ = entitytag[triple.object]
            if triple.object not in entitymap:
                entitymap[triple.object] = 'ENTITY-' + str(entities)
                entities += 1
            new_object = entitymap[triple.object]
            triples.append(new_subject + ' | ' + triple.predicate + ' | ' + new_object)

            template = template.replace(subject, new_subject).replace(object_, new_object)

        return triples, template


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


    def extract_tree(self, text, template, entitymap):
        references = reg.extract_references(text, template, entitymap)

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

        trees = trees.strip()
        delex = delex.strip()
        return trees, delex, deps


    def extract(self, tripleset, template, entitymap):
        '''
        extract pair of ordered tripleset and tokenized text
        :param tripleset:
        :param template:
        :param entitymap:
        :return:
        '''

        sentences = self.tokenize(template)

        templates = []
        for i in range(len(sentences)):
            idx = i+1

            for j, snt in enumerate(sentences):
                snts = sentences[j:j+idx]
                if len(snts) == idx:
                    template_ = ' '.join(snts)
                    orderedset = order.order(copy.deepcopy(tripleset), template_, entitymap)

                    orderedset_, template_ = self.format(orderedset, template_, entitymap)
                    templates.append((orderedset_, template_))

        return templates


    def group(self, templates):
        result = {}

        for template in templates:
            tripleset = template[0]
            idx = len(tripleset)
            if idx not in result:
                result[idx] = {}
            text = template[1]
            if tuple(tripleset) not in result[idx]:
                result[idx][tuple(tripleset)] = []
            result[idx][tuple(tripleset)].append(text)

        fjson = {'sizes': {}}
        for idx in result:
            fjson['sizes'][idx] = {'entries':[]}
            for tripleset in result[idx]:
                templates = map(lambda x: dict([('template', x[0]), ('frequency', x[1])]), collections.Counter(result[idx][tripleset]).items())
                fjson['sizes'][idx]['entries'].append({
                    'orderedset': list(tripleset),
                    'templates': templates
                })

        return fjson


if __name__ == '__main__':
    entryset = p.load(open('corpus/dev.cPickle', 'rb'))