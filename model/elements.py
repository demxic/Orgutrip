'''
Created on 24/03/2016

This module holds all auxiliary classes neede to effectively model a
flight app. It includes mainly definitions for Airport, CrewMember,
Equipment, Airline
@author: Xico
'''
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta


class Airport(object):
    '''
    An Airport class holds valuable information to interact with
    the 3-letter code cities defined by iata.
    '''

    def __init__(self, iata, name, shortName, countryCode, countryName,
                 timeZoneRegionName, viatPayScale):
        '''
        Provide all required fields to create an airport.
        '''
        self.iata = iata
        self.name = name
        self.shortName = shortName
        self.countryCode = countryCode
        self.countryName = countryName
        self.tzRegionName = timeZoneRegionName
        self.viatPayScale = viatPayScale

    def __str__(self):
        '''
        Only print as the iata 3-letter code
        '''
        return self.iata + ' ' + self.name + '-' + self.shortName

class Airline(object):
    '''
    Represents an airline for a given flight. As almost all flights
    used will be Aeromexico specific, note the default values.
    '''

    def __init__(self, iata = 'AM', name = 'Aeromexico'):
        '''
        If non given, default to Aeromexico
        '''
        self.iata = iata
        self.name = name

    def __str__(self):
        return self.iata

class CrewMember(object):
    '''
    Holds all related data for a given CrewMember
    '''

    def __init__(self, crewId, name, pos, group, crewType, base,
                 seniority, hireDate = None):
        self.crewId = crewId
        self.name = name
        self.pos = pos
        self.group = group
        self.crewType = crewType
        self.base = base
        self.seniority = seniority
        self.hireDate = hireDate


    def __str__(self):
        return "{0:3s} {1:6s}-{2:12s}".format(
                                              self.pos,
                                              self.crewId,
                                              self.name)

class Equipment(object):
    '''
    Models an Aeromexico equipment
    '''

    def __init__(self, iata, aeromexicoCode, name, minCrewMembers):
        '''
        All arguments
        '''
        self.iata = iata
        self.aeromexicoCode = aeromexicoCode
        self.name = name
        self.minCrewMembers = minCrewMembers


class DateTracker(object):
    """Used to track whenever there is a change in month"""

    def __init__(self, year, month, carry_in=False):
        """

        :type carry_in: boolean
        """
        months = {'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
                 'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12}
        three_letter_month = month[0:3]
        self.year = year
        self.month = months[three_letter_month]
        self.dated = date(self.year, self.month, 1)
        if carry_in:
            self.backwards()
            print("There is a carry in so datetracker now points to: ")
            print(self)

    def backwards(self):
        """Moves one day back in time"""
        self.dated = self.dated + relativedelta(months=-1)

    def replace(self, day):
        """Change self.date's day to given value, resulting date must
           always be forward in time"""
        day = int(day)
        if day < self.dated.day:
            # If condition is met, move one month forward
            self.dated = self.dated.replace(day = day)
            self.dated = self.dated + relativedelta(months=+1)
        else:
            # Still in the same month
            self.dated = self.dated.replace(day = day)

    def __str__(self):
        return "Pointing to {0:%d-%b-%Y}".format(self.dated)

class Dotdict(dict):
    '''Dot notation access to dictionary attributes'''

    def __getattr__(self, key):
        return self[key]
    def __setattr__(self, key, val):
        if key in self.__dict__:
            self.__dict__[key] = val
        else:
            self[key] = val

def neighborhood(iterable):
    iterator = iter(iterable)
    prev = None
    item = next(iterator)  # throws StopIteration if empty.
    for following in iterator:
        yield (prev, item, following)
        prev = item
        item = following
    yield (prev, item, None)
