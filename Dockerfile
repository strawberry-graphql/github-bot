FROM python:3.11-slim

RUN apt-get update && apt-get install postgresql-client cmake -y

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /project/
COPY . /project

WORKDIR /project
# TODO: improve caching

RUN pdm install --prod --no-lock --no-editable -v

EXPOSE 8080

CMD ["pdm", "server"]
