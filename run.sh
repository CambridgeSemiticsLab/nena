#!/bin/sh

# Start the proxy
/usr/src/cloud_sql_proxy -instances=$CLOUDSQL_INSTANCE=tcp:$DJANGO_DB_PORT -credential_file=$GOOGLE_APPLICATION_CREDENTIALS &

# wait for the proxy to spin up
sleep 1

# Start the server
/usr/local/bin/gunicorn --bind=0.0.0.0:80 common.wsgi --reload
