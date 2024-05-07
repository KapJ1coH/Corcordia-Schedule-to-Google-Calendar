# Driver file to run the program
from datetime import datetime

# TODO: Add a way to modify the calendar according to
#  the university's academic calendar
import GcalApiIntegration
import CourseScheduleParser


def main():
    delete_or_not()

    filename = "summer_schedule_list_view.html"
    with_modifications = True
    courses = CourseScheduleParser.parse_course_cart(
        with_modifications=with_modifications, filename=filename
    )
    status = GcalApiIntegration.main(courses)
    print(status)


def delete_or_not():
    print("Delete anything? (y/n)")
    delete_choice = input()
    if delete_choice == "n":
        return None

    print("From the start or a specific date? (s/d)")
    date_choice = input()
    if date_choice == "d":
        date = None
        delete_from_date(date)
    elif date_choice == "s":
        GcalApiIntegration.delete_all_events()
        exit(0)
    else:
        print("Invalid choice, exiting...")
        exit(1)


def delete_from_date(date):
    flag = 0
    while flag != 1:
        print("Enter the date in the format of YYYY-MM-DD")
        date = input()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Incorrect date format, should be YYYY-MM-DD")
        else:
            flag = 1
    GcalApiIntegration.delete_all_events(date)
    exit(0)


if __name__ == "__main__":
    main()
