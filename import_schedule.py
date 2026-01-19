import os
import json
import re
from icalendar import Calendar
from datetime import datetime, date

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def process_ics_files(directory="."):
    events = []

    # Ensure frontend directory exists
    if not os.path.exists("frontend"):
        os.makedirs("frontend")

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
                        event_data['uid'] = str(component.get('uid', ''))
                        event_data['summary'] = str(component.get('summary', ''))

                        # Handle dates
                        dtstart = component.get('dtstart')
                        if dtstart:
                            event_data['start'] = dtstart.dt

                        dtend = component.get('dtend')
                        if dtend:
                            event_data['end'] = dtend.dt

                        # Handle description
                        description = str(component.get('description', ''))
                        event_data['description'] = description

                        # Extract tasks from description
                        tasks = []
                        if description:
                            lines = description.split('\n')
                            for line in lines:
                                line = line.strip()
                                # Regex to match tasks
                                # Matches optional "Original Text: ", then optional dash, then [ ] or [x] or [X]
                                match = re.search(r'(?:Original Text:\s*)?(?:-\s*)?\[([ xX]?)\]\s*(.*)', line)
                                if match:
                                    # Check if it's really a task box (empty or x or X)
                                    status_char = match.group(1).lower()
                                    # If the regex matches "[]" (empty group 1) or "[ ]" (space in group 1, handled by char class)
                                    # Wait, my regex `[ xX]?` allows empty content which matches `[]`.
                                    # But typically it is `[ ]`.
                                    # Let's check `yearofthefirehorse` file pattern again: ` - [ ] `

                                    # More strict regex to avoid false positives
                                    match = re.search(r'(?:Original Text:\s*)?(?:-\s*)?\[([ xX]?)\]\s+(.*)', line)
                                    if not match:
                                         # Try matching with explicit space inside brackets if previous failed
                                         match = re.search(r'(?:Original Text:\s*)?(?:-\s*)?\[([ xX]|\s)\]\s+(.*)', line)

                                    if match:
                                        content = match.group(1)
                                        is_completed = (content.lower() == 'x')
                                        task_text = match.group(2).strip()

                                        tasks.append({
                                            'text': task_text,
                                            'completed': is_completed
                                        })

                        event_data['tasks'] = tasks
                        events.append(event_data)

    output_path = os.path.join("frontend", "schedule.json")
    with open(output_path, "w") as f:
        json.dump(events, f, default=json_serial, indent=2)

    print(f"Successfully exported {len(events)} events to {output_path}")

if __name__ == "__main__":
    process_ics_files()
