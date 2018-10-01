
class Entry():
    def __init__(self, category, eid, size, originaltripleset, modifiedtripleset, entitymap, lexEntries):
        self.category = category
        self.eid = eid
        self.size = size
        self.originaltripleset = originaltripleset
        self.modifiedtripleset = modifiedtripleset
        self.lexEntries = lexEntries
        self.entitymap = entitymap

    def entitymap_to_dict(self):
        return dict(map(lambda tagentity: tagentity.to_tuple(), self.entitymap))

class Triple():
    def __init__(self, subject, predicate, object):
        self.subject = subject
        self.predicate = predicate
        self.object = object

class Lex():
    def __init__(self, comment, lid, text, template):
        self.comment = comment
        self.lid = lid
        self.text = text
        self.template = template
        self.orderedtripleset = []
        self.references = []

        # german entry
        self.text_de = ''
        self.template_de = ''
        self.orderedtripleset_de = []
        self.references_de = []

class TagEntity():
    def __init__(self, tag, entity):
        self.tag = tag
        self.entity = entity

    def to_tuple(self):
        return (self.tag, self.entity)

class Reference():
    def __init__(self, tag, entity, refex, number):
        self.tag = tag
        self.entity = entity
        self.refex = refex
        self.number = number