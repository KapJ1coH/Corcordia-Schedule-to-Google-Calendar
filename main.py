import re

from bs4 import BeautifulSoup


LOCATION = {
    "Hall Building" : "1455 de Maisonneuve Boulevard West",
    "Learning square" : "1535 de Maisonneuve Boulevard West",
    "John Molson Building" : "1450 Guy Street",
    "EV Building" : "1515 Sainte-Catherine Street West",
    "Faubourg Building" : "1250 Guy Street",
    "Grey Nuns Building" : "1190 Guy Street",
    "Guy-Metro Building" : "1616 Sainte-Catherine Street West",
    "J.W. McConnell Building" : "1400 De Maisonneuve Boulevard West",
    "LB Building" : "1400 De Maisonneuve Boulevard West",
    "MB Building" : "1450 Guy Street",
    "SP Building" : "2149 Mackay Street",
    "VA Building" : "1395 René-Lévesque Boulevard West",
    "Webster Library" : "1400 De Maisonneuve Boulevard West",

}

class TimeBlock:
    def __init__(self, course_title, block_type,location, instructor, days = "", start_time = "", end_time = ""):
        self.course_title = course_title
        self.block_type = block_type
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.instructor = instructor

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
        print(course)

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

    schedule = []
    for row in table.find_all('tr'):
        if row.find('td', class_='notes'):
            continue
        block_type = row.find('strong', class_='type_block').text.strip()
        location = location_clean(row).split(" Rm ")
        if len(location) > 1:
            location[-1] = "Room " + location[-1]
        block = TimeBlock(course_title=course_title, block_type=block_type, location=location, instructor=instructor)
        schedule.append(block)

    course = Course(course_title, course_subtitle, session_label, term_label, instructor, units, schedule)

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


def extract_calendar(soup, course):
    pass


def main():

    crs_list = read_html('summer_1.html')
    soup = BeautifulSoup(crs_list, 'html.parser')
    course = extract_courses(soup)
    # Extract times from the calendar
    summer = True
    if summer:
        summer_1 = read_html('summer_1_calendar.html')
        soup = BeautifulSoup(summer_1, 'html.parser')
        course = extract_calendar(soup, course)
        summer_2 = read_html('summer_2_calendar.html')
        soup = BeautifulSoup(summer_2, 'html.parser')
        course = extract_calendar(soup, course)
    else:
        term = read_html('calendar.html')
        soup = BeautifulSoup(term, 'html.parser')
        course = extract_calendar(soup, course)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
