from datetime import timedelta

from model.timeClasses import Duration


# TODO : Apply the observer pattern to all classes so that calculated values may be updated on the fly


class Itinerary(object):
    """ An Itinerary represents a Duration occurring between a 'begin' and an 'end' time. """

    def __init__(self, begin, end):
        """
        :Duration duration: Duration
        """
        self.begin = begin
        self.end = end

    @classmethod
    def from_timedelta(cls, begin, a_timedelta):
        """Returns an Itinerary from a given begin datetime and the timedelta duration of it"""
        end = begin + a_timedelta
        return cls(begin, end)

    @property
    def duration(self):
        return Duration(self.end - self.begin)

    def compute_credits(self, itinerator = None):
        return None

    def overlaps(self, other):
        begin_date = self.begin.date()
        overlap = max(0, min(self.end, other.end) - max(self.begin, other.begin))
        return overlap

    def __str__(self):
        template = "{0.begin:%d%b} BEGIN {0.begin:%H%M} END {0.end:%H%M}"
        return template.format(self)


class Marker(Itinerary):
    """
    Represents  Vacations, GDO's, time-off, etc.
    Markers don't account for duty or block time in a given month
    """

    def __init__(self, name, published_itinerary=None, actual_itinerary=None):
        self.name = name
        self.published_itinerary = published_itinerary
        self.actual_itinerary = actual_itinerary
        self.is_flight = False
        self._credits = None

    @property
    def begin(self):
        return self.actual_itinerary.begin if self.actual_itinerary else self.published_itinerary.begin

    @property
    def end(self):
        return self.actual_itinerary.end if self.actual_itinerary else self.published_itinerary.end

    def __str__(self):
        template = "{0.name} {0.begin:%d%b} BEGIN {0.begin:%H%M} END {0.end:%H%M}"
        return template.format(self)


class GroundDuty(Marker):
    """
    Represents  training, reserve or special assignments.
    """

    def __init__(self, name, published_itinerary=None, actual_itinerary=None, origin='MEX', destination='MEX',
                 equipment=None):
        super().__init__(name, published_itinerary, actual_itinerary)
        self.origin = origin
        self.destination = destination
        self.equipment = equipment

    @property
    def report(self):
        return self.published_itinerary.begin if self.published_itinerary else self.actual_itinerary.begin

    @property
    def release(self):
        return self.end

    def compute_credits(self, creditator=None):
        self._credits = {'block': Duration(0), 'dh': Duration(0)}

    def as_robust_string(self, rpt=4 * '', rls=4 * '', turn=4 * ''):
        """Prints a Ground Duty following this heather template
        DATE  RPT  FLIGHT DEPARTS  ARRIVES  RLS  BLK        TURN       EQ
        05JUN 0900 E6     MEX 0900 MEX 1500 1500 0000

        OR ********************************************************************
        Prints a Flight following this heather template
        DATE  RPT  FLIGHT DEPARTS  ARRIVES  RLS  BLK        TURN       EQ
        03JUN 1400 0924   MEX 1500 MTY 1640 1720 0140       0000       738


        Following arguments being optional
        rpt : report
        rls : release
        turn: turn around time
        eq : equipment"""

        template = """
        {0.begin:%d%b} {rpt:4s} {0.name:<6s} {0.origin} {0.begin:%H%M} {0.destination} {0.end:%H%M} {rls:4s} {block:0}       {turn:4s}       {eq}"""
        eq = self.equipment if self.equipment else 3 * ''
        self.compute_credits()
        block = self._credits['block']
        return template.format(self, rpt=rpt, rls=rls, turn=turn, eq=eq, block=block)


class Flight(GroundDuty):
    def __init__(self, name, origin, destination, published_itinerary=None, actual_itinerary=None,
                 equipment=None, carrier='AM'):
        """
        Holds those necessary fields to represent a Flight Itinerary
        """
        super().__init__(name, published_itinerary, actual_itinerary, origin, destination, equipment)
        self.carrier = carrier
        self.is_flight = True

    @property
    def report(self):
        """Flight's report time"""
        return super().report - timedelta(hours=1)

    @property
    def release(self):
        """Flights's release time """
        return super().release + timedelta(minutes=30)

    def compute_credits(self, creditator=None):
        if self.name.isdigit():
            block = self.duration
            dh = Duration(0)
        else:
            dh = self.duration
            block = Duration(0)
        self._credits = {'block': block, 'dh': dh}

    def __str__(self):
        template = """
        {0.begin:%d%b} {0.name:>6s} {0.origin} {0.begin:%H%M} {0.destination} {0.end:%H%M}\
        {0.duration:2}        {eq}
        """
        eq = self.equipment if self.equipment else 3 * ''
        return template.format(self, eq=eq)


class DutyDay(object):
    """
    A DutyDay is a collection of Events, it is not a representation of a regular calendar day,
    but rather the collection of Events to be served within a given Duty.
    """

    def __init__(self):
        self.events = []
        self._credits = {}

    @property
    def begin(self):
        return self.events[0].begin

    @property
    def end(self):
        return self.events[-1].end

    @property
    def report(self):
        return self.events[0].report

    @property
    def release(self):
        return self.events[-1].release

    @property
    def delay(self):
        delay = Duration(self.begin - self.report) - Duration(60)
        return delay

    @property
    def duration(self):
        """How long is the DutyDay"""
        return Duration(self.release - self.report)

    @property
    def turns(self):
        return [Duration(j.begin - i.end) for i, j in zip(self.events[:-1], self.events[1:])]

    @property
    def origin(self):
        return self.events[0].origin

    def compute_credits(self, creditator=None):
        """Cares only for block, dh, total and daily"""
        # TODO : Take into consideration whenever there is a change in month
        if creditator:
            creditator.credits_from_duty_day(self)
        else:
            self._credits['block'] = Duration(0)
            self._credits['dh'] = Duration(0)
            for event in self.events:
                event.compute_credits(creditator)
                self._credits['block'] += event._credits['block']
                self._credits['dh'] += event._credits['dh']

            self._credits.update({'daily': self.duration,
                                  'total': self._credits['block'] + self._credits['dh']})
        return [self._credits]

    def append(self, current_duty):
        """Add a duty, one by one  to this DutyDay"""
        self.events.append(current_duty)

    def merge(self, other):
        if self.report <= other.report:
            all_events = self.events + other.events
        else:
            all_events = other.events + self.events
        self.events = []
        for event in all_events:
            self.events.append(event)

    def __str__(self):
        """The string representation of the current DutyDay"""
        rpt = '{:%H%M}'.format(self.report)
        rls = '    '
        body = ''
        if len(self.events) > 1:
            for event, turn in zip(self.events, self.turns):
                turn = format(turn, '0')
                body = body + event.as_robust_string(rpt, rls, turn)
                rpt = 4 * ''
            rls = '{:%H%M}'.format(self.release)
            body = body + self.events[-1].as_robust_string(rls=rls)
        else:
            rls = '{:%H%M}'.format(self.release)
            body = self.events[-1].as_robust_string(rpt, rls, 4 * '')

        return body


class Trip(object):
    """
        A trip is a collection of DutyDays
        It should be started by passing in a Trip number
    """

    def __init__(self, number, dated):
        self.number = number
        self.duty_days = []
        self.dated = dated
        self._credits = {}

    @property
    def report(self):
        return self.duty_days[0].report

    @property
    def release(self):
        return self.duty_days[-1].release

    @property
    def rests(self):
        """Returns a list of all calculated rests between each duty_day"""
        return [Duration(j.report - i.release) for i, j in zip(self.duty_days[:-1], self.duty_days[1:])]

    @property
    def layovers(self):
        """Returns a list of all layover stations """
        return [duty_day.events[-1].destination for duty_day in self.duty_days]

    def compute_credits(self, creditator=None):

        if creditator:
            return creditator.credits_from_trip(self)
        else:
            self._credits['block'] = Duration(0)
            self._credits['dh'] = Duration(0)
            self._credits['daily'] = Duration(0)
            for duty_day in self.duty_days:
                duty_day.compute_credits(creditator)
                self._credits['block'] += duty_day._credits['block']
                self._credits['dh'] += duty_day._credits['dh']
                self._credits['daily'] += duty_day._credits['daily']
            self._credits.update({'total': self._credits['block'] + self._credits['dh'],
                                  'tafb': Duration(self.release - self.report)})

    def append(self, duty_day):
        """Simply append a duty_day"""
        self.duty_days.append(duty_day)

    def pop(self, index=-1):
        return self.duty_days.pop(index)

    def how_many_sundays(self):
        delta = self.release.date() - self.report.date()
        all_dates = (self.report.date() + timedelta(days=i) for i in range(delta.days + 1))
        sundays = filter(lambda date: date.isoweekday() == 7, all_dates)
        return len(list(sundays))

    def __delitem__(self, key):
        del self.duty_days[key]

    def __getitem__(self, key):
        try:
            item = self.duty_days[key]
        except:
            item = None
        return item

    def __setitem__(self, key, value):
        self.duty_days[key] = value

    def __str__(self):
        self.compute_credits()
        header_template = """
        # {0.number}                                                  CHECK IN AT {0.report:%H:%M}
        {0.report:%d%b%Y}
        DATE  RPT  FLIGHT DEPARTS  ARRIVES  RLS  BLK        TURN        EQ"""

        body_template = """{duty_day}
                     {destination} {rest}                   {block:0}BL {dh:0}CRD {total:0}TL {daily:0}DY"""

        footer_template = """

          TOTALS     {total:2}TL     {block:2}BL     {dh:2}CR           {tafb:2}TAFB"""

        header = header_template.format(self)
        body = ''

        for duty_day, rest in zip(self.duty_days, self.rests):
            rest = repr(rest)
            body = body + body_template.format(duty_day=duty_day,
                                               destination=duty_day.events[-1].destination,
                                               rest=rest,
                                               **duty_day._credits)
        else:
            duty_day = self.duty_days[-1]
            body = body + body_template.format(duty_day=duty_day,
                                               destination='    ',
                                               rest='    ',
                                               **duty_day._credits)

        footer = footer_template.format(**self._credits)
        return header + body + footer


class Line(object):
    """ Represents an ordered sequence of events for a given month"""

    def __init__(self, month, year, crew_member=None):
        self.duties = []
        self.month = month
        self.year = year
        self.crewMember = crew_member
        self._credits = {}

    def append(self, duty):
        self.duties.append(duty)

    def compute_credits(self, creditator=None):
        self._credits['block'] = Duration(0)
        self._credits['dh'] = Duration(0)
        self._credits['daily'] = Duration(0)
        for duty in self.duties:
            cr = duty.compute_credits()
            if cr:
                self._credits['block'] += duty._credits['block']
                self._credits['dh'] += duty._credits['dh']
                self._credits['daily'] += duty._credits['daily']

        if creditator:
            credits_list = creditator.credits_from_line(self)

        return credits_list

    def return_duty(self, dutyId):
        """Return the corresponding duty for the given dutyId"""
        return (duty for duty in self.duties if duty.id == dutyId)

    def __delitem__(self, key):
        del self.duties[key]

    def __getitem__(self, key):
        try:
            item = self.duties[key]
        except:
            item = None
        return item

    def __setitem__(self, key, value):
        self.duties[key] = value

    def __iter__(self):
        return iter(self.duties)

    def return_duty_days(self):
        """Turn all dutydays to a list called dd """
        dd = []
        for element in self.duties:
            if isinstance(element, Trip):
                dd.extend(element.duty_days)
            elif isinstance(element, DutyDay):
                dd.append(element)
        return dd

    def __str__(self):
        return "\n".join(str(d) for d in self.duties)
