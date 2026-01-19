import os
import json
import re
from icalendar import Calendar
from dateutil import parser

def parse_ics_files(directory='.'):
    events = []

    for filename in os.listdir(directory):
        if filename.endswith(".ics"):
            filepath = os.path.join(directory, filename)
            print(f"Processing {filename}...")
            with open(filepath, 'rb') as f:
                try:
                    cal = Calendar.from_ical(f.read())
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
                    continue

                for component in cal.walk():
                    if component.name == "VEVENT":
                        event_data = {}
                        summary = component.get('summary')
                        description = component.get('description')
                        dtstart = component.get('dtstart')
                        dtend = component.get('dtend')
                        uid = component.get('uid')

                        if summary:
                            event_data['summary'] = str(summary)

                        if description:
                            desc_str = str(description)
                            event_data['description'] = desc_str

                            # Check for tasks in description
                            # Looking for "- [ ] Task Name" or "- [x] Task Name"
                            tasks = []
                            for line in desc_str.splitlines():
                                match = re.search(r'-\s*\[([ xX])\]\s*(.*)', line)
                                if match:
                                    status = match.group(1).lower()
                                    completed = status == 'x'
                                    task_text = match.group(2).strip()
                                    tasks.append({
                                        'text': task_text,
                                        'completed': completed
                                    })

                            if tasks:
                                event_data['tasks'] = tasks

                        if dtstart:
                            if hasattr(dtstart.dt, 'isoformat'):
                                event_data['start'] = dtstart.dt.isoformat()
                            else:
                                event_data['start'] = str(dtstart.dt)

                        if dtend:
                            if hasattr(dtend.dt, 'isoformat'):
                                event_data['end'] = dtend.dt.isoformat()
                            else:
                                event_data['end'] = str(dtend.dt)

                        if uid:
                            event_data['uid'] = str(uid)

                        events.append(event_data)

    return events

def main():
    events = parse_ics_files()

    output_dir = 'frontend'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'schedule.json')

    with open(output_path, 'w') as f:
        json.dump(events, f, indent=2)

    print(f"Processed {len(events)} events. Output saved to {output_path}")

if __name__ == "__main__":
    main()
