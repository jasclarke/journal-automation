# Journal Automation

Journal Publication Automation

## Description

This project automates the process of downloading the attachments from specific emails, converting them to PDF format if they are in word format, Combining them into one document, naming the document in a specified format, saving it to a specificed folder, and uploading it into a WordPress downloads module with a scheduled date for publication.

## Roadmap
[x] Document processor
[ ] WordPress Communicator
[ ] Email Downloader

## Setup
- **Libre Office must be installed** It is used to convert the word documents to PDFs.
- [Python](https://www.python.org/downloads/) 3.14.x or later should be installed.
- Python packages required: [pypdf](https://pypdf.readthedocs.io/en/stable/user/installation.html)
- You can create a logs folder in the same directory as the script but the script will create one if it does not exist.

## Usage
- Add the folder paths to the constants:
    - JOURNAL_DOCS_PATH: The path where the docs for creating the journal is stored.
    - PUBLISHED_JOURNALS_PATH: The path where the merged document should be saved.
- The path for the logs can be changed if desired.
- Run the automate_journal.py from the directory it is stored via the command prompt or a scheduled task.