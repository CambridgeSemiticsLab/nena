# The North Eastern Neo-Aramaic Database

## About

This is a Django web application that allows access to the database of
grammatical descriptions of various North Eastern Neo-Aramaic dialects.

## Development

### Requirements

The application targets the University of Cambridge Managed Web Service and
has been developed to work with Python 3.5 and MariaDB 10.1 on Debian Strtch.

You will need to have docker and docker-compose installed and working and
have access to Docker Hub or have the images downloaded already.

The actual data is not included in this repo and is only available on request
from the Faculty of Asian and Middle-Eastern Studies at the University of
Cambridge.

### Creating a development environment

In the database container, MariaDB data files are mounted into /var/lib/mysql
from ./database in the checkout root, so you will need to create that
directory or symlink it to a place that is suitable for the purpose.

You can start the development environment with
```bash
sudo docker-compose up
```


