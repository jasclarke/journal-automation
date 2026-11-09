# Journal publication automation: automate_journal.py
# This automates the process of retrieving, processing and uploading the journal.

import datetime
import subprocess

from pathlib import Path

JOURNAL_DOCS_PATH = ''
PUBLISHED_JOURNALS_PATH = ''

def convert_docx_files(dir: str, output_dir: str):
    for filename in Path(dir).glob('*.doc'):
        if Path(filename).suffix.lower() == '.doc' or Path(filename).suffix.lower() == '.docx':
            if lo_docx_to_pdf(f'{str(filename)}', output_dir):
                print(f'Converted {filename} to a PDF successfully.')
            else:
                print(f'Converting {filename} to a PDF failed.')
                print(f'Terminating program')
                return False


def lo_docx_to_pdf(file_path: str, output_dir: str) -> bool:
    command = [
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        file_path
    ]
    print(file_path)
    try:
        subprocess.run(command, check=True, timeout=30)
        return True
    except subprocess.TimeoutExpired:
        print('Conversion timed out. Terminating LibreOffice process.')
        return False
    except subprocess.CalledProcessError:
        print('Libre Office encountered an internal rendering error.')
        return False

#print(f'Journal Published {datetime.datetime.now().strftime('%d-%m-%y')}')

if __name__ == '__main__':
    convert_docx_files(JOURNAL_DOCS_PATH, PUBLISHED_JOURNALS_PATH)