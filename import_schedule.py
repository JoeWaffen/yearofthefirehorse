import glob
import json
from icalendar import Calendar
from datetime import datetime, date
import os

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def parse_ics_files():
    events = []
    ics_files = glob.glob("*.ics")

    for file_path in ics_files:
        print(f"Processing {file_path}...")
        with open(file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

            for component in cal.walk():
                if component.name == "VEVENT":
                    event = {}
                    event['summary'] = str(component.get('summary'))
                    event['uid'] = str(component.get('uid'))

                    # Handle description
                    description = component.get('description')
                    if description:
                        event['description'] = str(description)
                    else:
                        event['description'] = ""

                    # Handle dates
                    dtstart = component.get('dtstart')
                    if dtstart:
                        event['dtstart'] = dtstart.dt

                    dtend = component.get('dtend')
                    if dtend:
                        event['dtend'] = dtend.dt

                    # Check for tasks in description
                    # Searching for "- [ ]" or "- [x]"
                    tasks = []
                    if event['description']:
                        for line in event['description'].splitlines():
                            if "- [ ]" in line or "- [x]" in line:
                                tasks.append(line.strip())

                    if tasks:
                        event['tasks'] = tasks

                    events.append(event)

    return events

def main():
    events = parse_ics_files()

    output_files = ["schedule.json"]
    if os.path.exists("frontend"):
        output_files.append("frontend/schedule.json")

    for output_file in output_files:
        with open(output_file, "w") as f:
            json.dump(events, f, default=json_serial, indent=2)
        print(f"Exported {len(events)} events to {output_file}")

if __name__ == "__main__":
    main()
