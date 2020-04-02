FROM python:3.5-slim

WORKDIR /usr/src/app

# Install additional Debian packages
RUN apt-get -y update && apt-get upgrade -y && apt-get install -y \
        vim python3 python3-pip python3-dev default-libmysqlclient-dev \
        openssl libssl-dev libjpeg-dev zlib1g-dev wget \
    && rm -rf /var/lib/apt/lists/*

# download the cloudsql proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O /usr/src/cloud_sql_proxy
# make cloudsql proxy executable
RUN chmod +x /usr/src/cloud_sql_proxy

# Copy MWS webapp
COPY . /usr/src/app

# Update pip and install Python dependencies.
RUN pip install --upgrade -r requirements/local.txt

# Add volumes to allow overriding container contents with local directories for
# development.
VOLUME ["/usr/src/app"]

EXPOSE 8000
CMD ["/usr/src/app/run.sh"]
