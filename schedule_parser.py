from datetime import datetime
import re
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

from bs4 import BeautifulSoup

LOCATION = {
    "Hall Building": "1455 de Maisonneuve Boulevard West",
    "Learning square": "1535 de Maisonneuve Boulevard West",
    "John Molson Building": "1450 Guy Street",
    "EV Building": "1515 Sainte-Catherine Street West",
    "Faubourg Building": "1250 Guy Street",
    "Grey Nuns Building": "1190 Guy Street",
    "Guy-Metro Building": "1616 Sainte-Catherine Street West",
    "J.W. McConnell Building": "1400 De Maisonneuve Boulevard West",
    "LB Building": "1400 De Maisonneuve Boulevard West",
    "MB Building": "1450 Guy Street",
    "SP Building": "2149 Mackay Street",
    "VA Building": "1395 René-Lévesque Boulevard West",
    "Webster Library": "1400 De Maisonneuve Boulevard West",

}

"""
New format:
 - Grab all the course info from the course cart
 - Grab university closed dates from the academic calendar

 - Make the program event based
    - For each course, create a list of events
    - Each event should have a start date, end date, start time, end time, location, instructor and days of the week
    - Each event should have a recurrence rule
    - Allow for multiple days per block
    - Represent days in this format: 'MO,TU,WE,TH,FR'
    - Add a recurrence rule for each

- Course, Event are both objects
- Course has a list of events and general course info
- Course contains start and end date, course instructor, course title, course subtitle, course number, course section, course session, course credits
- Event contains start and end time, location, days of the week, recurrence rule
    - Location should be a tuple of (building, room)
    - Building should be a string with the full address
    - No location --> Empty string

- Enable event deletion and modification
    - Delete all events for a course
    - Delete all events for a course on a specific day
    - Modify based on data stored in a file.

"""

"""
This module is responsible for parsing the schedule from the course cart.

"""


class TimeBlock:
    """
    Represents a single event in a course.
    """

    def __init__(self, start_date, end_date, start_time, end_time, days, building, room, instructor):
        """
        :type start_date: datetime        :type end_date:
        :param start_date: Class start date
        :param end_date: Class end date
        :param start_time: Class start time
        :param end_time: Class end time
        :param days: Days of the week the class is on
        :param building: Building the class is in
        :param room: Room the class is in
        :param instructor: Instructor of the class
        """
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.days = days
        self.building = building
        self.room = room
        self.instructor = instructor

    def next_weekday(self, start_date, day):
        match day:
            case "Mo":
                return start_date + relativedelta(weekday=MO(1))
            case "Tu":
                return start_date + relativedelta(weekday=TU(1))
            case "We":
                return start_date + relativedelta(weekday=WE(1))
            case "Th":
                return start_date + relativedelta(weekday=TH(1))
            case "Fr":
                return start_date + relativedelta(weekday=FR(1))
            case "Sa":
                return start_date + relativedelta(weekday=SA(1))
            case "Su":
                return start_date + relativedelta(weekday=SU(1))
            case _:
                return start_date


class Course:
    """
    This class represents a single course.
    """

    def __init__(self, course_title, course_subtitle, course_number, course_section, course_session, course_credits,
                 events):
        self.course_title = course_title
        self.course_subtitle = course_subtitle
        self.course_number = course_number
        self.course_section = course_section
        self.course_session = course_session
        self.course_credits = course_credits
        self.events = events


def parse_course_cart():
    """
    Goes through the html table, and parses the course cart.
    Each block is one course with all the information.
    :return: List of courses
    """
    courses = {}
    table = extract_table('summer_schedule_list_view.html').find('tbody')

    units_regex = re.compile(r'DERIVED_REGFRM1_UNT_TAKEN$\d+')

    count = 0;

    for i, block in enumerate(table.findChildren('tr', recursive=False)):
        count = go_thru_each_class(block, count, i)
    pass


def go_thru_each_class(block, count, i):
    class_name = block.find('h3', class_="ui-bar").text
    units = block.find('span', id=f'DERIVED_REGFRM1_UNT_TAKEN${i}').text
    for row in block.find('table', id=f"CLASS_MTG_VW$scroll${i}").find('table', class_='ui-table').find(
            'tbody').findAll('tr'):
        """
        Example data extracted:
        3103 CCCG Tutorial MoWe 6:30PM - 8:10PM H 521 SGW JOUMANA DARGHAM 
        03/07/2023 - 10/08/2023
        """
        cls_number = ""
        if not (cls_number := row.find('span', id=f"DERIVED_CLS_DTL_CLASS_NBR${count}")):
            print("No class number found")
            continue
        cls_number = cls_number.text
        cls_section = row.find('a', id=f"MTG_SECTION${count}").text
        # :3 to shorten from Lecture to Lec
        cls_component = row.find('span', id=f"MTG_COMP${count}").text[:3]
        # make it in the proper format
        cls_day_time = row.find('span', id=f"MTG_SCHED${count}").text
        days, start_time, end_time = clean_cls_day_time(cls_day_time)
        cls_room = row.find('span', id=f"MTG_LOC${count}").text
        cls_instructor = row.find('span', id=f"DERIVED_CLS_DTL_SSR_INSTR_LONG${count}").text
        cls_start_end = row.find('span', id=f"MTG_DATES${count}").text
        print(cls_number ,cls_section, cls_component, cls_day_time, cls_room, cls_instructor, cls_start_end)
        count += 1

    return count


def clean_cls_day_time(cls_day_time):
    """
    Transform a string of location/time into a tuple of days and times.
    :param cls_day_time: String. Ex: MoWe 6:30PM - 8:10PM
    :return: String, String, datetime.time, datetime.time. Ex: MO,WE,18:30,20:10
    """
    days, time = cls_day_time.split(' ', 1)
    print(days, time)
    start_time, end_time = time.split(' - ')
    start_time = datetime.strptime(start_time, '%I:%M%p').time()
    end_time = datetime.strptime(end_time, '%I:%M%p').time()
    return days, start_time, end_time

def extract_table(filename):
    html = read_html(filename)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('table', id='ACE_STDNT_ENRL_SSV2$0')


def read_html(name):
    with open(name, 'r') as f:
        return f.read()


if __name__ == '__main__':
    parse_course_cart()
