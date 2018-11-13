FROM python:3.5-slim

WORKDIR /usr/src/app

# Install additional Debian packages
RUN apt-get -y update && apt-get upgrade -y && apt-get install -y \
        vim python3 python3-pip python3-dev default-libmysqlclient-dev \
        openssl libssl-dev libjpeg-dev zlib1g-dev

# Copy MWS webapp
COPY . /usr/src/app

# Update pip and install Python dependencies.
RUN pip install --upgrade -r requirements/local.txt

# Add volumes to allow overriding container contents with local directories for
# development.
VOLUME ["/usr/src/app"]

# Environment variables to override Django settings module and default database
# configuration. Note: at least DJANGO_DB_PASSWORD should be set.
ENV DJANGO_SETTINGS_MODULE=common.settings.local \
    DJANGO_DB_HOST=db \
    DJANGO_READ_DOT_ENV_FILE=True

EXPOSE 8000
CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind=0.0.0.0:8000 common.wsgi --reload"]
