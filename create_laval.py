from datetime import datetime, date, timedelta
import calendar;
from icalendar import Calendar, Event
from datetime import datetime
from pathlib import Path
from pytz import timezone
import os
import uuid

#Secteur D - Zone14 - Collectes ordures
#https://www.laval.ca/Pages/Fr/Citoyens/calendrier-collectes.aspx

#Lundi : 0
#Mardi : 1
#Mercredi : 2
#Jeudi : 3
#Vendredi : 4
#Samedi : 5
#Dimanche : 6

DAY_OF_RECYCLING = 1;
DAY_OF_ORGANIC = 3;
DAY_OF_GARBAGE = 1;
DAY_OF_ENCOMBRANTS = 0;
MONTHS_OF_WINTER = [1, 2, 3, 12]; #Organic every 2 weeks (starting on the second week)
DAY_OF_CHRISTMAS_TREE = 1;
MAX_NUMBER_OF_DAYS_CHRISTMASS = 2;

BEGINNING_EVENT_HOUR = 7;

YEAR = 2026;

garbage_days = [];
recycling_days = [];
encombrants_days = [];
christmas_tree_days = [];
organic_days = [];


def isChristmassTreeDays (year, month, day):
    if (len(christmas_tree_days) < 2):
        myDate = datetime(year, month, day, BEGINNING_EVENT_HOUR, 0, 0, tzinfo=tz);

        if (myDate.weekday() == DAY_OF_CHRISTMAS_TREE and month == 1):
            #print(str(date) + '-CHRISTMASS DAY');
            christmas_tree_days.append(myDate);


def isGarbageDays (year, month, day):
    myDate = datetime(year, month, day, BEGINNING_EVENT_HOUR, 0, 0, tzinfo=tz);
    if (myDate.weekday() == DAY_OF_GARBAGE):
        #print(str(date) + '-GARBAGE DAY');
        garbage_days.append(myDate);

def isRecyclingDays (year, month, day):
    myDate = datetime(year, month, day, BEGINNING_EVENT_HOUR, 0, 0, tzinfo=tz);
    if (myDate.weekday() == DAY_OF_RECYCLING):
        #print(str(date) + '-RECYCLING DAY');
        recycling_days.append(myDate);

#Encombrants est le lundi de la dernière semaine complète du mois.
#Pour savoir si on est la dernière semaine complète du mois, il faut que le samedi soit plus grand ou égal au nombre de jours du mois - 5
def isEncombrantsDays (year, month, day):
    myDate = datetime(year, month, day, BEGINNING_EVENT_HOUR, 0, 0, tzinfo=tz);
    num_days = calendar.monthrange(year, month)[1]

    if (myDate.weekday() == DAY_OF_ENCOMBRANTS and day >= num_days - 10 and day <= num_days - 4):
        #print(str(date) + '-ENCOMBRANTS DAY');
        encombrants_days.append(myDate);


def isOnTheRightWeek (month: int, week_no: int):
    if (month in MONTHS_OF_WINTER and week_no % 2 == 0): 
        #print('Winter and on the right week')
        return True;

    if (not month in MONTHS_OF_WINTER): 
        #print('Not in winter : ok')
        return True;
    
    #print('Winter, but not in the right week')
    return False;

#TODO : 1 semaine sur 2 seulement
def isOrganicDays (year, month, day, week_no):
    myDate = datetime(year, month, day, BEGINNING_EVENT_HOUR, 0, 0, tzinfo=tz);
    if (myDate.weekday() == DAY_OF_ORGANIC and isOnTheRightWeek(month, week_no)):
        #print('organic week no : ' + str(week_no));
        if (myDate == datetime(year, 12, 25)):
            #print(str(myDate+timedelta(days=5-DAY_OF_ORGANIC)) + '-ORGANIC DAY, but christmas');
            #On doit trouver le samedi alors si c'est Noel
            organic_days.append(myDate+timedelta(days=5-DAY_OF_ORGANIC));
        else: 
            #print(str(date) + '-ORGANIC DAY');
            organic_days.append(myDate);

tz = timezone('America/Montreal');
week_no = 1;

for i in range(12):
    month = i + 1;
    num_days = calendar.monthrange(YEAR, month)[1]
    
    for j in range(num_days):
        day = j + 1;
        date = datetime(YEAR, month, day)
        if (date.weekday() == 0):
            week_no = week_no + 1;

        #On peut tester les dates selon les situations qu'on a besoin.
        isChristmassTreeDays(YEAR, month, day);
        isGarbageDays(YEAR, month, day);
        isRecyclingDays(YEAR, month, day);
        isEncombrantsDays(YEAR, month, day);
        isOrganicDays(YEAR, month, day, week_no);

def writeCalendarICS(cal, name):
    directory = Path.cwd() / 'MyCalendar'
    try:
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder already exists")
    else:
        print("Folder was created")
    
    f = open(os.path.join(directory, name + '.ics'), 'wb')
    f.write(cal.to_ical())
    f.close()


def addEvents(cal, liste, name):
    for oneEvent in liste:
        # Add subcomponents
        event = Event()
        event.add('name', name + " - " + oneEvent.strftime("%Y-%m-%d %H:%M:%S"))
        event.add('description', name + ' collection in laval, Secteur D, Zone 14')
        event.add('Summary', name)
        
        event.add('dtstart', oneEvent)
        event.add('dtend', oneEvent+timedelta(hours=7));
        #TODO : Mieux : UID:2025-01-14-Ottawa-waste-@recollect.net
        event['uid'] = uuid.uuid4()
        cal.add_component(event)
    
    return cal;


def createEvents():
    cal = Calendar()

    # Some properties are required to be compliant
    cal.add('prodid', '-//Laval-garbage-ics-generator_python//')
    cal.add('version', '1.0')

    cal = addEvents(cal, garbage_days, "Garbage");
    cal = addEvents(cal, recycling_days, "Recycling");
    cal = addEvents(cal, encombrants_days, "Encombrants");
    cal = addEvents(cal, christmas_tree_days, "ChristmasTree");
    cal = addEvents(cal, organic_days, "Organic");

    writeCalendarICS(cal, "Laval")

createEvents();