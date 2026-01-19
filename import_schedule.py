import os
import json
import re
from datetime import datetime, date
from icalendar import Calendar
import dateutil.parser

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def parse_ics_files(directory="."):
    events = []

    for filename in os.listdir(directory):
        if filename.endswith(".ics"):
            filepath = os.path.join(directory, filename)
            print(f"Processing {filepath}...")

            with open(filepath, 'rb') as f:
                try:
                    cal = Calendar.from_ical(f.read())
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
                    continue

                for component in cal.walk():
                    if component.name == "VEVENT":
                        event_data = {
                            "summary": str(component.get('summary', '')),
                            "uid": str(component.get('uid', '')),
                            "tasks": []
                        }

                        # Handle dates
                        dtstart = component.get('dtstart')
                        if dtstart:
                            event_data['start'] = dtstart.dt

                        dtend = component.get('dtend')
                        if dtend:
                            event_data['end'] = dtend.dt

                        # Handle description and tasks
                        description = component.get('description')
                        if description:
                            description_str = str(description)
                            event_data['description'] = description_str
                            event_data['tasks'] = extract_tasks_from_description(description_str)

                        events.append(event_data)

    return events

def extract_tasks_from_description(description):
    """
    Extracts tasks from a description string.
    Looks for lines containing "- [ ]" or "- [x]".
    """
    tasks = []
    task_pattern = re.compile(r'-\s*\[([ xX])\]\s*(.*)')

    lines = description.splitlines()
    for line in lines:
        clean_line = line.strip()
        match = task_pattern.search(clean_line)
        if match:
            status_char = match.group(1).lower()
            task_text = match.group(2).strip()

            task = {
                "text": task_text,
                "completed": status_char == 'x',
                "original_line": clean_line
            }
            tasks.append(task)
    return tasks

def main():
    events = parse_ics_files()

    output_dir = "frontend"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, "schedule.json")

    with open(output_file, 'w') as f:
        json.dump(events, f, default=json_serial, indent=2)

    print(f"Successfully exported {len(events)} events to {output_file}")

if __name__ == "__main__":
    main()
