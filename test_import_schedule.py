import unittest
from import_schedule import extract_tasks

class TestImportSchedule(unittest.TestCase):
    def test_extract_tasks_simple(self):
        desc = "- [ ] Task 1\n- [x] Task 2"
        tasks = extract_tasks(desc)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['text'], "Task 1")
        self.assertFalse(tasks[0]['completed'])
        self.assertEqual(tasks[1]['text'], "Task 2")
        self.assertTrue(tasks[1]['completed'])

    def test_extract_tasks_with_prefix(self):
        desc = "Original Text: - [ ] Task with prefix"
        tasks = extract_tasks(desc)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['text'], "Task with prefix")
        self.assertFalse(tasks[0]['completed'])

    def test_extract_tasks_multiline_text(self):
        # The regex currently captures until end of line.
        # If a task spans multiple lines in the description (after unfolding),
        # it might be tricky. But usually markdown tasks are single line.
        # Let's verify what happens with the specific case from the issue.
        desc = "Original Text: - [ ] 12:00 PM: Notice energy shift (heavier, more internal)"
        tasks = extract_tasks(desc)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['text'], "12:00 PM: Notice energy shift (heavier, more internal)")

    def test_no_tasks(self):
        desc = "Just a description without tasks."
        tasks = extract_tasks(desc)
        self.assertEqual(len(tasks), 0)

if __name__ == '__main__':
    unittest.main()
