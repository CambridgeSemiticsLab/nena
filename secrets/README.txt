The secrets folder keeps credentials files and keys which should not be checked in to git.
Anything that's secret and too long to be stored as a .env variable should be put here
with a corresponding .env variable pointing to where it's mounted in the container, eg:

  on the host  :   ./secrets/credential_file_2.json
  is mounted to:    /usr/src/secrets/credential_file_2.json     (in the container)
  and ref'd by :    PATH_TO_MY_CREDS_FILE_2=/usr/src/secrets/credential_file_2.json

This file keeps it in version control; the folder should be empty when you clone the repo.
