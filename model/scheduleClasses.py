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

    def __str__(self):
        template = "{0.begin:%d%b} BEGIN {0.begin:%H%M} END {0.end:%H%M}"
        return template.format(self)


class Marker(object):
    """
    Represents  Vacations, GDO's, time-off, etc.
    Markers don't account for duty or block time in a given month
    """

    def __init__(self, name, published_itinerary=None, actual_itinerary=None):
        self.name = name
        self.published_itinerary = published_itinerary
        self.actual_itinerary = actual_itinerary
        self.is_flight = False

    @property
    def begin(self):
        return self.actual_itinerary.begin if self.actual_itinerary else self.published_itinerary.begin

    @property
    def end(self):
        return self.actual_itinerary.end if self.actual_itinerary else self.published_itinerary.end

    @property
    def duration(self):
        """How long is the Marker"""
        return Duration(self.end - self.begin)

    def compute_basic_credits(self, creditator):
        return None

    def calculate_credits(self, creditator):
        return None

    def __str__(self):
        template = "{0.name} {0.begin:%d%b} BEGIN {0.begin:%H%M} END {0.end:%H%M}"
        return template.format(self)


class GroundDuty(Marker):
    """
    Represents  training, reserve or special assignments.
    """
    def __init__(self, name, published_itinerary=None, actual_itinerary=None, origin='MEX', destination='MEX', equipment=None):
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

    def compute_basic_credits(self):
        return self.block, self.dh

    @property
    def block(self):
        return Duration(0)

    @property
    def dh(self):
        return Duration(0)

    def as_robust_string(self, rpt=4*'', rls=4*'', turn=4*''):
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

        # TODO : This might be printing always a block time even when deadheding
        template = """
        {0.begin:%d%b} {rpt:4s} {0.name:<6s} {0.origin} {0.begin:%H%M} {0.destination} {0.end:%H%M} {rls:4s} {block:0}       {turn:4s}       {eq}"""
        eq = self.equipment if self.equipment else 3 * ''
        block, _ = self.compute_basic_credits()
        return template.format(self, rpt=rpt, rls=rls, block=block, turn=turn, eq=eq)


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

    @property
    def block(self):
        if self.name.isdigit():
            return self.duration
        else:
            return Duration(0)

    @property
    def dh(self):
        if self.name.isdigit():
            return Duration(0)
        else:
            return self.duration

    def compute_basic_credits(self):
        return self.block, self.dh

    def __str__(self):
        template = """
        {0.begin:%d%b} {0.name:>6s} {0.origin} {0.begin:%H%M} {0.destination} {0.end:%H%M}\
        {0.duration:2}        {eq}
        """
        eq = self.equipment if self.equipment else 3*''
        return template.format(self, eq=eq)


class DutyDay(object):
    """
    A DutyDay is a collection of Events, it is not a representation of a regular calendar day,
    but rather the collection of Events to be served within a given Duty.
    """

    def __init__(self):
        self.events = []

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
    def duration(self):
        """How long is the DutyDay"""
        return Duration(self.release - self.report)

    @property
    def turns(self):
        return [Duration(j.begin - i.end) for i, j in zip(self.events[:-1], self.events[1:])]

    @property
    def block(self):
        block, dh, dur = self.compute_basic_credits()
        return block

    @property
    def dh(self):
        block, dh, dur = self.compute_basic_credits()
        return dh

    @property
    def origin(self):
        return self.events[0].origin

    def compute_basic_credits(self):
        """
        1. Calculate dh and block time
        2. Calulate all turnarond times
        """
        total_block = Duration(0)
        total_dh = Duration(0)
        for event in self.events:
            block, dh = event.compute_basic_credits()
            total_block += block
            total_dh += dh
        return total_block, total_dh, self.duration

    def calculate_credits(self, creditator):
        return creditator.to_credit_row(self)

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
        self.compute_basic_credits()
        rpt = '{:%H%M}'.format(self.report)
        rls = '    '
        body = ''
        if len(self.events) > 1:
            for event, turn in zip(self.events, self.turns):
                turn = format(turn, '0')
                body = body + event.as_robust_string(rpt, rls, turn)
                rpt = 4*''
            rls = '{:%H%M}'.format(self.release)
            body = body + self.events[-1].as_robust_string(rls=rls)
        else:
            rls = '{:%H%M}'.format(self.release)
            body = self.events[-1].as_robust_string(rpt, rls, 4*'')

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

    @property
    def report(self):
        return self.duty_days[0].report

    @property
    def release(self):
        return self.duty_days[-1].release

    @property
    def rests(self):
        """Returns a list of all calculated rests between each duty_day"""
        return [Duration(j.report-i.release) for i, j in zip(self.duty_days[:-1], self.duty_days[1:])]

    @property
    def layovers(self):
        """Returns a list of all layover stations """
        return [duty_day.events[-1].destination for duty_day in self.duty_days]

    def compute_basic_credits(self):
        total_block = Duration(0)
        total_dh = Duration(0)
        total_daily = Duration(0)
        for duty_day in self.duty_days:
            block, dh, daily = duty_day.compute_basic_credits()
            total_block += block
            total_dh += dh
            total_daily += daily
        tafb = Duration(self.release - self.report)
        return total_block + total_dh, total_block, total_dh, tafb

    def calculate_credits(self, creditator):
        '''Returns a credit holder '''
        credit_table = creditator.new_credit_table()
        for duty_day in self.duty_days:
            credit_row = duty_day.calculate_credits(creditator)
            if duty_day.begin.month == creditator.month_scope:
                credit_table.append(credit_row)
        for index, rest in enumerate(self.rests):
            pending_rest = creditator.calculate_pending_rest(rest)
            if pending_rest:
                credit_table[index].pending_rest = pending_rest

        return credit_table

    def append(self, duty_day):
        """Simply append a duty_day"""
        self.duty_days.append(duty_day)

    def pop(self, index=-1):
        return self.duty_days.pop(index)

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
        header_template = """
        # {0.number}                                                  CHECK IN AT {0.report:%H:%M}
        {0.report:%d%b%Y}
        DATE  RPT  FLIGHT DEPARTS  ARRIVES  RLS  BLK        TURN        EQ"""

        body_template = """{duty_day}
                     {destination} {rest}                   {bl:0}BL {cr:0}CRD {tl:0}TL {dy:0}DY"""

        footer_template = """

          TOTALS     {tl:2}TL     {bl:2}BL     {cr:2}CR           {tafb:2}TAFB"""

        header = header_template.format(self)
        body = ''

        for duty_day, rest in zip(self.duty_days, self.rests):
            rest = repr(rest)
            block, dh, daily = duty_day.compute_basic_credits()
            total = block + dh
            body = body + body_template.format(duty_day=duty_day,
                                               destination=duty_day.events[-1].destination,
                                               rest=rest,
                                               bl=block,
                                               cr=dh,
                                               tl=total,
                                               dy=daily)
        else:
            duty_day = self.duty_days[-1]
            block, dh, daily = duty_day.compute_basic_credits()
            total = block + dh
            body = body + body_template.format(duty_day=duty_day,
                                               destination='    ',
                                               rest='    ',
                                               bl=block,
                                               cr=dh,
                                               tl=total,
                                               dy=daily)
        total, block, dh, tafb = self.compute_basic_credits()
        footer = footer_template.format(tl=total, bl=block, cr=dh, tafb=tafb)
        return header + body + footer


class Line(object):
    """ Represents an ordered sequence of events for a given month"""

    def __init__(self, month, year, crew_member=None):
        self.duties = []
        self.month = month
        self.year = year
        self.crewMember = crew_member
        self.creditator = None

    def append(self, duty):
        self.duties.append(duty)

    def calculate_credits(self, creditator):
        credit_table = creditator.new_credit_table()
        for duty in self.duties:
            credit_holder = duty.calculate_credits(creditator)
            if credit_holder:
                credit_table.append(credit_holder)
        return credit_table

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
