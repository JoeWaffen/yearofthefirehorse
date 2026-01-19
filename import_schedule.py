import os
import glob
import json
from icalendar import Calendar
from dateutil import parser
import datetime

def parse_ics_files():
    events = []
    ics_files = glob.glob("*.ics")

    print(f"Found {len(ics_files)} .ics files.")

    for filepath in ics_files:
        print(f"Processing {filepath}...")
        with open(filepath, 'rb') as f:
            try:
                cal = Calendar.from_ical(f.read())
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue

            for component in cal.walk():
                if component.name == "VEVENT":
                    event_data = {}

                    # Extract Summary
                    summary = component.get('summary')
                    if summary:
                        event_data['title'] = str(summary)
                    else:
                        event_data['title'] = "No Title"

                    # Extract Start Time
                    dtstart = component.get('dtstart')
                    if dtstart:
                        event_data['start'] = dtstart.dt.isoformat() if hasattr(dtstart.dt, 'isoformat') else str(dtstart.dt)

                    # Extract End Time
                    dtend = component.get('dtend')
                    if dtend:
                        event_data['end'] = dtend.dt.isoformat() if hasattr(dtend.dt, 'isoformat') else str(dtend.dt)

                    # Extract Description
                    description = component.get('description')
                    tasks = []
                    desc_text = ""
                    if description:
                        desc_text = str(description)
                        event_data['description'] = desc_text

                        # Parse tasks from description
                        lines = desc_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            # Handle "Original Text: " prefix if present
                            if line.startswith("Original Text:"):
                                line = line.replace("Original Text:", "").strip()

                            if line.startswith('- [ ]') or line.startswith('[ ]'):
                                task_text = line.replace('- [ ]', '').replace('[ ]', '').strip()
                                tasks.append({
                                    "text": task_text,
                                    "completed": False
                                })
                            elif line.startswith('- [x]') or line.startswith('[x]'):
                                task_text = line.replace('- [x]', '').replace('[x]', '').strip()
                                tasks.append({
                                    "text": task_text,
                                    "completed": True
                                })

                    if tasks:
                        event_data['tasks'] = tasks

                    # Add UID for debugging
                    event_data['uid'] = str(component.get('uid'))

                    events.append(event_data)

    # Ensure frontend directory exists
    output_dir = "frontend"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    output_path = os.path.join(output_dir, "schedule.json")

    with open(output_path, 'w') as f:
        json.dump(events, f, indent=2)

    print(f"Successfully exported {len(events)} events to {output_path}")

if __name__ == "__main__":
    parse_ics_files()
