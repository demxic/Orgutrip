def compensation_dict(monthly_salary, assistance_bonus=469):
    comp_dict = dict()
    comp_dict['monthly_salary'] = monthly_salary
    comp_dict['daily_salary'] = monthly_salary / 30
    comp_dict['holiday'] = comp_dict['daily_salary'] * 2
    comp_dict['restday'] = comp_dict['daily_salary'] * 2
    comp_dict['sunday_premium'] = comp_dict['daily_salary'] * 0.25
    comp_dict['duty_overtime'] = comp_dict['monthly_salary'] / 180 * 2
    comp_dict['block_overtime'] = comp_dict['monthly_salary'] / 65 * 2
    comp_dict['unsurpassable'] = comp_dict['block_overtime'] * 2
    comp_dict['vacation_bonus'] = comp_dict['daily_salary'] * 15
    comp_dict['assistance_bonus'] = assistance_bonus
    comp_dict['night_premium'] = 0.002 * comp_dict['monthly_salary']
    return comp_dict


class PayCheck(object):
    def __init__(self, compensations):
        """ Calculates all pay_items within a paycheck for the given compensation factors """
        self.compensation_dict = compensations
        self.salary = None
        self.holiday = None
        self.rest_day = None
        self.sunday_premium = None
        self.duty_overtime = None
        self.block_overtime = None
        self.unsurpassable = None
        self.night_premium = None
        self.vacation_bonus = None
        self.assistance_bonus = None

    def calculate(self, credits):
        """Calculate all Paycheck items from their corresponding credit item"""
        self.salary = self.compensation_dict['daily_salary'] * 14
        self.holiday = self.compensation_dict['daily_salary'] * 0
        self.rest_day = self.compensation_dict['daily_salary'] * credits['day7']
        self.sunday_premium = self.compensation_dict['sunday_premium'] * credits['sunday']
        self.duty_overtime = self.compensation_dict['duty_overtime'] * credits['xduty']
        self.block_overtime = self.compensation_dict['block_overtime'] * credits['xblock']
        self.unsurpassable = self.compensation_dict['unsurpassable'] * credits['maxirre']
        self.night_premium = self.compensation_dict['night_premium'] * credits['night']
        self.vacation_bonus = self.compensation_dict['vacation_bonus'] * 0
        self.assistance_bonus = self.compensation_dict['assistance_bonus']
        self.total = self.salary + self.duty_overtime + self.block_overtime + self.unsurpassable + \
                     self.night_premium + self.assistance_bonus

    def to_list(self):
        return [self.salary, self.holiday, self.restday, self.sunday_premium, self.duty_overtime,
                self.block_overtime, self.unsurpassable, self.night_premium, self.vacation_bonus,
                self.assistance_bonus]

    def __str__(self):
        template = """
        SUELDO:               ${0: >9.2f}
        PRIMA DOMINICAL:      ${1: >9.2f}
        T EXT SERVICIO:       ${2: >9.2f}
        T EXT VUELO:          ${3: >9.2f}
        MAX IRREBASABLE:      ${4: >9.2f}
        T EXT NOCTURNO:       ${5: >9.2f}
        PREMIO ASISTENCIA:    ${6: >9.2f}
        ---------------------------------------
        TOTAL                 ${7: >9.2f}
        """
        return template.format(self.salary, self.sunday_premium, self.duty_overtime,
                               self.block_overtime, self.unsurpassable,
                               self.night_premium, self.assistance_bonus,
                               self.total)
