import datetime
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


class TimeBlock:
    def __init__(self, course_title, block_type, location, instructor, start_date=None, days="", start_time="",
                 end_time=""):
        self.course_title = course_title
        self.block_type = block_type
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.instructor = instructor
        self.start_date = start_date

    def add_time_info(self, info, start_date):
        # info format is 'Tue, 08:15 - 10:00'
        day = info.split(",")[0]
        time = info.split(",")[1].split(" - ")
        if self.days == "":
            self.start_date = self.next_weekday(start_date, day)
            self.days = day
            self.start_time = datetime.datetime.strptime(time[0].strip(), "%H:%M").time()
            self.end_time = datetime.datetime.strptime(time[1].strip(), "%H:%M").time()
        else:
            self.days += "," + day
            self.start_date = self.next_weekday(start_date, day)


    def next_weekday(self, start_date, day):
        match day:
            case "Mon":
                return start_date + relativedelta(weekday=MO(1))
            case "Tue":
                return start_date + relativedelta(weekday=TU(1))
            case "Wed":
                return start_date + relativedelta(weekday=WE(1))
            case "Thu":
                return start_date + relativedelta(weekday=TH(1))
            case "Fri":
                return start_date + relativedelta(weekday=FR(1))
            case "Sat":
                return start_date + relativedelta(weekday=SA(1))
            case "Sun":
                return start_date + relativedelta(weekday=SU(1))
            case _:
                return start_date


class Course:
    def __init__(self, course_title, course_subtitle, session, term, instructor, units, schedule):
        self.course_title = course_title
        self.course_subtitle = course_subtitle
        self.session = session
        self.term = term
        self.instructor = instructor
        self.units = units
        self.schedule = schedule

    def add_time_block(self, time_block):
        self.schedule.append(time_block)

    def __str__(self):
        return f"{self.course_title} {self.course_subtitle} {self.session} {self.term} {self.instructor} {self.units} {self.schedule}"


def extract_courses(soup):
    courses = {}
    # Extract course info from the list of courses besides the calendar
    for course_box in soup.find_all('div', class_='course_box block_animation show_extras be0'):
        course = extract_course_info_from_list(course_box)
        courses[course.course_title] = course

    # Extract course info from the calendar
    # for time_block in soup.find_all('div', class_='time_block'):
    #     course_pattern = r"([A-Za-z]+)(\s*\d+)([A-Za-z]+)"
    #     course_info = time_block.text[1:]
    #     print(course_info)
    #     match = re.match(course_pattern, course_info)
    #     if match:
    #         crs_abbreviation, crs_number, block_type = match.groups()
    #         course_title = f"{crs_abbreviation}{crs_number}"
    #     else:
    #         print("No match found")
    #     print(course_title, block_type)
    #     course = courses[course_title]
    #
    #     style = time_block['style']
    #     top = float(style.split(";")[0].split(":")[1].strip("px"))
    #     height =

    return courses


def extract_course_info_from_list(course_box):
    course_title = course_box.find('h4', class_='course_title').text.strip()
    course_subtitle = course_box.find('div', title="Instructor(s)").text.strip()
    session_label = course_box.find('div', class_='session_label').text.strip()
    term_label = course_box.find('span', class_='term_label').next_sibling.strip()
    instructor = course_box.find('div', title='Instructor(s)').text.strip()
    units = course_box.find('div', class_='credits_block').text.strip()
    table = course_box.find('table', class_='inner_legend_table')

    # Splits into the start and end dates
    term_temp = term_label.split(" - ")
    term = {}
    current_year = datetime.datetime.now().year
    term['Start'] = datetime.datetime.strptime(term_temp[0], "%b %d")
    term['Start'] = term['Start'].replace(year=current_year)
    term['End'] = datetime.datetime.strptime(term_temp[1], "%b %d")
    term['End'] = term['End'].replace(year=current_year)

    print(term['Start'], term['End'])

    schedule = {}
    for row in table.find_all('tr'):
        if row.find('td', class_='notes'):
            continue
        block_type = row.find('strong', class_='type_block').text.strip()
        location = location_clean(row).split(" Rm ")
        if len(location) > 1:
            location[-1] = "Room " + location[-1]

        block = TimeBlock(course_title=course_title, block_type=block_type, location=location, instructor=instructor)
        # [:3] is to get the abbreviation of the block type only, ex "LEC" instead of "LEC AA"
        schedule[block_type[:3]] = block

    course = Course(course_title, course_subtitle, session_label, term, instructor, units, schedule)

    return course


def location_clean(row):
    location = row.find('span', class_='location_block').text.split("-")
    if len(location) > 1:
        return location[-1].strip()
    else:
        return ""
    pass


def read_html(name):
    with open(name, 'r') as f:
        return f.read()


def separate_course_info(text):
    # separate SOEN 287LEC into SOEN 287 and LEC
    course_pattern = r"([A-Za-z]+)(\s*\d+)([A-Za-z]+)"
    match = re.match(course_pattern, text)
    if match:
        crs_abbreviation, crs_number, block_type = match.groups()
        course_title = f"{crs_abbreviation}{crs_number}"
        return course_title, block_type
    else:
        return None, None


def extract_calendar(soup, courses):
    table = soup.find('table', class_='class-schedule__calendar')
    for hour in table.find_all('tr'):
        for day in hour.find_all('td'):
            course_info = day.find('span', class_='class-label')
            if course_info:
                course_title, block_type = separate_course_info(course_info.text)
                info = day.find('div', class_='class-info')
                # split time by <br> tag
                info = info.get_text(separator='<br>').split('<br>')
                # leave only time
                info = info[1]
                courses[course_title].schedule[block_type]\
                    .add_time_info(info, courses[course_title].term['Start'])

    print("breakpoint")
    return courses


def main():
    crs_list = read_html('summer_1.html')
    soup = BeautifulSoup(crs_list, 'html.parser')
    courses = extract_courses(soup)
    # Extract times from the calendar
    summer = True
    if summer:
        summer_1 = read_html('summer_1_calendar.html')
        soup = BeautifulSoup(summer_1, 'html.parser')
        courses = extract_calendar(soup, courses)
        summer_2 = read_html('summer_2_calendar.html')
        soup = BeautifulSoup(summer_2, 'html.parser')
        courses = extract_calendar(soup, courses)
    else:
        term = read_html('calendar.html')
        soup = BeautifulSoup(term, 'html.parser')
        courses = extract_calendar(soup, courses)

    return courses


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
