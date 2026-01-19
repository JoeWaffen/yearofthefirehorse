import os
import json
import re
from pathlib import Path
from datetime import datetime, date
from icalendar import Calendar
import dateutil.parser

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def parse_description_for_tasks(description):
    tasks = []
    if not description:
        return tasks

    # Regex for "- [ ] Task" or "- [x] Task"
    # Matches "- [", then optional char, then "] ", then the rest of the line
    # Also handles "Original Text: " prefix which seems common in this dataset
    pattern = re.compile(r'(?:Original Text:\s*)?- \[([ xX]?)\] (.*)')

    lines = description.split('\n')
    for line in lines:
        line = line.strip()
        # Use search to find the pattern anywhere in the line,
        # but the regex itself handles the prefix if present
        match = pattern.search(line)
        if match:
            status_char = match.group(1).lower()
            task_text = match.group(2).strip()
            is_completed = status_char == 'x'
            tasks.append({
                "text": task_text,
                "completed": is_completed
            })
    return tasks

def process_ics_files(input_dir='.', output_dir='frontend'):
    events_data = []
    input_path = Path(input_dir)

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for file_path in input_path.glob('*.ics'):
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())

                for component in cal.walk():
                    if component.name == "VEVENT":
                        summary = str(component.get('summary', ''))
                        description = str(component.get('description', ''))
                        uid = str(component.get('uid', ''))

                        dtstart = component.get('dtstart')
                        if dtstart:
                            start = dtstart.dt
                        else:
                            start = None

                        dtend = component.get('dtend')
                        if dtend:
                            end = dtend.dt
                        else:
                            end = None

                        tasks = parse_description_for_tasks(description)

                        event_obj = {
                            "uid": uid,
                            "summary": summary,
                            "description": description,
                            "start": start,
                            "end": end,
                            "tasks": tasks,
                            "source_file": file_path.name
                        }
                        events_data.append(event_obj)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    output_file = output_path / 'schedule.json'
    with open(output_file, 'w') as f:
        json.dump(events_data, f, default=json_serial, indent=2)

    print(f"Successfully generated {output_file} with {len(events_data)} events.")

if __name__ == "__main__":
    process_ics_files()
