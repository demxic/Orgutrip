from datetime import datetime, timedelta
from data.timezones import citiesDic, asianCities
from model.scheduleClasses import Itinerary


class FinalItinAdapter(object):
    """Given string parameters, this adapter will return a dictionary containing the corresponding
    parameters turned into objects, thus creating Itinerary objects from strings
    in any given timezone."""

    def __init__(self, airport_where_time = None):
        '''
        airport_where_time asks for the 3-letter airport code of the timeZone, defaults to None.
        A None value, indicates local times
        '''
        self.dataTZ = citiesDic[airport_where_time].timezone if airport_where_time else None

    def convert(self, date, begin, end, endDay = None, origin = None, destination = None):
        '''date should have a %d%b%y (13FEB2015) format or be a datetime object
        begin and end should have a %H%M (2345) format
        origin and destination are three-letter airport codes'''

        if not self.dataTZ:
            self.localTimeZone(date, origin, begin, destination, end)
        else:
            begin, end = self.givenTimeZone(date, begin, end, endDay)

        return Itinerary(begin, end)

    def givenTimeZone(self, dated, begin, end, endDay):
        '''Generate begin and end datetime objects unaware'''

        formating = '%H%M'
        beginString = datetime.strptime(begin, formating).time()
        begin = datetime.combine(dated, beginString)
        endString = datetime.strptime(end, formating).time()
        end = datetime.combine(dated, endString)

        if end < begin:
            end += timedelta(days = 1)
        if endDay:
            end.replace(day = int(endDay))

        begin = self.dataTZ.localize(begin)
        end = self.dataTZ.localize(end)

        return begin, end
#         if isinstance(date, datetime.date):
#             date = date.strftime('%d%b%Y')
#
#         formating = '%d%b%Y%H%M'
#         date_string = date + begin
#         begin = datetime.datetime.strptime(date_string, formating)
#         date_string = date + end
#         end = datetime.datetime.strptime(date_string, formating)
#
#         if end < begin:
#             end += datetime.timedelta(days = 1)
#         if endDay:
#             end.replace(day = int(endDay))
#
#         begin = self.dataTZ.localize(begin)
#         end = self.dataTZ.localize(end)
#
#         return begin, end

    def localTimeZone(self, date, origin, begin, destination, end):
        pass
#         '''Generate begin and end datetime objects unaware'''
#
#         formating = '%d%b%Y%H%M'
#         date_string = date + begin
#         begin = datetime.datetime.strptime(date_string, formating)
#         date_string = date + end
#         end = datetime.datetime.strptime(date_string, formating)
#
#         if end < begin and not self.origin in asianCities:  # Adjust date for a next day eta
#             end += datetime.timedelta(days = 1)
#
#         originTimeZone = citiesDic[self.origin].timezone
#         destinationTimeZone = citiesDic[self.destination].timezone
#
#         ''' Generate aware datetimes in local times'''
#         begin = originTimeZone.localize(begin)
#         end = destinationTimeZone.localize(end)
#
#         return begin, end


    def asDict(self):
        return {'name':self.name, 'origin':self.origin, 'destination':self.destination,
                'begin':self.begin, 'end':self.end}



class LocalItinAdapter(object):
    '''Given string parameters, this adapter will return a dictionary containing the appropriate
    parameters but now turned into objects. This allows to create Itinerary objects from strings
    in local timezone. Returned dictionary values in Zulu'''

    def __init__(self, date, name, origin, begin, destination, end):
        '''
        Date should have a %d%b%y (13FEB2015) format
        begin and end should have a %H%M (2345) format
        '''
        self.name = name
        self.origin = origin
        self.destination = destination
        self.begin, self.end = self.convert(date, begin, end)

    def convert(self, date, begin, end):
        '''Generate begin and end datetime objects unaware'''

        formating = '%d%b%Y%H%M'
        date_string = date + begin
        begin = datetime.datetime.strptime(date_string, formating)
        date_string = date + end
        end = datetime.datetime.strptime(date_string, formating)

        if end < begin and not self.origin in asianCities:  # Adjust date for a next day eta
            end += datetime.timedelta(days = 1)

        originTimeZone = citiesDic[self.origin].timezone
        destinationTimeZone = citiesDic[self.destination].timezone

        ''' Generate aware datetimes in local times'''
        begin = originTimeZone.localize(begin)
        end = destinationTimeZone.localize(end)

        return begin, end

    def asDict(self):
        return {'name':self.name, 'origin':self.origin, 'destination':self.destination,
                'begin':self.begin, 'end':self.end}


class TimeZoneItinAdapter(object):
    '''Given string parameters, this adapter will return a dictionary containing the appropriate
    parameters but now turned into objects. This allows to create Itinerary objects from strings
    in any given timezone.'''

    def __init__(self, date, name, origin, begin, destination, end, displayZone = 'MEX'):
        '''
        Date should have a %d%b%y (13FEB2015) format
        begin and end should have a %H%M (2345) format
        '''
        self.displayZone = displayZone
        self.name = name
        self.origin = origin
        self.destination = destination
        self.begin, self.end = self.convert(date, begin, end)

    def convert(self, date, begin, end):
        '''Generate begin and end datetime objects unaware'''

        formating = '%d%b%Y%H%M'
        date_string = date + begin
        begin = datetime.datetime.strptime(date_string, formating)
        date_string = date + end
        end = datetime.datetime.strptime(date_string, formating)

        if end < begin and not self.origin in asianCities:  # Adjust date for a next day eta
            end += datetime.timedelta(days = 1)

        displayTimeZone = citiesDic[self.displayZone].timezone

        ''' Generate aware datetimes in the given display Time Zone'''
        begin = displayTimeZone.localize(begin)
        end = displayTimeZone.localize(end)

        return begin, end

    def asDict(self):
        return {'name':self.name, 'origin':self.origin, 'destination':self.destination,
                'begin':self.begin, 'end':self.end}


