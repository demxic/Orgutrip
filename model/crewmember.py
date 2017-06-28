class CrewMember(object):
    'Defines a CrewMember'

    def __init__(self, crew_member_id=None, name=None, pos=None, group=None, base=None, seniority=None):
        self.crew_member_id = crew_member_id
        self.name = name
        self.pos = pos
        self.group = group
        self.base = base
        self.seniority = seniority
        self.salary = 0
        self.line = None

    def __str__(self):
        return self.crew_member_id + ' ' + self.name
