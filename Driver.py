# Driver file to run the program

# TODO: Add a way to modify the calendar according to
#  the university's academic calendar
import GcalApiIntegration
import CourseScheduleParser


def main():
    filename = 'summer_schedule_list_view.html'
    with_modifications = True
    courses = schedule_parser.parse_course_cart(
        with_modifications=with_modifications, filename=filename)
    status = gCal.main(courses)
    print(status)


if __name__ == '__main__':
    main()
