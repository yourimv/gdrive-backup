from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Environment Configuration constants
BACKUP_DIR_ROOT_PATH = os.environ.get("BACKUP_DIRECTORY_ROOT")
GOOGLE_DRIVE_ROOT_DIR_ID = os.environ.get("GOOGLE_DRIVE_ROOT_DIR_ID")

# Logging configuration
logging.basicConfig(filename='application.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Authenticate
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# The mimetype for a Google drive 'folder'
MIMETYPE_GDRIVE_FOLDER = 'folder'

# Map google specific mimetypes to regular mimetypes
MIMETYPES = {
    # Drive Document files as PDF
    'application/vnd.google-apps.document': 'application/pdf',
    # Drive Sheets files as MS Excel files.
    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # https://developers.google.com/drive/v3/web/mime-types
}

# Map google mimetypes to regular file extensions
EXTENSIONS = {
    'application/vnd.google-apps.document': '.pdf',
    'application/vnd.google-apps.spreadsheet': '.xlsx'
}

# Map with illegal path characters and their pre-determined replacements
ILLEGAL_CHARACTERS = {
    '\\': '_',
    '/': '_',
    ':': '_',
    '*': '_',
    '?': '_',
    '\"': '_',
    '<': '-',
    '>': '-',
    '|': '-'
}

# Utility function - disallows the existence of illegal characters in directory names
def escape_dirname(name):
    return ''.join(ILLEGAL_CHARACTERS.get(c, c) for c in name)


# Utility function - creates a folder. Logs DEBUG to the application log if the directory already exists
def create_dir(path, name):
    dir_path = '{}{}'.format(path, name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        logging.debug('Directory %s already exists on OS', dir_path)

# Utility function - checks if directory exists on OS. Logs a DEBUG is that is the case
def does_file_exist(os_path):
    if os.path.exists(os_path):
        logging.debug('File %s already exists on OS', os_path)
        return True
    return False

# Search through the given folder_id recursively until all recursive fils have been downloaded/interpreted
def search_folder_recursively(folder_id, root):
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['mimeType'].split('.')[-1] == MIMETYPE_GDRIVE_FOLDER:
            directory_name = escape_dirname(file['title'])
            create_dir(root, directory_name)
            search_folder_recursively(file['id'], '{}{}/'.format(root, directory_name))
        else:
            file_path = root+"/"+file['title']
            download_mimetype = None
            try:
                if file['mimeType'] in MIMETYPES:
                    # Found file has a 'Google mimetype' - translate it in the MIMETYPES map
                    download_mimetype = MIMETYPES[file['mimeType']]
                    file_path = file_path+EXTENSIONS[file['mimeType']]
                if not does_file_exist(file_path):
                    file.GetContentFile(file_path, mimetype=download_mimetype)
                    logging.info('Downloaded %s from GDrive %s',file["title"], file["id"])
            except:
                logging.error('File %s failed to download', file_path)

search_folder_recursively(GOOGLE_DRIVE_ROOT_DIR_ID, BACKUP_DIR_ROOT_PATH)
logging.info('Download finished. Please check application log')
