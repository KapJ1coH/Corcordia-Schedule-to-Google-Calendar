import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']

def main(courses):
    # TODO: Clean up this function
    calendarId = "55776be14ae7a96ee99b52690ac75ade9a0db90653d3f77b128c49e79edb3bad@group.calendar.google.com"

    creds = create_creds(calendarId)
    service = build('calendar', 'v3', credentials=creds)

    # delete_all_events(calendarId, service)
    return populate_events(calendarId, courses, creds, service)


def populate_events(calendarId, courses, creds, service):
    try:

        # Create a list of events, one event per course

        events = []
        for course in courses.values():
            for event in course.events:
                # create a new event
                event = create_event(course, event)
                event = service.events().insert(calendarId=calendarId, body=event).execute()
                print(f'Event created: {event.get("htmlLink")}')

    except HttpError as err:
        return f"Failed to create event. Error: {err}"
    except AttributeError as err:
        return f"Failed to create event. Error: {err}"
    return "Success"


def create_creds(calendarId):
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def create_event(course, event):
    event = {
        'summary': f"{course.title} {event.component} {event.room}",
        'location': f"{event.address}",
        'description': f'Course name: {course.subtitle}\n'
                       f'Credits: {course.credits}\n'
                       f'Instructor: {event.instructor}\n'
                       f'Class number: {event.class_number}\n'
                       f'Component: {event.component}\n'
                       f'Section: {event.section}',

        'start': {
            'dateTime': datetime.datetime.combine(event.start_date, event.start_time).isoformat(),
            'timeZone': 'America/Montreal',
        },
        'end': {
            'dateTime': datetime.datetime.combine(event.start_date, event.end_time).isoformat(),
            'timeZone': 'America/Montreal',
        },
        'recurrence': [
            f'RRULE:FREQ=WEEKLY;BYDAY={",".join(event.days)};UNTIL={event.end_date.strftime("%Y%m%dT%H%M%SZ")}'
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 15},
                {'method': 'popup', 'minutes': 30},
                {'method': 'popup', 'minutes': 120},
            ],
        },
    }
    return event


def delete_all_events(calendarId, service, start_date=None, specific_date=None):
    event_results = service.events().list(calendarId=calendarId, singleEvents=True).execute()
    if events := event_results.get('items', []):
        for event in events:
            if (
                start_date
                and event['start']['dateTime'] > start_date
                and not specific_date
            ):
                event_id = event['id']
                delete_one_event(calendarId, event_id, service)
            elif (
                specific_date
                and event['start']['dateTime'] == specific_date
            ):
                event_id = event['id']
                delete_one_event(calendarId, event_id, service)
    else:
        print('No upcoming events found.')


def delete_one_event(calendarId, event_id, service):
    try:
        service.events().delete(calendarId=calendarId, eventId=event_id).execute()
    except HttpError as err:
        print(f"Failed to delete event with id {event_id}. Error: {err}")


