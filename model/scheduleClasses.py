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
        return self.published_itinerary.begin if self.published_itinerary else self.actual_itinerary.begin

    @property
    def end(self):
        return self.actual_itinerary.end if self.actual_itinerary else self.published_itinerary.end

    @property
    def duration(self):
        """How long is the Marker"""
        return Duration(self.end - self.begin)

    def calculate_credits(self):
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
        return self.begin

    @property
    def release(self):
        return self.end

    def calculate_credits(self):
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
        block, _ = self.calculate_credits()
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
        return self.begin - timedelta(hours=1)

    @property
    def release(self):
        """Flights's release time """
        return self.end + timedelta(minutes=30)

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

    def calculate_credits(self):
        return self.block, self.dh

    def __str__(self):
        template = """
        {0.begin:%d%b} {0.name:>6s} {0.origin} {0.begin:%H%M} {0.destination} {0.end:%H%M}
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
        block, dh, dur = self.calculate_credits()
        return block

    @property
    def dh(self):
        block, dh, dur = self.calculate_credits()
        return dh

    def calculate_credits(self):
        """
        1. Calculate dh and block time
        2. Calulate all turnarond times
        """
        print("Estoy dentro del método calculate_credits del DutyDay")
        total_block = Duration(0)
        total_dh = Duration(0)
        for event in self.events:
            block, dh = event.calculate_credits()
            total_block += block
            total_dh += dh
        return total_block, total_dh, self.duration

    def append(self, current_duty):
        """Add a duty, one by one  to this DutyDay"""
        self.events.append(current_duty)

    def combine(self, other):
        dd = DutyDay()
        if self.report <= other.report:
            all_events = self.events + other.events
        else:
            all_events = other.events + self.events
        for event in all_events:
            dd.append(event)
        return dd

    def __str__(self):
        """The string representation of the current DutyDay"""
        self.calculate_credits()
        rpt = '{:%H%M}'.format(self.report)
        rls = '    '
        body = ''
        print("estoy dentro del método str de DutyDay")
        print("el valor de self.turns es:")
        print(self.turns)
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
        
    # def __str__(self):
    #     """The string representation of the current DutyDay"""
    #     rpt = '{:%H%M}'.format(self.report)
    #     rls = 4*''
    #     body = ''
    #     if len(self.events) > 1:
    #         for event, turn in zip(self.events, self.turns):
    #             turn = format(turn, '0')
    #             body = body + event.as_robust_string(rpt, rls, turn)
    #             rpt = 4*''
    #         rls = '{:%H%M}'.format(self.release)
    #         body = body + self.events[-1].as_robust_string(rls=rls)
    #     else:
    #         rls = '{:%H%M}'.format(self.release)
    #         body = self.events[-1].as_robust_string(rpt, rls, 4*'')
    #
    #     return body


class Trip(object):
    """
        A trip is a collection of DutyDays
        It should be started by passing in a Trip number
    """

    def __init__(self, number, dated, rules=None):
        self.number = number
        self.duty_days = []
        self.dated = dated
        self.rules = rules
        self.layovers = []
        self.rests = []

    @property
    def report(self):
        return self.duty_days[0].report

    @property
    def release(self):
        return self.duty_days[-1].release

    def calculate_credits(self):
        total_block = Duration(0)
        total_dh = Duration(0)
        total_daily = Duration(0)
        for duty_day in self.duty_days:
            block, dh, daily = duty_day.calculate_credits()
            total_block += block
            total_dh += dh
            total_daily += daily
        tafb = Duration(self.release - self.report)
        return total_block + total_dh, total_block, total_dh, tafb

    def append(self, duty_day):
        """ Will append duty_day to self provided the minimum rest time"""
        try:
            previous_duty_day = self.duty_days[-1]
            rest = duty_day.report - previous_duty_day.release
            # Checking for events worked in different calendar days but belong to the same duty day
            # TODO : This needs to take into account rest time, algorithm not working properly
            if rest.total_seconds() <= self.rules.MINIMUM_REST_TIME:
                self.pop()
                duty_day = previous_duty_day.combine(duty_day)
            rest = duty_day.report - previous_duty_day.release
            self.rests.append(Duration(rest))
            self.layovers.append(duty_day.events[-1].destination)
        except IndexError:
            pass

        self.duty_days.append(duty_day)

    def pop(self, index=-1):
        try:
            return self.duty_days.pop(index)
        except IndexError:
            return None

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
            block, dh, daily = duty_day.calculate_credits()
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
            block, dh, daily = duty_day.calculate_credits()
            total = block + dh
            body = body + body_template.format(duty_day=duty_day,
                                               destination='    ',
                                               rest='    ',
                                               bl=block,
                                               cr=dh,
                                               tl=total,
                                               dy=daily)
        total, block, dh, tafb = self.calculate_credits()
        footer = footer_template.format(tl=total, bl=block, cr=dh, tafb=tafb)
        return header + body + footer

    # def credits(self, creditator):
    #     """Return the routing and the total block, dh, and duty time accounted for
    #     in a given duty day"""
    #
    #     credit_table = creditator.CreditTable()
    #     for dutyDay in self.duty_days:
    #         credit_table.append(dutyDay.credits(creditator))
    #
    #     return credit_table

    # def append(self, duty_day):
    # THIS APPEND IS ONE VERSION BEFORE CURRENT AND IT HELPS TO DEBUG
    #     """ Will append duty_day to self provided the minimum rest time"""
    #     previous_duty_day = self[-1]
    #
    #     if previous_duty_day:
    #         print("actual_itinerary duty_day begin ", duty_day.begin)
    #         print("previous duty_day end ", previous_duty_day.end)
    #         rest = duty_day.begin - previous_duty_day.end
    #         print("duty day rest: ", rest.total_seconds())
    #         if rest.total_seconds() <= self.rules.MINIMUM_REST_TIME:
    #             print("combining duty days with rest less than minimum required: ")
    #             print("previous day :")
    #             print(previous_duty_day)
    #             print("previous duty day begin ", previous_duty_day.begin)
    #             print("previous duty day end ", previous_duty_day.end)
    #             print()
    #             print("current day :")
    #             print("current duty day begin ", duty_day.begin)
    #             print("current duty day end ", duty_day.end)
    #             print(duty_day)
    #             print()
    #             print()
    #             self.pop()
    #             duty_day = previous_duty_day.combine(duty_day)
    #             print("New combined day: ")
    #             print(duty_day)
    #             print()
    #
    #     self.duty_days.append(duty_day)


class Line(object):
    """ Represents an ordered sequence of events for a given month"""

    def __init__(self, month, year, crew_member=None):
        self.duties = []
        self.month = month
        self.year = year
        self.crewMember = crew_member

    def append(self, duty):
        self.duties.append(duty)

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
            else:
                dd.append(element)
        return dd

    def __str__(self):
        return "\n".join(str(d) for d in self.duties)
