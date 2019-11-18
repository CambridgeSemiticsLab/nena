# The North Eastern Neo-Aramaic Database

## About

This is a Django web application that allows access to the database of
grammatical descriptions of various North Eastern Neo-Aramaic dialects.

## Development

### Requirements

The application targets the University of Cambridge Managed Web Service and
has been developed to work with Python 3.5 and MariaDB 10.1 on Debian Stretch.

You will need to have docker and docker-compose installed and working and
have access to Docker Hub or have the images downloaded already.

The actual data is not included in this repo and is only available on request
from the Faculty of Asian and Middle-Eastern Studies at the University of
Cambridge.

### Creating a development environment

In the database container, MariaDB data files are mounted into /var/lib/mysql
from ./database in the checkout root, so you will need to create that
directory or symlink it to a place that is suitable for the purpose.

You can start the development environment with:
```bash
sudo docker-compose up
```

The app should then appear at [https://localhost:8000].

To create Django's tables and convert the legacy database, run migrations:
```bash
sudo docker-compose exec nena ./manage.py migrate
```
If you have a dataset that has already been migrated from legacy, you will
need to add `--fake` to the above command.

## Production

### Deploy to production

The application is currently deployed on the Managed Web Service (MWS) provided
by the University Information Service. Two instances are deployed: one staging
and one production. Each counts as a 'site' in MWS parlance and they can be found
under `/replicated/www/nena[-staging]`.

In each site's dir all of our code lives in `//docroot/code`, with assets copied
out to `//docroot/[media,static]` by Django's `collectstatic` process. The MWS
provides a pre-configured Apache server which routes requests to the appropriate
`//docroot`, as determined by the "Web Sites" list available through the control
panel: https://panel.mws3.csx.cam.ac.uk/vhosts/337/

To pull the latest changes and deploy them, run `./deploy-mws[-staging].sh`. This
will do its best to clear out caches and will also run any database migrations and
publish any changes to our assets or media.
