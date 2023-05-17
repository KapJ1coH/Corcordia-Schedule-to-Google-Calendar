import CourseExtraction
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():

    courses = CourseExtraction.main()
    creds = None
    # Test calendar ID
    calendarId = "55776be14ae7a96ee99b52690ac75ade9a0db90653d3f77b128c49e79edb3bad@group.calendar.google.com"
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

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Create a list of events, one event per course
        # delete_all_events(calendarId, service)
        events = []
        for course in courses.values():
            for block in course.schedule.values():
                #create a new event
                event = {
                    'summary': f"{course.course_title} {block.location[-1]}",
                    'location': block.location[0],
                    'description': f'{course.course_subtitle} {course.session}',
                    'start': {
                        'dateTime': datetime.datetime.combine(course.term['Start'], block.start_time).isoformat(),
                        'timeZone': 'America/Montreal',
                    },
                    'end': {
                        'dateTime': datetime.datetime.combine(course.term['Start'], block.end_time).isoformat(),
                        'timeZone': 'America/Montreal',
                    },
                    'recurrence': [
                        f'RRULE:FREQ=WEEKLY;UNTIL={course.term["End"].strftime("%Y%m%dT%H%M%SZ")}'
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
                event = service.events().insert(calendarId=calendarId, body=event).execute()
                print(f'Event created: {event.get("htmlLink")}')








    except HttpError as err:
        print(f"Failed to create event. Error: {err}")


def delete_all_events(calendarId, service):
    event_results = service.events().list(calendarId=calendarId, singleEvents=True).execute()
    events = event_results.get('items', [])
    if not events:
        print('No upcoming events found.')
    else:
        for event in events:
            event_id = event['id']
            try:
                service.events().delete(calendarId=calendarId, eventId=event_id).execute()
            except HttpError as err:
                print(f"Failed to delete event with id {event_id}. Error: {err}")
    exit(0)

if __name__ == '__main__':
    main()