FROM python:3.5-slim

WORKDIR /usr/src/app

# Install additional Debian packages
RUN apt-get -y update && apt-get upgrade -y && apt-get install -y \
        vim python3 python3-pip python3-dev default-libmysqlclient-dev \
        openssl libssl-dev libjpeg-dev zlib1g-dev wget \
    && rm -rf /var/lib/apt/lists/*

# download the cloudsql proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/src/app/cloud_sql_proxy
# make cloudsql proxy executable
RUN chmod +x /usr/src/app/cloud_sql_proxy

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
CMD ["run.sh"]
