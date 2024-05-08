import requests
import re
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
        components = [self.course_name, self.lecture]
        if self.tutorial:
            components.append(self.tutorial)
        if self.lab:
            components.append(self.lab)
        return " ".join(components).upper()


def add_course_args(parser):
    parser.add_argument("-n", "--name", action="append", help="Course name")
    parser.add_argument("-l", "--lecture", action="append", help="Lecture section")
    parser.add_argument(
        "-t", "--tutorial", action="append", help="Tutorial section", default=[]
    )
    parser.add_argument("-lb", "--lab", action="append", help="Lab section", default=[])


def process_courses(args):
    courses = []
    if args.name:
        for i, name in enumerate(args.name):
            if i >= len(args.lecture):
                print("Course {} has no lecture section".format(name))
                sys.exit(1)

            lecture = args.lecture[i]
            tutorial = args.tutorial[i] if i < len(args.tutorial) else None
            lab = args.lab[i] if i < len(args.lab) else None

            if re.match(r"[a-zA-Z]{4}\d{3}", name) is None:
                print("Invalid lecture section for course {}".format(name))
                sys.exit(1)

            courses.append(Class(name, lecture, tutorial, lab))
    return courses


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduler")
    add_course_args(parser)

    args = parser.parse_args()

    courses = process_courses(args)
