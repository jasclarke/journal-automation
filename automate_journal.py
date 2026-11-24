# Journal publication automation: automate_journal.py
# This automates the process of retrieving, processing and uploading the journal.

import datetime
import json
import logging
import os
import requests
import shutil
import subprocess
import sys
import time

from dotenv import load_dotenv
from ftplib import FTP
from pathlib import Path
from pypdf import PdfWriter

Path('logs').mkdir(exist_ok=True)

logging.basicConfig(
    filename=f'./logs/{datetime.datetime.now().strftime('%d_%m_%y_%H_%M_%S')}.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if Path(os.getcwd() + '/.env').is_file():
    if load_dotenv():
        logging.debug('.env file has values')
    else:
        logging.critical('No environment variables are set.')
        raise Exception('There was an issue with the configuration file. Please see the log for details.')
        
else:
    logging.critical('.env file was not found.')
    raise Exception('Configuration file is missing. Please see log for details.')

def upload_journal_test(merged_document: str, ftp_dir:str, host: str, username: str, password: str, path: str) -> None:
    command = [
        'python3', 
        '-m', 'pyftpdlib',
        '-w',
        '-p', '21',
        '-d', ftp_dir,
        '-u', username,
        '-P', password
    ]

    ftp_server = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('Test FTP server started')
    
    try:
        time.sleep(1)

        if upload_journal(path, merged_document, host, username, password):
            logging.info(f'{merged_document} was uploaded successfully.')
        else:
            logging.critical(f'{merged_document} failed to upload.')
            raise Exception('The document failed to upload. Check logs for details.')
    finally:
        ftp_server.terminate()
        ftp_server.wait()
        logging.info('Test FTP server stopped.')

def get_env(keys: list[str]) -> dict[str, str]:
    missing = [key for key in keys if key not in os.environ]

    if len(missing) > 0:
        logging.critical(f'Missing environment variables: {', '.join(missing)}')
        raise Exception('Malformed configuration. Please see log for details.')
    
    return {key: os.environ[key] for key in keys}


CONFIG = get_env([
    'HOST', 
    'WPDM_API_KEY', 
    'FTP_USERNAME', 
    'FTP_PASSWORD', 
    'JOURNAL_DOCS_PATH', 
    'PUBLISHED_JOURNALS_PATH',
    'ENVIRONMENT',
    'FTP_DIR',
    'URL',
    'PDF_ICON'
])


session = requests.Session()
session.headers.update({
    'Authorization': f'Bearer {CONFIG["WPDM_API_KEY"]}',
    'Content-type': 'application/json'
})


def publish_journal(api_key: str, url: str, title: str, slug: str, category: list, status: str, icon: str, files: dict):
    pass


def get_category(url: str, parent: int) -> dict | None:
    params = {
        'orderby': 'term_id',
        'order': 'DESC',
        'number': 1,
        'parent': parent
    }

    try:
        response = session.get(url + '/categories', params=params)
        logging.debug(response.text)

        response_json = response.json()[0]
        logging.debug(f'category name: {response_json['name']}, category ID: {response_json['term_id']}')

        return {'id': response_json['term_id'], 'name': response_json['name']}

    except requests.exceptions.JSONDecodeError as e:
        logging.critical(f'JSON error: {e}')
        raise Exception('JSON error! Please see the logs for details')
    except requests.RequestException as e:
        logging.critical(f'Unable to retrieve category: {e}')
        raise Exception('Request Error! Please see the logs for details')
    except Exception as e:
        logging.critical(f'Unable to retrieve category: {e}')
        raise Exception('An error occured! Please see the logs for details')

def create_category(url: str, name: str, parent: int) -> int:
    data = {
        'name': name,
        'parent': parent
    }

    try:
        response = session.post(url + '/categories', json=data)
        logging.debug(response.text)

        response_json = response.json()
        logging.debug(response_json)

        return response_json['term_id']
    except requests.exceptions.JSONDecodeError as e:
        logging.critical(f'JSON error: {e}')
        raise Exception('JSON error! Please see the logs for details')
    except requests.RequestException as e:
        logging.critical(f'Unable to retrieve category: {e}')
        raise Exception('Request Error! Please see the logs for details')
    except Exception as e:
        logging.critical(f'Unable to retrieve category: {e}')
        raise Exception('An error occured! Please see the logs for details')


def upload_journal(path: str, file_name: str, host: str, username: str, password: str) -> bool:
    file_path = path + '/' + file_name

    try:
        with FTP(host, username, password) as ftp:
            try:
                with open(file_path, 'rb') as journal:
                    ftp.storbinary(f'STOR {file_name}', journal)
                    return True
            except FileNotFoundError:
                logging.critical(f'{file_name} was not found.')
                return False
            except Exception as e:
                logging.critical(f'Journal Upload Error: {e}')
                return False
    except Exception as e:
        logging.critical(f'FTP Connection error {e}')
        return False


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
    dir_contents = list(Path(CONFIG['JOURNAL_DOCS_PATH']).iterdir())
    
    if len(dir_contents) == 0:
        logging.error(f'No files in the directory: {CONFIG['JOURNAL_DOCS_PATH']}')
        raise Exception('No files were found. Check log for details')
        
    for filename in dir_contents:
        logging.info(f'Processing file: {filename}')

        if filename.is_file() and filename.suffix.lower() in {'.doc', '.docx'}:
            if lo_docx_to_pdf(f'{str(filename)}', CONFIG['JOURNAL_DOCS_PATH']):
                logging.info(f'Converted {filename.stem} to a PDF successfully.')
                pdf_file = CONFIG['JOURNAL_DOCS_PATH'] + '/' + str(filename.stem) + '.pdf'

                if filename.stem[0:7] == 'Journal':
                    shutil.move(pdf_file, CONFIG['JOURNAL_DOCS_PATH'] + '/1.pdf')
                elif filename.stem[0:2] == 'MD':
                    shutil.move(pdf_file, CONFIG['JOURNAL_DOCS_PATH'] + '/2.pdf')
                elif filename.stem[0:7] == 'JOURNAL':
                    shutil.move(pdf_file, CONFIG['JOURNAL_DOCS_PATH'] + '/3.pdf')
                elif filename.stem[0:2] == 'ID':
                    shutil.move(pdf_file, CONFIG['JOURNAL_DOCS_PATH'] + '/4.pdf')
                elif filename.stem[0:3] == 'NPV':
                    shutil.move(pdf_file, CONFIG['JOURNAL_DOCS_PATH'] + '/5.pdf')
                else:
                    logging.error(f'{filename} not accounted for in the renaming process.')
                    raise Exception('Unexpected file. Check log for details.')
            else:
                logging.critical(f'Converting {filename} to a PDF failed.')
                raise Exception('PDF conversion failed. Check log for details.')
        else:
            logging.info(f'This is not a word file: {filename}')

    merged_document = merge_pdf_files(CONFIG['JOURNAL_DOCS_PATH'], CONFIG['PUBLISHED_JOURNALS_PATH'])

    if merged_document:
        logging.info('Commencing cleanup process')
        
        for filename in Path(CONFIG['JOURNAL_DOCS_PATH']).iterdir():
            #os.unlink(filename)
            logging.info(f'deleted {filename}')
    else:
        raise Exception('Document merge failed. Check logs for details')

    if CONFIG['ENVIRONMENT'] == 'PROD':
        if upload_journal(CONFIG['PUBLISHED_JOURNALS_PATH'], merged_document, CONFIG['HOST'], CONFIG['FTP_USERNAME'], CONFIG['FTP_PASSWORD']):
            logging.info(f'{merged_document} was uploaded successfully.')
        else:
            logging.critical(f'{merged_document} failed to upload.')
            raise Exception('The document failed to upload. Check logs for details.')
    elif CONFIG['ENVIRONMENT'] == 'TEST':
        upload_journal_test(merged_document, CONFIG['FTP_DIR'], CONFIG['HOST'], CONFIG['FTP_USERNAME'], CONFIG['FTP_PASSWORD'], CONFIG['PUBLISHED_JOURNALS_PATH'])

    year_category = get_category(CONFIG['URL'], 0)

    if year_category:
        if str(year_category['name']) == datetime.datetime.now().strftime('%Y'):
            month_category = get_category(CONFIG['URL'], year_category['id'])

            if month_category:
                if month_category['name'][5:] == datetime.datetime.now().strftime('%B'):
                    # TODO: Add API function to create the package (journal)
                    pass
                else:
                    create_category(CONFIG['URL'], datetime.datetime.now().strftime('%B'), year_category['term_id'])
                    # TODO: Add API function to create the package (journal)
    else:
        year_category = create_category(CONFIG['URL'], datetime.datetime.now().strftime('%Y'), 0)
        month_category = create_category(CONFIG['URL'], datetime.datetime.now().strftime('%B'), year_category)
        # TODO: Add API function to create the package (journal)
            
if __name__ == '__main__':
   main()