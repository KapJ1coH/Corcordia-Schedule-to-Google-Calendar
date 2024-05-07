import requests
import sys
import argparse


class Class:
    def __init__(self, course_name, lecture, tutorial, lab):
        self.course_name = course_name
        self.lecture = lecture
        self.tutorial = tutorial
        self.lab = lab

    def __str__(self):
        # acccount for no tutorial or lab
        if self.tutorial == None and self.lab == None:
            return f"{self.course_name} - {self.lecture}"
        elif self.tutorial == None:
            return f"{self.course_name} - {self.lecture} - {self.lab}"
        elif self.lab == None:
            return f"{self.course_name} - {self.lecture} - {self.tutorial}"
        else:
            return f"{self.course_name} - {self.lecture} - {self.tutorial} - {self.lab}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduler")

    parser.add_argument(
        "-a", "--add", help="Enable adding classes", action="store_true"
    )
    parser.add_argument("-n", "--name", help="Course name")
    parser.add_argument("-l", help="Lecture section")
    parser.add_argument("-t", help="Tutorial section")
    parser.add_argument("-lb", help="Lab section")

    parser.add_argument("-r", "--remove", help="Remove courses from the schedule")
    parser.add_argument("--list", help="List all courses in the schedule")
    parser.add_argument("-c", "--clear", help="Clear the schedule")

    args = parser.parse_args()

    if args.add:
        print("Adding a course to the schedule:")
        new_class = Class(args.name, args.l, args.t, args.lb)

        print(new_class)
