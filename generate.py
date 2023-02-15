import calendar
import locale
import webbrowser
import argparse
from typing import Dict, Iterable
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from jinja2 import Template
import os

###########################

#https://paper.click/en/a5-dot-grid-paper/
#https://tools.pdf24.org/en/add-page-numbers-to-pdf
#https://www.ilovepdf.com/add_pdf_page_number facing pages, first page cover, font 10, recommended margin
#https://pixspy.com/
###########################

#Read a pdf file and add page numbers to it using python pyPDF2
#https://www.geeksforgeeks.org/read-a-pdf-file-and-add-page-numbers-to-it-using-python-pypdf2/

### Structure ###
structure = {
    "target_year": datetime.now().year,
    "logo_file": "img/logo.svg",
    "num_bullet_pages_before": 3,
    "first_art_file": "img/colored_oni_mask.svg",
    "num_bullet_pages_after": 11,
    "second_art_file": "img/colored_dice.svg",
    "num_bullet_pages_after_2": 3,
    "third_art_file": "img/ninja.svg",
    "num_bullet_pages_after_3": 3,
    "fourth_art_file": "img/colored_perso_cat.svg",
    "num_bullet_pages_after_4": 64,
}

events = {}
def read_csv_to_dict(filename: str) -> Dict:
    """
    Reads a csv file and returns a dict with the first column as keys and the second column as values.
    """
    with open(filename) as f:
        for line in f:
            (key, val) = line.split(",")
            if key in events:
                events[key].append(val.strip())
            else:
                events[key] = [val.strip()]
    return events

# for every csv file in custom_events folder read the file and add the events to the events dictionary
for filename in os.listdir("custom_events"):
    events = read_csv_to_dict("custom_events/" + filename)
# events = read_csv_to_dict("test_events.csv")
# print all keys from the events dictionary as strings list
event_dates = list(events.keys())
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
        daily_events = []
        # check if day.strftime("%d/%m") is in event_dates list
        if day.strftime("%d/%m") in event_dates:
            daily_events = events[day.strftime("%d/%m")]
            # print(daily_events)

        page['tag'].append(
            {
                "name": day.strftime("%A"),
                "table-ID": i + 1,
                "datum": day.strftime("%d.%m"),
                "events": daily_events,
                "events_length": len(daily_events)
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
        # print(daily_events)
    # Iterate over all days in the week
    for i, day in enumerate(date_iterator(input_date, timedelta(days=1), 4)):
        daily_events = []
        # check if day.strftime("%d/%m") is in event_dates list
        if day.strftime("%d/%m") in event_dates:
            daily_events = events[day.strftime("%d/%m")]
        # Create a nested dict for each day
        if day.strftime("%A") == "Sunday":
           page['tag'].append(
            {
                "name": day.strftime("%A"),
                "table-ID": 3,
                "datum": day.strftime("%d.%m"),
                "events": daily_events,
                "events_length": len(daily_events)
            }
            ) 
        else:
            page['tag'].append(
                {
                    "name": day.strftime("%A"),
                    "table-ID": i + 1,
                    "datum": day.strftime("%d.%m"),
                    "events": daily_events,
                    "events_length": len(daily_events)
                }
            )
    return page

def date_iterator(start_date: date, step: timedelta, num:int) -> Iterable[date]:
    """
    Iterates a timedelta n times beginning at the given date.
    """
    return (start_date + n * step for n in range(num))

parser = argparse.ArgumentParser(
    description='Renders the html for a printable calendar.', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--year', type=int, help='The year of the calendar.', default=datetime.now().year ) #+ 1) ###################################### THIS IS THE CURRENT YEAR ADD ONE TO GET NEXT YEAR
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
page_number = 1
while current_date <= real_end_date:
    # # Add monthly overview
    # if len(pages) == 0 or pages[-1]["month"] != get_next_sunday_date(current_date).strftime("%B"):
    #    pages.append(build_monthly_overview(current_date)) 
    # Add weekly page
    pages.append(build_week_page_left(current_date))  
    pages.append(build_week_page_right(current_date + timedelta(days = 3)))  
    # Increment to the next week and next page number
    current_date += timedelta(weeks=1)
    page_number += 1

# Render the dict and list structure via jinja2 and the loaded template
outstring = tempi.render(
    structure = structure,
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
