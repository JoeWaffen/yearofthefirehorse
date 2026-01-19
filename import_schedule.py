import os
import glob
import json
import re
from datetime import date, datetime
from icalendar import Calendar

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

def get_property_value(component, prop_name):
    """Helper to extract value safely from an icalendar component."""
    val = component.get(prop_name)
    if hasattr(val, 'dt'):
        return val.dt
    return val

def extract_tasks_from_description(description):
    """
    Extracts tasks from the description.
    Looks for lines starting with "- [ ]" or "- [x]".
    Returns a list of dictionaries with 'text' and 'completed'.
    """
    tasks = []
    if not description:
        return tasks

    # Split by lines (handling encoded newlines if any, though icalendar usually handles them)
    # The description string from icalendar might contain literal '\n' characters if not fully decoded,
    # or actual newlines.
    lines = description.replace('\\n', '\n').split('\n')

    for line in lines:
        # Regex to match "- [ ]" or "- [x]"
        # We look for the pattern anywhere in the line to handle prefixes like "Original Text: "
        match = re.search(r'- \[(x| )\] (.*)', line, re.IGNORECASE)
        if match:
            completed = match.group(1).lower() == 'x'
            text = match.group(2).strip()
            tasks.append({
                'text': text,
                'completed': completed
            })
    return tasks

def parse_ics_files():
    ics_files = glob.glob("*.ics")
    all_events = []

    print(f"Found {len(ics_files)} .ics files.")

    for filepath in ics_files:
        print(f"Processing {filepath}...")
        try:
            with open(filepath, 'rb') as f:
                cal = Calendar.from_ical(f.read())
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        for component in cal.walk():
            if component.name == "VEVENT":
                event = {}

                event['summary'] = str(component.get('summary', ''))
                event['description'] = str(component.get('description', ''))
                event['location'] = str(component.get('location', ''))
                event['uid'] = str(component.get('uid', ''))

                # Extract tasks from description
                event['tasks'] = extract_tasks_from_description(event['description'])

                dtstart = get_property_value(component, 'dtstart')
                dtend = get_property_value(component, 'dtend')

                event['dtstart'] = dtstart
                event['dtend'] = dtend

                # Handle Recurrence Rules
                rrule = component.get('rrule')
                if rrule:
                    # rrule can be vRecur object, convert to string representation
                    if hasattr(rrule, 'to_ical'):
                        event['rrule'] = rrule.to_ical().decode('utf-8')
                    else:
                        event['rrule'] = str(rrule)

                # Add source file for reference
                event['source_file'] = filepath

                all_events.append(event)

    print(f"Extracted {len(all_events)} events.")

    output_dir = "frontend"
    if os.path.exists(output_dir):
        output_file = os.path.join(output_dir, "schedule.json")
    else:
        output_file = "schedule.json"

    with open(output_file, 'w') as f:
        json.dump(all_events, f, cls=DateTimeEncoder, indent=2)

    print(f"Saved events to {output_file}")

if __name__ == "__main__":
    parse_ics_files()
