"""
Created on 29/12/2015

@author: Xico

A bidline reader should return a bidline

"""
from data.regex import crewstats_no_type, crewstats_with_type,\
    rosterDayRE, airItineraryRE, itineraryRE, carryInRE
from model.elements import Dotdict


class RosterReader(object):
    def __init__(self, fp=None):
        """
        Receives an fp iterable and reads out all roster information
        """
        self.fp = fp
        self.crew_stats = None
        self.carry_in = None
        self.roster_days = []
        self.timeZone = None
        self.month = None
        self.year = None
        self.read_data()

    def read_data(self):
        """
        Iterates thru all roster rows and collects data needed to
        create event objects.
        Data may be of three types
        - roster_day
        - heather of a roster file
        - crew_stats or information of the crew member
        """

        for row in self.fp:

            if self.carry_in is None and carryInRE.match(row):
                # Month should start in number 1 or else there is a carry in
                cin = carryInRE.match(row).groupdict()
                self.carry_in = int(cin['day']) > 1

            roster_day = rosterDayRE.match(row)
            if roster_day:
                # Found a valid row with information of a duty
                roster_day = clean(roster_day.groupdict())
                self.roster_days.append(roster_day)

            elif 'SERVICIOS' in row.upper():
                # Found the header of the roster, extract month and year
                self.set_date(row)

            elif crewstats_no_type.search(row):
                # Found all crewMember stats. Of particular importance are the
                # timeZone of the given bidLine.
                crew_stats = crewstats_no_type.search(row).groupdict()
                self.timeZone = crew_stats.pop('timeZone')
                self.crew_stats = crew_stats

            elif crewstats_with_type.search(row):
                # Found all crewMember stats. Of particular importance are the
                # timeZone of the given bidLine.
                crew_stats = crewstats_with_type.search(row).groupdict()
                self.timeZone = crew_stats.pop('timeZone')
                self.crew_stats = crew_stats

    def set_date(self, row):
        """Given a row with a ___________  MONTH YEAR format string,
        read its year and month"""
        rs = row.upper().split()
        self.year = int(rs.pop())
        self.month = rs.pop()


def clean(roster_day):
    """
        Given a roster_day as a String, clean it up and return it as a DotDict
    """
    # print("\n\nIam inside the clean(roster_day) method")
    # print("roster_day (as a Dotdict): ")
    roster_day = Dotdict(**roster_day)
    # print("\n\t\t", roster_day)
    if len(roster_day.name) == 4:
        # print("the above roster_day belongs to a Trip")
        # Found information of a trip
        # Turn all flights in this roster day into a list
        flights = airItineraryRE.finditer(roster_day.sequence)
        cleaned_seq = [Dotdict(flight.groupdict()) for flight in flights]
        # print("And the cleaned_seq from roster_day looks like this: ")
        # print("\n\t\t", cleaned_seq)
    else:
        # Found information of a ground duty
        try:
            cleaned_seq = Dotdict(itineraryRE.search(roster_day.sequence).groupdict())
        except:
            print("roster_day:")
            print(roster_day)
            print("Enter sequence for ", roster_day.name)
            sequence = input()
            roster_day.sequence = sequence
            cleaned_seq = Dotdict(itineraryRE.search(roster_day.sequence).groupdict())

    roster_day.sequence = cleaned_seq
    # print("This is how roster_day looks after being cleaned up: ")
    # print("\n\t\t", roster_day)
    # print("\n\n")

    return roster_day

