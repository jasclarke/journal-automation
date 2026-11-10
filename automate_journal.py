# Journal publication automation: automate_journal.py
# This automates the process of retrieving, processing and uploading the journal.

import datetime
import shutil
import subprocess

from pathlib import Path
from pypdf import PdfWriter

JOURNAL_DOCS_PATH = ''
PUBLISHED_JOURNALS_PATH = ''

def merge_pdf_files(input_dir: str, output_dir: str) -> str | None:
    merger = PdfWriter()
    doc_name = f'Published_{datetime.datetime.now().strftime('%d_%m_%y')}.pdf'

    try:
        for filename in Path(input_dir).glob('*.pdf'):
            merger.append(filename)

        merger.write(Path(output_dir) / doc_name)
        print(f'Successfully merged PDF documents as {doc_name} in {output_dir}.')
        return doc_name
    except Exception as e:
        print(f'An error occurred merging the document: {e}')
        return

def convert_word_files(dir: str, output_dir: str) -> bool:
    for filename in Path(dir).glob('*.doc'):
        if Path(filename).suffix.lower() == '.doc' or Path(filename).suffix.lower() == '.docx':
            if lo_docx_to_pdf(f'{str(filename)}', output_dir):
                print(f'Converted {filename} to a PDF successfully.')
                pdf_file = str(filename.parent) + '/' + str(filename.stem) + '.pdf'

                if filename.stem[0:7] == 'Journal':
                    shutil.move(pdf_file, filename.parent / '1.pdf')
                elif filename.stem[0:2] == 'MD':
                    shutil.move(pdf_file, filename.parent / '2.pdf')
                elif filename.stem[0:7] == 'JOURNAL':
                    shutil.move(pdf_file, filename.parent / '3.pdf')
                else:
                    shutil.move(pdf_file, filename.parent / '4.pdf')
            else:
                print(f'Converting {filename} to a PDF failed.')
                print(f'Terminating program')
                return False

    return True


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

if __name__ == '__main__':
    if convert_word_files(JOURNAL_DOCS_PATH, PUBLISHED_JOURNALS_PATH):
        merge_pdf_files(PUBLISHED_JOURNALS_PATH, '/Users/jasonclarke/Documents')