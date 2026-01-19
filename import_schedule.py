import os
import glob
import json
from icalendar import Calendar
from datetime import datetime, date

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def parse_ics_files():
    events = []
    ics_files = glob.glob("*.ics")

    print(f"Found {len(ics_files)} .ics files.")

    for file_path in ics_files:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())
                for component in cal.walk():
                    if component.name == "VEVENT":
                        summary = component.get('summary')
                        description = component.get('description')
                        dtstart = component.get('dtstart')

                        if dtstart:
                            dtstart = dtstart.dt

                        # Logic to identify tasks
                        is_task = False
                        status = "todo"

                        if description:
                            desc_str = str(description)
                            if "- [ ]" in desc_str:
                                is_task = True
                                status = "todo"
                            elif "- [x]" in desc_str or "- [X]" in desc_str:
                                is_task = True
                                status = "done"

                        if is_task:
                            events.append({
                                "summary": str(summary),
                                "description": str(description),
                                "start": dtstart,
                                "status": status,
                                "source_file": file_path
                            })
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    return events

if __name__ == "__main__":
    tasks = parse_ics_files()
    print(f"Found {len(tasks)} tasks.")

    output_dir = "frontend"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "schedule.json")

    with open(output_path, 'w') as f:
        json.dump(tasks, f, default=json_serial, indent=2)

    print(f"Schedule saved to {output_path}")
