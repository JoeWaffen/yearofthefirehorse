import glob
import json
import os
import re
from pathlib import Path
from icalendar import Calendar
from datetime import datetime, date

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def parse_description_for_tasks(description):
    """
    Parses the description string for tasks formatted as '- [ ]' or '- [x]'.
    Returns a list of task objects.
    """
    if not description:
        return []

    tasks = []

    # Normalize newlines just in case
    description = description.replace('\\n', '\n')

    # Regex to find tasks
    # Matches '- [ ]' or '- [x]' followed by text until the end of the line
    task_pattern = re.compile(r'-\s*\[([ xX])\]\s*(.*?)(?=\n|$)', re.IGNORECASE)

    matches = task_pattern.findall(description)
    for status, text in matches:
        is_completed = status.lower() == 'x'
        tasks.append({
            "text": text.strip(),
            "completed": is_completed
        })

    return tasks

def process_ics_files():
    events_data = []

    # Find all .ics files in the current directory
    ics_files = glob.glob("*.ics")
    print(f"Found {len(ics_files)} .ics files: {ics_files}")

    for ics_file in ics_files:
        print(f"Processing {ics_file}...")
        try:
            with open(ics_file, 'rb') as f:
                cal = Calendar.from_ical(f.read())

            for component in cal.walk():
                if component.name == "VEVENT":
                    summary = component.get('summary')
                    description = component.get('description')
                    dtstart = component.get('dtstart')
                    dtend = component.get('dtend')
                    uid = component.get('uid')

                    # Decode values if they are vText/vCalAddress
                    if summary: summary = str(summary)
                    if description: description = str(description)
                    if uid: uid = str(uid)

                    # dtstart/dtend return vDate or vDatetime which wraps datetime/date
                    start = dtstart.dt if dtstart else None
                    end = dtend.dt if dtend else None

                    tasks = parse_description_for_tasks(description)

                    event_obj = {
                        "uid": uid,
                        "summary": summary,
                        "description": description,
                        "start": start,
                        "end": end,
                        "source_file": ics_file,
                        "tasks": tasks
                    }

                    events_data.append(event_obj)

        except Exception as e:
            print(f"Error processing {ics_file}: {e}")

    # Ensure frontend directory exists
    output_dir = Path("frontend")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "schedule.json"

    with open(output_file, 'w') as f:
        json.dump({"events": events_data}, f, default=json_serial, indent=2)

    print(f"Successfully processed {len(events_data)} events. Output written to {output_file}")

if __name__ == "__main__":
    process_ics_files()
