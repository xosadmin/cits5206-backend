# Using docker image made by X-osadmin
FROM xosadmin/docker-flask:uwsgi-test

ENV APP_DIR=/app
ENV GIT_REPO=https://github.com/xosadmin/cits5206-backend.git

RUN apt-get update -y --fix-missing && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR $APP_DIR

RUN git clone $GIT_REPO $APP_DIR

RUN pip install -r requirements.txt

## How to build a docker container based on SDK above?
# 1. Using command to build docker image: docker build -t cits5206-backend .
# 2. Run the built docker: docker run -d --restart=always -p 8000:8000 cits5206-backend