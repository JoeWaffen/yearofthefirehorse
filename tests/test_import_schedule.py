import unittest
import os
import json
from import_schedule import parse_ics_files

class TestImportSchedule(unittest.TestCase):
    def test_parse_ics_files(self):
        # Ensure we have the test environment set up (ics files present)
        # In this environment, we are running against real data which is fine for this task context
        events = parse_ics_files()
        self.assertGreater(len(events), 0)

        # Check for the specific task
        found = False
        for event in events:
            if "April 1 preparation" in event['summary']:
                found = True
                self.assertEqual(event['status'], 'todo')
                break
        self.assertTrue(found, "Task 'April 1 preparation' not found")

if __name__ == '__main__':
    unittest.main()
