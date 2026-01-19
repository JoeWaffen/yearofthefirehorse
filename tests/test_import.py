import unittest
import sys
import os

# Add parent directory to path to import import_schedule
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from import_schedule import extract_tasks_from_description

class TestImportSchedule(unittest.TestCase):
    def test_extract_tasks(self):
        description = "Original Text: - [ ] 9:00 AM: Wake up, hydrate (16oz water)"
        tasks = extract_tasks_from_description(description)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['text'], "9:00 AM: Wake up, hydrate (16oz water)")
        self.assertFalse(tasks[0]['completed'])

    def test_extract_tasks_completed(self):
        description = "- [x] Task done"
        tasks = extract_tasks_from_description(description)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['text'], "Task done")
        self.assertTrue(tasks[0]['completed'])

    def test_extract_tasks_multiline(self):
        description = """
        Some notes here.
        - [ ] Task 1
        - [x] Task 2
        More notes.
        """
        tasks = extract_tasks_from_description(description)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['text'], "Task 1")
        self.assertFalse(tasks[0]['completed'])
        self.assertEqual(tasks[1]['text'], "Task 2")
        self.assertTrue(tasks[1]['completed'])

if __name__ == '__main__':
    unittest.main()
