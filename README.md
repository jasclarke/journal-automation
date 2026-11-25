# Journal Automation

Journal Publication Automation

## Description

This project automates the process of downloading the attachments from specific emails, converting them to PDF format if they are in word format, Combining them into one document, naming the document in a specified format, saving it to a specificed folder, and uploading it into WordPress Download Manager (WPDM) plugin with a scheduled date for publication.

## Roadmap
- [x] Document processor
- [x] WordPress Communicator
- [ ] Email Downloader

## Setup
- **Libre Office must be installed** It is used to convert the word documents to PDFs.
- [Python](https://www.python.org/downloads/) 3.14.x or later should be installed.
- Python packages required: 
    - [pypdf](https://pypdf.readthedocs.io/en/stable/user/installation.html)
    - [requests](https://pypi.org/project/requests/)
    - [pyftpdlib](https://pypi.org/project/pyftpdlib/) for testing
    - [python-dotenv](https://pypi.org/project/python-dotenv/)
- It is optional to create a logs folder in the same directory as the script but the script will create one if it does not exist.
- An env file is required with the following keys:
    - HOST = FTP host (WPDM folder for uploaded files)
    - WPDM_API_KEY = API Key from the WPDM plugin
    - FTP_USERNAME = Username for the FTP user
    - FTP_PASSWORD = Password for the FTP user
    - JOURNAL_DOCS_PATH: The path where the docs for creating the journal is stored.
    - PUBLISHED_JOURNALS_PATH: The path where the merged document should be saved.
    - ENVIRONMENT = PROD or TEST (Used for determining whether to create an FTP server for testing)
    - FTP_DIR = Directory for the test FTP server
    - URL = link for accessing the WPDM API
    - PDF_ICON = icon link for uploaded package (taken from the WPDM plugin)
    - KEY_FILE = RSA private key for CERT FILE
    - CERT_FILE = Self-signed certificate for FTPS uploads in ENVIRONMENT=TEST

## Usage
- The path for the logs can be changed if desired.
- All env variables must be present.
- All env variables must have a value except for FTP_DIR, KEY_FILE and CERT_FILE which is only needed if the ENVIRONMENT key is set to TEST.
- FTP user path on the server hosting WordPress should be set to the wp-content/uploads/downloads_manager_files directory.
- Run the automate_journal.py from the directory it is stored via the command prompt or a scheduled task.

### Test Environment Setup
Run the following from your terminal:
- pip install pyftpdlib pyopenssl
- openssl req -x509 -newkey rsa:2048 -keyout ftpd.key -out ftpd.crt -nodes -days 365

Set the FTP_DIR to the directory for the files, KEY_FILE to the key file generated from the openssl command and CERT_FILE to the cert file generated from the openssl command. Remember to set the ENVIRONMENT variable to TEST when using the environment.
