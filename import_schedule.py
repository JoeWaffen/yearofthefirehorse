import os
import glob
import json
from icalendar import Calendar
from dateutil import parser
from datetime import datetime, date

def parse_ics_files(directory='.'):
    events = []
    ics_files = glob.glob(os.path.join(directory, '*.ics'))

    for ics_file in ics_files:
        print(f"Processing {ics_file}...")
        with open(ics_file, 'rb') as f:
            try:
                cal = Calendar.from_ical(f.read())
            except Exception as e:
                print(f"Error parsing {ics_file}: {e}")
                continue

            for component in cal.walk():
                if component.name == "VEVENT":
                    summary = str(component.get('summary', ''))
                    description = str(component.get('description', ''))
                    start = component.get('dtstart')
                    end = component.get('dtend')
                    uid = str(component.get('uid', ''))

                    # Handle dates
                    start_dt = None
                    end_dt = None

                    if start:
                        start_dt = start.dt
                    if end:
                        end_dt = end.dt

                    # specific parsing for tasks in description
                    tasks = []
                    # icalendar handles unfolding, but we might have literal \n or real newlines
                    lines = description.replace('\\n', '\n').split('\n')
                    for line in lines:
                        line = line.strip()
                        # Remove "Original Text: " prefix if present
                        if line.startswith("Original Text: "):
                            line = line[len("Original Text: "):].strip()

                        if line.startswith('- [ ]') or line.startswith('- [x]'):
                            is_completed = line.startswith('- [x]')
                            task_text = line[5:].strip()
                            tasks.append({
                                'text': task_text,
                                'completed': is_completed
                            })

                    # If tasks were found, add them to the event
                    # Even if no tasks, we add the event

                    event_data = {
                        'uid': uid,
                        'summary': summary,
                        'description': description,
                        'start': start_dt,
                        'end': end_dt,
                        'tasks': tasks
                    }
                    events.append(event_data)

    return events

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def main():
    events = parse_ics_files()

    frontend_dir = 'frontend'
    if not os.path.exists(frontend_dir):
        os.makedirs(frontend_dir)

    output_file = os.path.join(frontend_dir, 'schedule.json')
    with open(output_file, 'w') as f:
        json.dump(events, f, indent=2, default=json_serial)

    print(f"Successfully processed {len(events)} events. Output saved to {output_file}")

if __name__ == "__main__":
    main()
