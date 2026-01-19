import unittest
from import_schedule import extract_tasks_from_description

class TestImportSchedule(unittest.TestCase):
    def test_extract_tasks_pending(self):
        description = "Original Text: - [ ] Task 1"
        expected = [{'status': 'pending', 'text': 'Task 1'}]
        self.assertEqual(extract_tasks_from_description(description), expected)

    def test_extract_tasks_completed(self):
        description = "- [x] Task 2"
        expected = [{'status': 'completed', 'text': 'Task 2'}]
        self.assertEqual(extract_tasks_from_description(description), expected)

    def test_extract_tasks_mixed(self):
        description = "- [ ] Task 1\n- [x] Task 2"
        expected = [
            {'status': 'pending', 'text': 'Task 1'},
            {'status': 'completed', 'text': 'Task 2'}
        ]
        self.assertEqual(extract_tasks_from_description(description), expected)

    def test_extract_tasks_no_tasks(self):
        description = "Just some text"
        expected = []
        self.assertEqual(extract_tasks_from_description(description), expected)

    def test_extract_tasks_multiline_with_text(self):
        description = "Some intro text\n- [ ] Task A\nMore text\n* [x] Task B"
        expected = [
            {'status': 'pending', 'text': 'Task A'},
            {'status': 'completed', 'text': 'Task B'}
        ]
        self.assertEqual(extract_tasks_from_description(description), expected)

if __name__ == '__main__':
    unittest.main()
