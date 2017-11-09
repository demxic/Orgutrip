"""
Created on 29/12/2015

@author: Xico

A bidline reader should return a bidline

"""
import io
from data.regex import crewstats_no_type, crewstats_with_type,\
    rosterDayRE, airItineraryRE, itineraryRE, carryInRE
from model.elements import Dotdict
from pdfminer import high_level, layout


# TODO : This basically returns a JSON format of the given roster
class RosterReaderTemplate(object):
    def __init__(self, path):
        """
        Receives """
        self.path = path
        self.crew_stats = None
        self.carry_in = None
        self.roster_as_string = None
        self.roster_days = []
        self.timeZone = None
        self.month = None
        self.year = None

    def read_file(self):
        raise NotImplementedError

    def build(self):
        """
        Iterates thru all roster rows and collects data needed to
        create event objects.
        Data may be of three types
        - roster_day
        - heather of a roster file
        - crew_stats or information of the crew member
        """

        for row in self.roster_as_string:

            if self.carry_in is None and carryInRE.match(row):
                # Month should start in number 1 or else there is a carry in
                cin = carryInRE.match(row).groupdict()
                self.carry_in = int(cin['day']) > 1

            roster_day = rosterDayRE.match(row)
            if roster_day:
                # Found a valid row with information of a duty
                roster_day = self.clean(roster_day.groupdict())
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
                print(self.crew_stats)

            elif crewstats_with_type.search(row):
                # Found all crewMember stats. Of particular importance are the
                # timeZone of the given bidLine.
                crew_stats = crewstats_with_type.search(row).groupdict()
                self.timeZone = crew_stats.pop('timeZone')
                self.crew_stats = crew_stats
                print(self.crew_stats)

    def set_date(self, row):
        """Given a row with a ___________  MONTH YEAR format string,
        read its year and month"""
        rs = row.upper().split()
        self.year = int(rs.pop())
        self.month = rs.pop()

    def clean(self, roster_day):
        """
            Given a roster_day as a String, clean it up and return it as a DotDict
        """
        roster_day = Dotdict(**roster_day)
        if len(roster_day.name) == 4:
            flights = airItineraryRE.finditer(roster_day.sequence)
            cleaned_seq = [Dotdict(flight.groupdict()) for flight in flights]
        else:
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
        return roster_day

    def save_as_json(self):
        pass


class TxtRosterReader(RosterReaderTemplate):

    def read_file(self):
        fp = open(self.path, 'r')
        self.roster_as_string = fp.readlines()
        fp.close()


class PdfRosterReader(RosterReaderTemplate):

    def read_file(self):
        output = io.StringIO()
        laparams = layout.LAParams()
        with open(self.path, "rb") as pdffile:
            high_level.extract_text_to_fp(pdffile, output, laparams=laparams)
        self.roster_as_string = output.getvalue().split('\n')

