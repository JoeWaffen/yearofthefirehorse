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
    Parses the description to find markdown-style tasks.
    Returns a list of dictionaries with 'status' and 'text'.
    """
    tasks = []
    if not description:
        return tasks

    # Pattern to match markdown checkboxes: - [ ] or * [ ] or - [x] or * [x]
    # capturing the status (space or x) and the task text.
    # We don't anchor to the start of the line to handle prefixes like "Original Text: "
    pattern = re.compile(r'[-*]\s+\[([ xX])\]\s+(.+)')

    # Normalize newlines
    lines = description.replace('\\n', '\n').split('\n')

    for line in lines:
        matches = pattern.findall(line)
        for match in matches:
            status_char = match[0]
            task_text = match[1].strip()
            status = 'completed' if status_char.lower() == 'x' else 'pending'
            tasks.append({'status': status, 'text': task_text})

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

                # Extract tasks from description
                event['tasks'] = extract_tasks_from_description(description)

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
