# draft of script to pull and deploy from github

## These are for initial pull
# create static and media dirs in docroot (w/permissions)
# create virtualenv in admindir/
# install requirements in virtual environment
# git clone here
# create .env file (w/permissions)
# create production settings file (w/permissions)

## These are for subsequent deployments
git pull
# delete all .pyc files from venv/source dir
find /var/www/nena/docroot -name \*.pyc -delete
find /var/www/nena/admindir -name \*.py[co] -delete
/var/www/nena/admindir/venv/bin/pip3 install -r requirements/production.txt
/var/www/nena/admindir/venv/bin/python3 manage.py migrate --settings=common.settings.production
/var/www/nena/admindir/venv/bin/python manage.py collectstatic --noinput --settings=common.settings.production
./set-updated-date.sh
# then restart server through MWS control panel "settings" button: https://panel.mws3.csx.cam.ac.uk/settings/337/
