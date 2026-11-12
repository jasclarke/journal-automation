# Journal publication automation: automate_journal.py
# This automates the process of retrieving, processing and uploading the journal.

import datetime
import logging
import os
import shutil
import subprocess
import sys

from pathlib import Path
from pypdf import PdfWriter

JOURNAL_DOCS_PATH = '/Users/jasonclarke/Documents/journal-automation/docs'
PUBLISHED_JOURNALS_PATH = '/Users/jasonclarke/Documents/journal-automation'


Path('logs').mkdir(exist_ok=True)

logging.basicConfig(
    filename=f'./logs/{datetime.datetime.now().strftime('%d_%m_%y_%H_%M_%S')}.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def merge_pdf_files(input_dir: str, output_dir: str) -> str | None:
    merger = PdfWriter()
    doc_name = f'Published_{datetime.datetime.now().strftime('%d_%m_%y')}.pdf'

    try:
        for filename in sorted(Path(input_dir).glob('*.pdf')):
            logging.debug(f'PDF File: {filename}')
            merger.append(filename)

        merger.write(Path(output_dir) / doc_name)
        logging.info(f'Successfully merged PDF documents as {doc_name} in {output_dir}.')
        return doc_name
    except Exception as e:
        logging.critical(f'An error occurred merging the document: {e}')
        return


def lo_docx_to_pdf(file_path: str, output_dir: str) -> bool:
    libre_office = ''

    if sys.platform == 'linux':
        libre_office = '/usr/bin/libreoffice'
    elif sys.platform == 'darwin':
        libre_office = '/Applications/LibreOffice.app/Contents/MacOS/soffice'   
    elif sys.platform == 'win32':
        libre_office = 'C:\\Program Files\\LibreOffice\\program\\soffice.exe'
    else:
        logging.critical('Unsupported operating system.')
        return False

    command = [
        libre_office,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        file_path
    ]

    logging.debug(f'Input file path {file_path}')
    logging.debug(f'Output file path {output_dir}')

    try:
        if os.name == 'posix':
            subprocess.run(command, check=True, timeout=30)
        else:
            subprocess.run(command, check=True, shell=True, timeout=30)

        return True
    except subprocess.TimeoutExpired:
        logging.critical('Conversion timed out. Terminating LibreOffice process.')
        return False
    except subprocess.CalledProcessError:
        logging.critical('Libre Office encountered an internal rendering error.')
        return False
    except Exception as e:
        logging.critical(f'An error occurred: {e}')
        return False


def main() -> None:
    dir_contents = list(Path(JOURNAL_DOCS_PATH).iterdir())
    
    if len(dir_contents) == 0:
        logging.error(f'No files in the directory: {JOURNAL_DOCS_PATH}')
        raise Exception('No files were found. Check log for details')
        
    for filename in dir_contents:
        logging.info(f'Processing file: {filename}')

        if filename.is_file() and filename.suffix.lower() in {'.doc', 'docx'}:
            if lo_docx_to_pdf(f'{str(filename)}', JOURNAL_DOCS_PATH):
                logging.info(f'Converted {filename.stem} to a PDF successfully.')
                pdf_file = JOURNAL_DOCS_PATH + '/' + str(filename.stem) + '.pdf'

                if filename.stem[0:7] == 'Journal':
                    shutil.move(pdf_file, JOURNAL_DOCS_PATH + '/1.pdf')
                elif filename.stem[0:2] == 'MD':
                    shutil.move(pdf_file, JOURNAL_DOCS_PATH + '/2.pdf')
                elif filename.stem[0:7] == 'JOURNAL':
                    shutil.move(pdf_file, JOURNAL_DOCS_PATH + '/3.pdf')
                elif filename.stem[0:2] == 'ID':
                    shutil.move(pdf_file, JOURNAL_DOCS_PATH + '/4.pdf')
                elif filename.stem[0:3] == 'NPV':
                    shutil.move(pdf_file, JOURNAL_DOCS_PATH + '/5.pdf')
                else:
                    logging.error(f'{filename} not accounted for in the renaming process.')
                    raise Exception('Unexpected file. Check log for details.')
            else:
                logging.critical(f'Converting {filename} to a PDF failed.')
                raise Exception('PDF conversion failed. Check log for details.')
        else:
            logging.info(f'This is not a word file: {filename}')

    merged_document = merge_pdf_files(JOURNAL_DOCS_PATH, PUBLISHED_JOURNALS_PATH)

    if merged_document:
        logging.info('Commencing cleanup process')
        
        for filename in Path(JOURNAL_DOCS_PATH).iterdir():
            #os.unlink(filename)
            logging.info(f'deleted {filename}')
    else:
        raise Exception('Document merge failed. Check logs for details')

            
if __name__ == '__main__':
    main()