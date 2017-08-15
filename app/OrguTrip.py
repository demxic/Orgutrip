import sqlite3
import sys
from datetime import datetime, timedelta

import model.creditator as creditator
from model.creditator import Creditator
from model.crewmember import CrewMember
from model.elements import DateTracker
from model.scheduleClasses import Itinerary, Trip, DutyDay, GroundDuty
from rosterReaders.lineCreator import Liner
from rosterReaders.txtroster import RosterReader

# Roles de la Cuija
#rolFile = "C:\\Users\\Xico\\Google Drive\\Sobrecargo\\roles\\Rol-2017-07-P.txt"
# summaryFile = "C:\\Users\\Xico\\Google Drive\\Sobrecargo\\Resumen de horas\\Rol-2017-02-R.txt"

#Mis roles
rolFile = "C:\\Users\\Xico\\Google Drive\\Sobrecargo\\roles\\201707.txt"
summaryFile = "C:\\Users\\Xico\\Google Drive\\Sobrecargo\\Resumen de horas\\2017\\res201707.txt"


class Menu:
    """Display a menu and respond to choices when run"""

    def __init__(self):
        self.line = None
        self.choices = {
            "1": self.read_printed_line,
            "2": self.print_line,
            "3": self.credits,
            "4": self.viaticum,
            "5": self.store,
            "6": self.read_flights_summary,
            "7": self.retrieve_flights_from_database,
            "8": self.print_components,
            "10": self.quit}

    @staticmethod
    def display_menu():
        print('''
        Orgutrip Menu

        1. Carga tu rol mensual.
        2. Imprime en pantalla tu rol.
        3. Calcula los créditos.
        4. Obtener viáticos.
        5. Almacenar tu rol en la base de datos.
        6. Cargar tu resumen de horas mensuales.
        7. Cargar tiempos por itinerario de la base de datos.
        8. Imprimir cada componente
        10. Quit
        ''')

    def run(self):
        """Display the menu and respond to choices"""
        while True:
            self.display_menu()
            choice = input("¿Qué deseas realizar?: ")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))

    def read_printed_line(self):
        """Let's read the roaster from a given .txt file"""
        print("read_printed_line")
        with open(rolFile) as fp:
            rr = RosterReader(fp)
        crew_member = CrewMember(**rr.crew_stats)
        print("crew_member : ", crew_member)
        print("Carry in within month? ", rr.carry_in)
        print("Roster timeZone ", rr.timeZone)
        print("Roster year and month ", rr.year, rr.month)
        dt = DateTracker(rr.year, rr.month, rr.carry_in)
        print("Date Tracker: ", dt)
        print()
        # print("Printing txtroster line by line")
        # print(40*"*")
        # for row in rr.roster_days:
        #     print(row)
        # print(40 * "*")
        print("\nCreating a Liner . . . ")
        liner = Liner(dt, rr.roster_days, 'scheduled')
        liner.build_line()
        self.line = liner.line
        self.line.crewMember = crew_member

    def print_line(self):
        """Let's print out the roaster"""
        print(self.line)

    def credits(self):
        cr = Creditator('SOB', 'SO01', self.line.month)
        print(creditator.line_credits_header)
        for row in self.line.compute_credits(cr):
            print(row)
        print(self.line._credits['template'].format(**self.line._credits))
        print(cr.month_credits(self.line._credits))
        # compensations = compensation_dict(691.02*30)
        # paycheck = PayCheck(compensations, credit_table.totals())
        # paycheck.calculate()
        # print(paycheck)


    def viaticum(self):
        pass

    def store(self):
        print('Storing data ')
        conn = sqlite3.connect('C:\\Users\\Xico\\Dropbox\\PyCharmProjects\\Orgutrip\\data\\flights.db')
        c = conn.cursor()
        for duty_day in self.line.return_duty_days():
            for event in duty_day.events:
                if event.name == 'X' or event.name == 'RZ':
                    pass
                else:
                    print(event)
                    c.execute("INSERT INTO flights (date, number, origin, begin, destination, duration)"
                              "VALUES (?, ?, ?, ?, ?, ?)", (event.begin.date(),
                                                            event.name,
                                                            event.origin,
                                                            event.begin.strftime("%H%M"),
                                                            event.destination,
                                                            event.duration.minutes))
                    conn.commit()

        print('Reading data :')
        for row in c.execute("SELECT * FROM flights"):
            print(row)
        conn.close()

    def read_flights_summary(self):
        """Let's read month's flights summary from a given .txt file"""
        with open(summaryFile) as fp:
            rr = RosterReader(fp)
        print("crew_stats : ", rr.crew_stats)
        print("Carry in within month? ", rr.carry_in)
        print("Roster timeZone ", rr.timeZone)
        print("Roster year and month ", rr.year, rr.month)

        dt = DateTracker(rr.year, rr.month, rr.carry_in)
        print("\ndatetracker for ", dt)

        print("\nCreating a Liner")
        liner = Liner(dt, rr.roster_days, 'actual_itinerary')
        liner.build_line()
        self.line = liner.line

    def retrieve_flights_from_database(self):
        SQL = "SELECT * FROM flights WHERE number = ? AND date = ?"
        conn = sqlite3.connect('C:\\Users\\Xico\\Dropbox\\PyCharmProjects\\Orgutrip\\data\\flights.db')
        c = conn.cursor()
        for duty_day in self.line.return_duty_days():
            events = duty_day.events
            try:
                for flight in duty_day.events:
                    print(50 * '*')
                    print("Flight's actual_itinerary itinerary: ", flight.name)
                    print(flight.actual_itinerary)
                    print()
                    for row in c.execute(SQL, [flight.name, flight.begin.date()]):
                        begin = datetime.strptime(row[0]+row[3], "%Y-%m-%d%H%M")
                        duration = timedelta(minutes = int(row[5]))
                        scheduled_itinerary = Itinerary.from_timedelta(begin, duration)
                        print("Flight's scheduled itinerary: ", flight.name)
                    flight.published_itinerary = scheduled_itinerary
                    print(flight.published_itinerary)
            except:
                    try:
                        for flight in duty_day.events:
                            print(50 * '*')
                            print("Flight's actual_itinerary itinerary: ", flight.name)
                            print(flight.actual_itinerary)
                            print()
                            for row in c.execute(SQL, [flight.name, flight.begin.date()-timedelta(days=-1)]):
                                begin = datetime.strptime(row[0] + row[3], "%Y-%m-%d%H%M")
                                duration = timedelta(minutes=int(row[5]))
                                scheduled_itinerary = Itinerary.from_timedelta(begin, duration)
                                print("Flight's scheduled itinerary: ", flight.name)
                            flight.published_itinerary = scheduled_itinerary
                            print(flight.published_itinerary)
                    except:
                        pass

        conn.close()

    def print_components(self):
        for duty in self.line:
            if isinstance(duty, Trip):
                for duty_day in duty.duty_days:
                    for turn in duty_day.turns:
                        print(turn)

    def quit(self):
        print("adiós")
        sys.exit(0)


if __name__ == '__main__':
    Menu().run()
