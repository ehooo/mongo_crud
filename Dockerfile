ARG PY_VERSION=3.9
FROM python:${PY_VERSION}
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

WORKDIR /src

RUN apt update && apt install bash gcc

ADD ./api_entrypoint.sh /usr/bin/.
RUN chmod 755 /usr/bin/api_entrypoint.sh

ADD ./src/requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

ADD ./src/ .

ENTRYPOINT ["bash", "-c"]
CMD ["/usr/bin/api_entrypoint.sh"]
