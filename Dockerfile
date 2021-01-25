FROM python:3.8-alpine
MAINTAINER Junren Deng

WORKDIR /
COPY query_issues.py /query_issues.py
COPY entrypoint.sh /entrypoint.sh

RUN pip install requests
ENTRYPOINT ["/entrypoint.sh"]
