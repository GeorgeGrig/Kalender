import calendar
import locale
import webbrowser
import argparse
from typing import Dict, Iterable
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from jinja2 import Template

def get_next_sunday_date(input_date: date) -> date:
    """
    Returns the date of the next sunday.
    """
    return input_date + timedelta(days=(6 - input_date.weekday()))

def get_previous_monday_date(input_date: date) -> date:
    """
    Returns the date of the previous monday.
    """
    return input_date - timedelta(days=input_date.weekday())

def build_week_page_left(input_date: date) -> Dict:
    """
    Builds the datastructure for the week page.
    """
    # Create page dictionary
    page = {
        "month": get_next_sunday_date(input_date).strftime("%B"),
        "type": "Week-Left",
        "tag": [],
        }
    # Iterate over all days in the week
    for i, day in enumerate(date_iterator(input_date, timedelta(days=1), 3)):
        # Create a nested dict for each day
        page['tag'].append(
            {
                "name": day.strftime("%A"),
                "table-ID": i + 1,
                "datum": day.strftime("%d.%m"),
            }
        )
    # # Append blank "day" for notes to get to an even number on the page
    # page['tag'].append({"name": "Notes", "table-ID": 2, "datum": ""})
    return page

def build_week_page_right(input_date: date) -> Dict:
    """
    Builds the datastructure for the week page.
    """
    # Create page dictionary
    page = {
        "month": get_next_sunday_date(input_date).strftime("%B"),
        "type": "Week-Right",
        "tag": [],
        }
    # Iterate over all days in the week
    for i, day in enumerate(date_iterator(input_date, timedelta(days=1), 4)):
        # Create a nested dict for each day
        if day.strftime("%A") == "Sunday":
           page['tag'].append(
            {
                "name": day.strftime("%A"),
                "table-ID": 3,
                "datum": day.strftime("%d.%m"),
            }
            ) 
        else:
            page['tag'].append(
                {
                    "name": day.strftime("%A"),
                    "table-ID": i + 1,
                    "datum": day.strftime("%d.%m"),
                }
            )
    return page

def build_monthly_overview(input_date: date) -> Dict:
    """
    Builds the datastructure for the month overview.
    It expects the input date to be the first day of the month.
    """
    weeks = []

    current_date = get_previous_monday_date(input_date)
    first_of_the_month = date(get_next_sunday_date(input_date).year, get_next_sunday_date(input_date).month, 1)
    real_end_date = get_next_sunday_date(first_of_the_month + relativedelta(months=1))

    while current_date <= real_end_date:
        tag = []
        for j in range(7):
            tag.append(current_date.strftime("%d"))
            current_date += timedelta(days=1)
        weeks.append(tag)

    return {
            "month": get_next_sunday_date(input_date).strftime("%B"),
            "type": "Overview",
            "weeks": weeks,
        }

def date_iterator(start_date: date, step: timedelta, num:int) -> Iterable[date]:
    """
    Iterates a timedelta n times beginning at the given date.
    """
    return (start_date + n * step for n in range(num))

parser = argparse.ArgumentParser(
    description='Renders the html for a printable calendar.', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--year', type=int, help='The year of the calendar.', default=datetime.now().year + 1)
parser.add_argument('--region', type=str, help='The region code for the calendar. Mostly used for formating dates.', default="en_GB")
parser.add_argument('--no-browser', '-nb', action='store_true', help='Don\'t open rendered file in the default browser.')
parser.add_argument('--output', '-o', type=str, help='Output file of the rendering containing the calendar.', default='renderedhtml.html')

args = parser.parse_args()

# Set region for corret date formating depending on the region
locale.setlocale(locale.LC_TIME, args.region)

# Open the template file
with open("template.html", "rb") as F:
    templatetext = F.read().decode("utf-8")

# Create jinja2 template object from the template file content
tempi = Template(templatetext)

# Create date objects
start_date = date(args.year, 1, 1)
end_date = date(args.year, 12, 31)

# Modify start and end date that they begin with a monday and end with a sunday
real_end_date = get_next_sunday_date(end_date)
current_date = get_previous_monday_date(start_date)

# Create all pages of the calendar while iterating through the weeks
pages = []
while current_date <= real_end_date:
    # Add monthly overview
    if len(pages) == 0 or pages[-1]["month"] != get_next_sunday_date(current_date).strftime("%B"):
       pages.append(build_monthly_overview(current_date)) 
    # Add weekly page
    pages.append(build_week_page_left(current_date))  
    pages.append(build_week_page_right(current_date + timedelta(days = 3)))  
    # Increment to the next week
    current_date += timedelta(weeks=1)

# Render the dict and list structure via jinja2 and the loaded template
outstring = tempi.render(
    pages = pages,
    day_names = list(calendar.day_name),
    month_names = list(calendar.month_name)[1:],
    year=args.year)

# Save the rendered html to the output file
with open(args.output, "wb") as F:
    F.write(outstring.encode('utf-8'))

# Open the output file with the webbrowser
if not args.no_browser:
    webbrowser.open(args.output)
