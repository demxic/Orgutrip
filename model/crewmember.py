class CrewMember(object):
    'Defines a CrewMember'

    def __init__(self, id_=None, name=None, pos=None, group=None, base=None, seniority=None):
        self.id = id_
        self.name = name
        self.pos = pos
        self.group = group
        self.base = base
        self.seniority = seniority

    def __str__(self):
        return self.id + ' ' + self.name
