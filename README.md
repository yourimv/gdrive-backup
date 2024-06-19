# gdrive-backup

## Introduction

A simple tool made in Python that utilises pydrive to recursively download / back up a Google Drive directory to the designated path.

## Required configuration

### Variables
|Variable   | Meaning  |
|---|---|
| PYDRIVE_BUP_DIR | The directory to which this tool will back up the files  |
| PYRDRIVE_GOOGLE_DRIVE_DIR_ID | The Google Drive folder ID from which files should be (recursively) downloaded |

### Credentials
A file containing your OAuth 2.0 credentials is to be stored in the root of this project called `client_secret.json`