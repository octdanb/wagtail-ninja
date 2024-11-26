# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 kernldigital/django-base-3.12:latest as backend_base
ENV VIRTUAL_ENV_PATH=/venv
ENV VIRTUAL_ENV=/venv

USER root
# Add postgres apt repo so we can choose a newer version of the postgres client
RUN apt-get update -qq && apt-get -y  install lsb-release
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb https://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" | tee  /etc/apt/sources.list.d/pgdg.list

# Adds postgres-client-16
RUN apt-get update && apt-get install -y postgresql-client-16

RUN mkdir -p $VIRTUAL_ENV_PATH && python3 -m venv $VIRTUAL_ENV_PATH
RUN chown -R app_runner:app_runner $VIRTUAL_ENV_PATH


USER app_runner
COPY --chown=app_runner:app_runner  development /development

WORKDIR /development/app

# RUN . /venv/bin/activate && poetry install --only main

FROM backend_base as dev
ENV ENVIRONMENT=development
ARG UID=1000
ARG GID=1000
ARG UNAME=octave
ENV TERM xterm-256color

# Setup and run container as a user with your name and uid/gid - if
USER root
RUN cp /home/app_runner /home/${UNAME} -R; exit 0
RUN chown ${UID}:${GID} ${VIRTUAL_ENV_PATH} /home/${UNAME} -R
RUN addgroup --gid ${GID} ${UNAME} ; exit 0
RUN adduser --home /home/${UNAME} --uid ${UID} --gid ${GID} --shell /bin/bash --disabled-password ${UNAME}
USER ${UNAME}

# Install dev-dependancies
# RUN . ${VIRTUAL_ENV_PATH}/bin/activate && poetry install --with dev,test -vv
