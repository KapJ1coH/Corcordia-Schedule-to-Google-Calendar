import requests
from IPython.display import display
from tabulate import tabulate
import re
import sys
import argparse
import pandas as pd


class Class:
    def __init__(self, course_name, lecture, tutorial, lab, term):
        self.course_name = course_name
        self.lecture = lecture
        self.tutorial = tutorial
        self.lab = lab
        self.term = term

    def __str__(self):
        # acccount for no tutorial or lab
        components = [self.course_name, self.lecture, self.term]
        if self.tutorial:
            components.append(self.tutorial)
        if self.lab:
            components.append(self.lab)
        return " - ".join(components).upper()


def add_course_args(parser):
    parser.add_argument(
        "--term", help="Term and year (e.g. Winter 2025)", nargs="+", required=True
    )
    parser.add_argument(
        "-n", "--name", action="append", help="Course name", required=True
    )
    parser.add_argument(
        "-l", "--lecture", action="append", help="Lecture section", required=True
    )
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

            term = " ".join(args.term) if len(args.term) > 1 else args.term[0]

            if re.match(r"[a-zA-Z]{4}\d{3}", name) is None:
                print("Invalid lecture section for course {}".format(name))
                sys.exit(1)

            courses.append(Class(name, lecture, tutorial, lab, term))
    return courses


def process_csv(courses):
    path = "CU_SR_OPEN_DATA_SCHED.csv"
    df = pd.read_csv(path, encoding="utf-16")
    # print(df.head())

    for course in courses:
        subject_df = df["Subject"] == course.course_name[:4]
        catalog_df = df["Catalog Nbr"] == course.course_name[4:]
        term_df = df["Term Descr"] == course.term
        section_df = df["Section"] == course.lecture if course.lecture else True

        tutorial_df = df["Section"] == course.tutorial
        lab_df = df["Section"] == course.lab

        lecture_conditions = subject_df & catalog_df & term_df & section_df
        tutorial_conditions = subject_df & catalog_df & term_df & tutorial_df
        lab_conditions = subject_df & catalog_df & term_df & lab_df

        # print(tabulate(filtered_df, headers="keys", tablefmt="psql"))
        filtered_df = df[lecture_conditions | tutorial_conditions | lab_conditions]

        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print("-" * 100)
            print(filtered_df)
            print("-" * 100)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scheduler")
    add_course_args(parser)

    args = parser.parse_args()

    courses = process_courses(args)
    database = process_csv(courses)

keys = [
    "Course ID",
    "Term Code",
    "Term Descr",
    "Session",
    "Subject",
    "Catalog Nbr",
    "Section",
    "Component Code",
    "Component Descr",
    "Class Nbr",
    "Class Association",
    "Course Title",
    "Topic ID",
    "Topic Descr",
    "Combined Section ID",
    "Class Status",
    "Location Code",
    "Location Descr",
    "Instruction Mode code",
    "Instruction Mode Descr",
    "Meeting Pattern Nbr",
    "Room Code",
    "Building Code",
    "Room",
    "Class Start Time",
    "Class End Time",
    "Mon",
    "Tues",
    "Wed",
    "Thurs",
    "Fri",
    "Sat",
    "Sun",
    "Start Date (DD/MM/YYYY)",
    "End Date (DD/MM/YYYY)",
    "Career",
    "Dept. Code",
    "Dept. Descr",
    "Faculty Code",
    "Faculty Descr",
    "Enrollment Capacity",
    "Current Enrollment",
    "Waitlist Capacity",
    "Current Waitlist Total",
    "Has some/all seats reserved?",
]


crs = [
    "032004",
    "2244",
    "Winter 2025",
    "13W",
    "SOEN",
    "287",
    "W WC",
    "TUT",
    "Tutorial",
    "4657",
    "3",
    "WEB PROGRAMMING",
    "",
    "",
    "",
    "Active",
    "SGW",
    "Sir George Williams Campus",
    "P",
    "In Person",
    "1",
    "MB2.445",
    "MB",
    "2.445",
    "10.15.00",
    "11.55.00",
    "N",
    "N",
    "N",
    "N",
    "Y",
    "N",
    "N",
    "13/01/2025",
    "12/04/2025",
    "Undergraduate",
    "COMPSOEN",
    "Computer Science & Software Engineering",
    "ENCS",
    "Gina Cody School of Engineering & Computer Science",
    "30",
    "1",
    "3",
    "3",
    "",
]
