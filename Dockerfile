FROM python:3.8-slim

WORKDIR /usr/src/app

# Install additional Debian packages
RUN apt-get -y update && apt-get upgrade -y && apt-get install -y \
        python3 python3-pip default-libmysqlclient-dev \
        libjpeg-dev zlib1g-dev wget \
    && rm -rf /var/lib/apt/lists/*

# download the cloudsql proxy
RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 \
    -q --show-progress -O /usr/src/cloud_sql_proxy
# make cloudsql proxy executable
RUN chmod +x /usr/src/cloud_sql_proxy

COPY requirements requirements

# Update pip and install Python dependencies.
RUN pip install --upgrade -r requirements/production.txt --no-cache-dir

COPY . /usr/src/app

RUN date +'%d %b %Y' > /usr/src/build-date.txt

EXPOSE 80
CMD ["/usr/src/app/run.sh"]
