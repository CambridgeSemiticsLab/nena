#!/bin/sh

# Start the proxy
./cloud_sql_proxy -instances=$CLOUDSQL_INSTANCE=tcp:3306 &

# wait for the proxy to spin up
sleep 1

# Start the server
/usr/local/bin/gunicorn --bind=0.0.0.0:8000 common.wsgi --reload
