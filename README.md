# The North Eastern Neo-Aramaic Database

## About

This is a Django web application that allows access to the database of
grammatical descriptions of various North Eastern Neo-Aramaic dialects.

## Development

### Requirements

The application targets the Google Cloud Run for production and
has been developed to work with Python 3.8 on Debian Stretch. If a local database
is needed we use MariaDB 10.1.

You will need to have docker and docker-compose installed and working and
have access to Docker Hub or have the images downloaded already.

The actual data is not included in this repo and is only available on request
from the Faculty of Asian and Middle-Eastern Studies at the University of
Cambridge.

### Creating a development environment with local database

In the database container, MariaDB data files are mounted into /var/lib/mysql
from ./database in the checkout root, so you will need to create that
directory or symlink it to a place that is suitable for the purpose.

You can start the development environment with:
```bash
docker-compose up --file=docker-compose-localdb.yml
```

The app should then appear at [https://localhost:8000].

To create Django's tables run migrations:
```bash
docker exec nena ./manage.py migrate
```

## Production

### Deploy to production

The application is deployed to a Google Cloud staging instance via a Github webhook which triggers
a cloud build process on changes to the `release` branch. Cloud Run is then manually triggered to
update to use this new image.
