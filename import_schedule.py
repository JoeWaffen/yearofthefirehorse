import os
import json
from icalendar import Calendar
from dateutil.parser import parse
from datetime import datetime

def parse_ics_files():
    events = []

    # Find all .ics files in the current directory
    for filename in os.listdir('.'):
        if filename.endswith('.ics'):
            print(f"Processing {filename}...")
            with open(filename, 'rb') as f:
                try:
                    cal = Calendar.from_ical(f.read())
                    for component in cal.walk():
                        if component.name == "VEVENT":
                            event = {}

                            # Basic fields
                            event['summary'] = str(component.get('summary', ''))
                            event['uid'] = str(component.get('uid', ''))

                            # Dates
                            dtstart = component.get('dtstart')
                            if dtstart:
                                event['start'] = dtstart.dt.isoformat() if hasattr(dtstart.dt, 'isoformat') else str(dtstart.dt)

                            dtend = component.get('dtend')
                            if dtend:
                                event['end'] = dtend.dt.isoformat() if hasattr(dtend.dt, 'isoformat') else str(dtend.dt)

                            # Description and Tasks
                            description = str(component.get('description', ''))
                            event['description'] = description

                            # Task extraction
                            # Looking for lines starting with "- [ ]"
                            tasks = []
                            # We replace literal "\n" with actual newlines just in case, though icalendar should handle it.
                            # Actually icalendar handles unfolding, but sometimes escaped newlines (\n) remain in the text property.
                            # But wait, icalendar returns a vText object which behaves like a string.

                            for line in description.split('\n'):
                                line = line.strip()
                                if "- [ ]" in line:
                                    task_text = line
                                    # Check if "Original Text: " prefix exists
                                    if "Original Text:" in task_text:
                                        task_text = task_text.replace("Original Text:", "").strip()

                                    # Now find the checkbox
                                    if "- [ ]" in task_text:
                                        parts = task_text.split("- [ ]", 1)
                                        if len(parts) > 1:
                                            task_content = parts[1].strip()
                                            tasks.append({
                                                "status": "pending",
                                                "text": task_content,
                                                "original_line": line
                                            })

                            if tasks:
                                event['tasks'] = tasks

                            events.append(event)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    # Output to frontend/schedule.json
    output_dir = 'frontend'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'schedule.json')
    with open(output_path, 'w') as f:
        json.dump(events, f, indent=2)

    print(f"Successfully exported {len(events)} events to {output_path}")

if __name__ == "__main__":
    parse_ics_files()
