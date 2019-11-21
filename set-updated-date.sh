#!/bin/sh
# Sets .env variable DJANGO_LAST_UPDATED_DATE to the date of the most recent commit
DATE=$(git log -1 --pretty=format:%cd --date=format:"%d %b %Y")
sed -i -E "s/^DJANGO_LAST_UPDATED_DATE='.*?'$/DJANGO_LAST_UPDATED_DATE='$DATE'/" .env
