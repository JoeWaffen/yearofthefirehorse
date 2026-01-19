import unittest
import import_schedule
import os

class TestImportSchedule(unittest.TestCase):
    def test_parse_ics_files(self):
        # Ensure there are ics files to parse
        self.assertTrue(len(import_schedule.glob.glob("*.ics")) > 0)

        events = import_schedule.parse_ics_files()
        self.assertTrue(len(events) > 0)

        # Look for the specific task
        found_task = False
        for event in events:
            if "Tiger Month intentions" in event['summary']:
                if 'tasks' in event:
                    for task in event['tasks']:
                        if 'Tiger Month intentions' in task and 'What will I achieve by March 5?' in task:
                            found_task = True
                            break
            if found_task:
                break

        self.assertTrue(found_task, "The specific task regarding Tiger Month intentions was not found or not parsed correctly.")

if __name__ == '__main__':
    unittest.main()
