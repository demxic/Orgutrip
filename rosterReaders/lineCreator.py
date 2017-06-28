from data import rules
from model.scheduleClasses import Line, Flight, GroundDuty, DutyDay, Trip, Itinerary
from datetime import datetime, timedelta


class Liner(object):
    """´Turns a Roster Reader into a bidline"""

    # TODO: Combining two one day-spaced duties into a single Duty Day.

    def __init__(self, date_tracker, roster_days, line_type='scheduled'):
        """Mandatory arguments"""
        print("wihtin Liner datetracker ", date_tracker)
        self.date_tracker = date_tracker
        self.roster_days = roster_days
        self.itinerary_builder = ItinBuilder()
        self.line_type = line_type
        month = self.date_tracker.month
        year = self.date_tracker.year
        self.line = Line(month, year)

    def build_line(self):
        """Returns a Line object containing all data read from the text file
        but now turned into corresponding objects"""
        trip_number_tracker = '0000'
        trip = None
        # print()
        # print()
        # print()
        # print(100*'*')
        # print("We are now building a line ")

        for rosterDay in self.roster_days:
            # Go over all roster days
            self.date_tracker.replace(rosterDay.day)
            # print("day ", rosterDay.day, " replaced in datetracker now ",
            #       self.date_tracker)

            if 1 <= len(rosterDay.name) <= 2:
                # Found groundDuty information
                duty_day = self.from_ground_itinerary(rosterDay)
                self.line.append(duty_day)

            else:
                # Found trip information
                trip_number = rosterDay.name
                duty_day = self.from_flight_itinerary(rosterDay)

                if trip_number != trip_number_tracker:
                    # A new trip has been found, let's create it
                    # print("A new trip has been found ")
                    trip = Trip(trip_number, duty_day.report, rules)
                    trip_number_tracker = trip.number
                    self.line.append(trip)

                # print("Adding duty_day ")
                trip.append(duty_day)

    def from_flight_itinerary(self, roster_day):
        """Given a group of duties, add them to a DutyDay"""
        duty_day = DutyDay()
        # print("print roster_day.sequence: ", roster_day.sequence)
        for itin in roster_day.sequence:
            # print("print itin: ", itin)
            itinerary = self.itinerary_builder.convert(self.date_tracker.dated, itin.begin, itin.end)
            if self.line_type == 'scheduled':
                f = Flight(itin.name, itin.origin, itin.destination, itinerary)
            else:
                f = Flight(itin.name, itin.origin, itin.destination, None, itinerary)
            duty_day.append(f)
        return duty_day

    def from_ground_itinerary(self, rD):
        """Given a ground duty, add it to a DutyDay"""
        duty_day = DutyDay()
        itinerary = self.itinerary_builder.convert(self.date_tracker.dated,
                                                   rD.sequence['begin'], 
                                                   rD.sequence['end'])
        if self.line_type == 'scheduled':
            i = GroundDuty(rD.name, itinerary)
        else:
            i = GroundDuty(rD.name, None, itinerary)
        duty_day.append(i)
        return duty_day


class ItinBuilder(object):
    """Given string parameters, this adapter will return a dictionary containing the corresponding
    parameters turned into objects, thus creating Itinerary objects from strings
    in any given timezone."""

    def __init__(self, airport_where_time = None):
        """
        airport_where_time asks for the 3-letter airport code of the timeZone, defaults to None.
        A None value, indicates local times
        """
        # self.dataTZ = citiesDic[airport_where_time].timezone if airport_where_time else None
        self.dataTZ = airport_where_time
        
    def convert(self, dated, begin, end):
        """date should  be a datetime object
        begin and end should have a %H%M (2345) format
        origin and destination are three-letter airport codes
        :type date: datetime.date"""

        begin, end = self.given_time_zone(dated, begin, end)
        return Itinerary(begin, end)

    @staticmethod
    def given_time_zone(dated, begin, end):
        """Generate begin and end datetime objects unaware"""

        formatting = '%H%M'
        begin_string = datetime.strptime(begin, formatting).time()
        begin = datetime.combine(dated, begin_string)
        end_string = datetime.strptime(end, formatting).time()
        end = datetime.combine(dated, end_string)

        if end < begin:
            end += timedelta(days = 1)
        # if end_day:
        #     end.replace(day = int(end_day))

        # begin = self.dataTZ.localize(begin)
        # end = self.dataTZ.localize(end)

        return begin, end
