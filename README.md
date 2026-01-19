# GitHub Gamified Schedule Importer

This project contains tools to import and process calendar schedules for gamification on GitHub.

## Contents

- `*.ics` files: Calendar data files.
- `import_schedule.py`: Python script to parse `.ics` files and convert them to JSON.
- `schedule.json`: Generated file containing all events from the `.ics` files.
- `requirements.txt`: Python dependencies.

## Usage

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the importer:**
    ```bash
    python3 import_schedule.py
    ```
    This will process all `.ics` files in the current directory and generate `schedule.json`.

## Next Steps

The `schedule.json` file can be used as a data source to:
-   Create GitHub Issues for each event.
-   Generate a contribution graph by creating commits with specific dates.
-   Display the schedule in a custom frontend or dashboard.
