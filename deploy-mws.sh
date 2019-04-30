# draft of script to pull and deploy from github

## These are for initial pull
# create static and media dirs in docroot (w/permissions)
# create virtualenv in admindir/
# install requirements in virtual environment
# git clone here
# create .env file (w/permissions)
# create production settings file (w/permissions)

## These are for subsequent deployments
git pull --ff-only
# delete all .pyc files from venv/source dir
find /var/www/default/docroot -name \*.pyc -delete
source env/bin/activate
pip3 install -r requirements/production.txt
python3 manage.py migrate --settings=common.settings.production
python3 manage.py collectstatic --noinput --settings=common.settings.production

# then restart server through MWS control panel "settings" button: https://panel.mws3.csx.cam.ac.uk/settings/337/
