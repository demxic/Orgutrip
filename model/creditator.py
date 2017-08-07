"""
Created on 23/06/2016

@author: Xico
"""

import numpy as np
from model.timeClasses import Duration

string_section_template = "{day: >2} {routing!s:20s} {event_names!s:25s} {duty_type:18s} {report:%H:%M} " \
                              "{release:%H:%M}    "
numeric_section_template = " {daily:3} {block:3} {dh:3} {night_time:3} {xblock:3} " \
                               "{xduty_time:3} {maxirre:3} {pending_rest:3} {xturn:3}"

# TODO : Move all this constants into a configuration file, associated to method set_rules

TRANSOCEANIC = ['MAD', 'CDG', 'MXP', 'FCO', 'LHR', 'AMS', 'SVO', 'BCN', 'MUC', 'FRA', 'NRT', 'ICN', 'PVG', 'PEK']
MINIMUM_BLOCK = Duration(13 * 60)
MINIMUM_DUTY = Duration(15 * 60)

# TABLA 1  Jornada continental
JORNADA_ORDINARIA_VUELO_REGULAR = Duration(7 * 60 + 30)
MAXIMA_IRREBASABLE_VUELO_REGULAR = Duration(10 * 60)
JORNADA_ORDINARIA_SERVICIO_REGULAR = Duration(9 * 60)
MAXIMA_IRREBASABLE_SERVICIO_REGULAR = Duration(12 * 60)

# TABLA 1 Jornada transoceanica
JORNADA_ORDINARIA_VUELO_TRAN = Duration(8 * 60)
MAXIMA_IRREBASABLE_VUELO_TRAN = Duration(13 * 60)
JORNADA_ORDINARIA_SERVICIO_TRAN = Duration(10 * 60)
MAXIMA_IRREBASABLE_SERVICIO_TRAN = Duration(15 * 60)

# TABLA 2 Largo alcance
JORNADA_ORDINARIA_VUELO_LARGO_ALCANCE = Duration(8 * 60)
MAXIMA_ASIGNABLE_VUELO_LARGO_ALCANCE = Duration(13 * 60)
JORNADA_ORDINARIA_SERVICIO_LARGO_ALCANCE = Duration(10 * 60)
MAXIMA_ASIGNABLE_SERVICIO_LARGO_ALCANCE = Duration(15 * 60)

# TABLA 5 Jornada transoceanica especial
JORNADA_ORDINARIA_VUELO_TRANSP = Duration(8 * 60)
MAXIMA_IRREBASABLE_VUELO_TRANSP = Duration(16 * 60)
JORNADA_ORDINARIA_SERVICIO_TRANSP = Duration(10 * 60)
# Nota, la tabla 5 especifica que para efectos de pago, se pagara como tiempo
# de vulo al doble a partir de las 16:00 aunque la maxima asiganble sea 18:00

MAXIMA_IRREBASABLE_SERVICIO_TRANSP = Duration(16 * 60)

# Jornadas mensuales
JORNADA_ORDINARIA_VUELO_MENSUAL = Duration(65 * 60)
JORNADA_ORDINARIA_DH_MENSUAL = Duration(3 * 60)
GARANTIA_HORAS_DE_VUELO_MENSUAL = Duration(80 * 60)

# Otros créditos
RECESO_CONTINENTAL = Duration(12 * 60)
RECESO_TRANS = Duration(48 * 60)


def get_rules_for(position, group):
    pass


class Creditator(object):
    def __init__(self, position: str = None, group: str = None, month_scope=None) -> None:
        """According to the position and group, creditator should load the corresponding
        rules to build credit objects
        :rtype: None"""
        self.position = position
        self.group = group
        self.rules = None
        self.set_rules()
        self.month_scope = month_scope
        self.header = 'D  RUTA                 SERVICIOS              TIPO DE JORNADA       FIMA  CIERRE    ' \
                      'DUTY  BLK   DH    NOCT  XBLK  XDTY  IRRE  RECE  PLAT'

    def set_rules(self):
        pass

    def calculate_pending_rest(self, rest):
        pending_rest = RECESO_CONTINENTAL - rest
        return pending_rest

    def to_credits_dict(self, duty_day):
        """
        Builds and returns a CreditRow from a given DutyDay
        """
        # 1. Init our credits_dict
        duty_day.credits_dict.update({'day': duty_day.begin.day,
                                      'routing': FormattedList([duty_day.origin]),
                                      'report': duty_day.report,
                                      'release': duty_day.release,
                                      'duty_type': 'regular',
                                      'event_names': FormattedList(['']),
                                      'night_time': Duration(0),
                                      'xduty_time': Duration(0),
                                      'xblock': Duration(0),
                                      'maxirre': Duration(0),
                                      'pending_rest': Duration(0),
                                      'xturn': Duration(0)})

        # 2. Calculate night, event_names and routing
        for event in duty_day.events:
            # TODO : I don´t like this, should think of using isinstance or another alternative
            if event.is_flight:
                duty_day.credits_dict['night_time'] += Creditator.calculate_night_time(event.begin, event.end)
            duty_day.credits_dict['event_names'].append(event.name)
            duty_day.credits_dict['routing'].append(event.destination)

        # 3. Classify duty
        Creditator.credit_row_classifier(duty_day)

        if duty_day.credits_dict['duty_type'] == 'regular':
            duty_day.credits_dict['xblock'] = duty_day.credits_dict['block'] - JORNADA_ORDINARIA_VUELO_REGULAR
            duty_day.credits_dict['xduty_time'] = duty_day.credits_dict['daily'] - JORNADA_ORDINARIA_SERVICIO_REGULAR
            duty_day.credits_dict['maxirre'] = duty_day.credits_dict['daily'] - MAXIMA_IRREBASABLE_SERVICIO_REGULAR
        elif duty_day.credits_dict['duty_type'] == 'transoceanic':
            duty_day.credits_dict['xblock'] = duty_day.credits_dict['block'] - JORNADA_ORDINARIA_VUELO_TRAN
            duty_day.credits_dict['xduty_time'] = duty_day.credits_dict['daily'] - JORNADA_ORDINARIA_SERVICIO_TRAN
            duty_day.credits_dict['maxirre'] = duty_day.credits_dict['daily'] - MAXIMA_IRREBASABLE_SERVICIO_TRAN
            # If there is a maxirre, normal xduty time ends where maxirre starts
            if duty_day.credits_dict['maxirre'] > Duration(0):
                duty_day.credits_dict['xduty_time'] = Duration(5 * 60)
        elif duty_day.credits_dict['duty_type'] == 'special trans':
            duty_day.credits_dict['xblock'] = duty_day.credits_dict['block'] - JORNADA_ORDINARIA_VUELO_TRANSP
            duty_day.credits_dict['xduty_time'] = duty_day.credits_dict['daily'] - JORNADA_ORDINARIA_SERVICIO_TRANSP
            duty_day.credits_dict['maxirre'] = duty_day.credits_dict['daily'] - MAXIMA_IRREBASABLE_SERVICIO_TRANSP
            # If there is a maxirre, normal xduty time ends where maxirre starts
            if duty_day.credits_dict['maxirre'] > Duration(0):
                duty_day.credits_dict['xduty_time'] = Duration(6 * 60)

    @staticmethod
    def calculate_night_time(begin, end):
        """
        Returns the nighttime flown in a given event, value is returned in seconds
        """

        BEGIN = begin.hour * 60 + begin.minute
        END = end.hour * 60 + end.minute
        NIGHTTIME_BEGIN = 22 * 60
        NIGHTTIME_END = 5 * 60
        MIDNIGHT = 24 * 60
        morninginter = [0, NIGHTTIME_END]
        nightinter = [NIGHTTIME_BEGIN, MIDNIGHT]

        if BEGIN > END:  # Event starts and ends in different days
            total = Creditator.overlapping(nightinter, [BEGIN, MIDNIGHT]) + Creditator.overlapping(morninginter,
                                                                                                   [0, END])
        else:  # Event starts and ends in same day
            total = Creditator.overlapping(morninginter, [BEGIN, END]) + Creditator.overlapping(nightinter,
                                                                                                [BEGIN, END])

        return Duration(total)

    @staticmethod
    # TODO : Probably this should be integrated into all ScheduleClasses
    def overlapping(a, b):
        """
        returns the total overlapping time of periods a and b
        """
        return max(0, min(a[1], b[1]) - max(a[0], b[0]))

    @staticmethod
    def credit_row_classifier(duty_day):
        """Given a DutyDay, this classifier will insert the following tags:
           - regular : any continental flight under 10:00 duty time. It is the default value
           - transoceanic : MAD, CDG, MXP, FCO, LHR, AMS, SVO, BCN, MUC, FRA, NRT, ICN, PVG, PEK
           - special transoceanic :
                                    a) MUST be transoceanic
                                    b) scheduled block time > 13:00 hrs
                                    c) scheduled duty time  > 15:00 hrs
           - long haul : Any flight with
                                    a) #of legs <= 2
                                    b) AND at least one leg > 4:30 hrs
                                    c) AND
                                        - OR    BLK > 10:00
                                        - OR    DUTY > 12:00
                                        - OR    DUTY > 09:30 AND  DUTY.OVERLAPS(00:59, 04:59) inclusive
           """
        if set(duty_day.credits_dict['routing']).intersection(TRANSOCEANIC):
            duty_day.credits_dict['duty_type'] = 'transoceanic'
            if (duty_day.credits_dict['total']) > MINIMUM_BLOCK or duty_day.credits_dict['daily'] > MINIMUM_DUTY:
                duty_day.credits_dict['duty_type'] = 'special trans'
        # TODO : Implement the Long Haul definition
        elif len(duty_day.events) <= 2:
            for event in duty_day.events:
                if event.duration > Duration(4*60 + 30):
                # First two mandatory clauses met
                    if duty_day.credits_dict['block'] > Duration(10*60) or duty_day.credits_dict['daily'] > Duration(12*60):
                        duty_day.credits_dict['duty_type'] = 'long haul'
                        #TODO : Add the third condition (MISSING) *************

    def new_credit_table(self):
        return CreditTable()


class CreditRow(object):
    string_section_template = "{0.day: >2} {0.routing!s:20s} {0.event_names!s:25s} {0.duty_type:18s} {0.report:%H:%M} " \
                              "{0.release:%H:%M}    "
    numeric_section_template = " {0.duty_time:3} {0.block:3} {0.dh:3} {0.night_time:3} {0.xblock:3} " \
                               "{0.xduty_time:3} {0.maxirre:3} {0.pending_rest:3} {0.xturn:3}"

    def __init__(self, duty_day=None):
        """A CreditRow models all credits for a given DutyDay
            Note that a CreditRow has two sections, one containing all strings info
            and the second part contains the credits """
        if duty_day:
            self.day = duty_day.begin.day
            self.routing = FormattedList([duty_day.origin])
            self.block, self.dh, self.duty_time = duty_day.compute_credits()
            self.report = duty_day.report
            self.release = duty_day.release
        else:
            self.day = 2 * ' '
            self.routing = 3 * ' '
            self.block, self.dh, self.duty_time = Duration(0), Duration(0), Duration(0)
            self.report = 5 * ' '
            self.release = 5 * ' '
        self.duty_type = 'regular'
        self.event_names = FormattedList([''])
        self.night_time = Duration(0)
        self.xduty_time = Duration(0)
        self.xblock = Duration(0)
        self.maxirre = Duration(0)
        self.pending_rest = Duration(0)
        self.xturn = Duration(0)

    def from_credits(self, block, dh, night_time, xduty_time, xblock, maxirre):
        credit_row = CreditRow('', 'Totals', ' ', None, None)
        credit_row.block = block
        credit_row.dh = dh
        credit_row.night_time = night_time
        credit_row.xduty_time = xduty_time
        credit_row.xblock = xblock
        credit_row.maxirre = maxirre
        return credit_row

    def calculate_totals(self):
        credits_array = self.as_list()
        formatted_totals = TotalsRow(credits_array)
        return formatted_totals

    def __add__(self, other):
        this_list = self.as_list()
        other_list = other.as_list()
        lists_of_lists = [this_list, other_list]
        return self.from_credits(*[sum(x) for x in zip(*lists_of_lists)])

    def as_list(self):
        return [self.duty_time, self.block, self.dh, self.night_time,
                self.xblock, self.xduty_time, self.maxirre, self.pending_rest, self.xturn]

    def __str__(self):
        """Use the class variable template"""
        st_section = CreditRow.string_section_template.format(self)
        nu_section = CreditRow.numeric_section_template.format(self)
        return st_section + nu_section


class CreditTable(object):
    """Adds al credit_rows to a single table"""

    def __init__(self):
        """Start up a List"""
        self.credit_rows = []
        self._totals = None

    def append(self, credit_holder):
        """appends a row to the current table"""
        if isinstance(credit_holder, CreditRow):
            self.credit_rows.append(credit_holder)
        else:
            self.credit_rows.extend(credit_holder.credit_rows)

    def calculate_totals(self):
        credits_array = np.array([row.as_list() for row in self.credit_rows])
        formatted_totals = TotalsRow(credits_array.sum(axis=0))
        self._totals = formatted_totals
        return self._totals

    def __getitem__(self, item):
        return self.credit_rows[item]

    def payable(self):
        block = GARANTIA_HORAS_DE_VUELO_MENSUAL if self._totals[1] < GARANTIA_HORAS_DE_VUELO_MENSUAL \
            else self._totals[1]
        dh = self._totals[2] - JORNADA_ORDINARIA_DH_MENSUAL
        xblock = self._totals[4]
        maxirre = self._totals[6]
        pending_rest = self._totals[7]
        xturn = self._totals[8]

        t_ext_vuelo = block + \
                      dh + \
                      xblock + \
                      maxirre + \
                      pending_rest + \
                      xturn \
                      - JORNADA_ORDINARIA_VUELO_MENSUAL
        t_ext_servicio = self._totals[5]
        t_ext_nocturno = self._totals[3]

        return """
        t_ext_vuelo:    {:2}
        t_ext_servicio: {:2}
        t_ext_nocturno: {:2}
        maxirre: {:2}
        """.format(t_ext_vuelo, t_ext_servicio, t_ext_nocturno, maxirre)

    def __str__(self):
        output = ''
        for creditRow in self.credit_rows:
            output += str(creditRow) + "\n"
        return output.rstrip()


class TotalsRow(list):
    def __str__(self):
        """Use the class variable template"""
        string_section = '   TOTALES                                                                           '
        numeric_section = ''
        for element in self:
            numeric_section = numeric_section + '{:3}'.format(element) + ' '

        return string_section + numeric_section


class FormattedList(list):
    """List containing all cities traveled chronologically in a given Duty Day"""

    def __str__(self):
        formatted = '/'.join(self)
        if formatted[0] == '/':
            return formatted[1:]
        else:
            return formatted


class CreditsDict(dict):
    """I need to add str representation and return a part of key-values as a list"""
    def __str__(self):
        """Use the class variable template"""
        st_section = string_section_template.format(**self)
        nu_section = numeric_section_template.format(**self)
        return st_section + nu_section
