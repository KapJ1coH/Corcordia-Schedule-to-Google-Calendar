from bs4 import BeautifulSoup
import requests
import datetime


def get_calendar_page(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def scrape_academic_calendar():
    url = "https://www.concordia.ca/students/undergraduate/undergraduate-academic-dates.html"
    soup = get_calendar_page(url)

    dates = list(extract_dates(soup))
    dates = list(clean_dates(dates))
    return dates


def extract_dates(soup):
    for section in soup.findAll("div", class_="c-list-featured-events section"):
        for date in section.findAll("li"):
            if "closed" in date.text:
                day_month = date.text.strip().split("\n")[0]
                year = section.find_previous_sibling(
                    "div", class_="c-wysiwyg wysiwyg section"
                )
                yield f"{day_month} {year.text.strip().split()[-1]}"


def clean_dates(dates):
    """
    Clean the dates to be in the format of
    :param dates: "Mon, Oct. 9 2017"
    :return: datetime.datetime object
    """
    for date in dates:
        if "." in date:
            date = date.replace(".", "")
        try:
            date_return = datetime.datetime.strptime(date, "%a, %b %d %Y")
        except ValueError:
            try:
                date_return = datetime.datetime.strptime(date, "%a, %B %d %Y")
            except ValueError:
                print(f"Failed to parse date, {date}")
            else:
                yield date_return
        else:
            yield date_return


if __name__ == "__main__":
    scrape_academic_calendar()
