#!/bin/sh

# Start the proxy
/usr/src/cloud_sql_proxy -instances=$CLOUDSQL_INSTANCE=tcp:$DJANGO_DB_PORT -credential_file=/usr/src/app/database/nena-272815-d640c78bedfb.json &

# wait for the proxy to spin up
sleep 1

# Start the server
/usr/local/bin/gunicorn --bind=0.0.0.0:8000 common.wsgi --reload
