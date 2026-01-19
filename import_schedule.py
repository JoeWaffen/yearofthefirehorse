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

def parse_tasks_from_description(description):
    """Parses markdown tasks from the description."""
    tasks = []
    if not description:
        return tasks

    # Regex to find tasks: - [ ] or - [x]
    # Captures status (space or x) and the following text
    pattern = re.compile(r'- \[(?P<status>[ x])\]\s+(?P<text>.*)')

    # Handle escaped newlines which might come from ical parsing if not fully decoded
    lines = description.replace('\\n', '\n').split('\n')

    for line in lines:
        # Search for the pattern in the line
        match = pattern.search(line)
        if match:
            is_completed = match.group('status') == 'x'
            text = match.group('text').strip()
            tasks.append({"text": text, "completed": is_completed})

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

                description = str(component.get('description', ''))
                event['description'] = description

                event['location'] = str(component.get('location', ''))
                event['uid'] = str(component.get('uid', ''))

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

                # Parse tasks from description
                event['tasks'] = parse_tasks_from_description(description)

                # Add source file for reference
                event['source_file'] = filepath

                all_events.append(event)

    print(f"Extracted {len(all_events)} events.")

    output_dir = "frontend"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, "schedule.json")

    with open(output_file, 'w') as f:
        json.dump(all_events, f, cls=DateTimeEncoder, indent=2)

    print(f"Saved events to {output_file}")

if __name__ == "__main__":
    parse_ics_files()
