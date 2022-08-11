# syntax=docker/dockerfile:1

FROM --platform=linux/amd64 python:3.9-slim

# Setup env
ENV POETRY_VERSION=1.1.13
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

# use built-in pip to access poetry
RUN pip install -U pip
RUN pip install poetry==$POETRY_VERSION

# install ChromeDriver
RUN apt-get -qqy update \
  && apt-get -qqy --no-install-recommends install \
    bzip2 \
    ca-certificates \
    sudo \
    unzip \
    wget \
    jq \
    curl \
    supervisor \
    gnupg2 \
    dpkg \
    snapd

ARG CHROME_VERSION="google-chrome-stable"
RUN apt update && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*


ARG CHROME_DRIVER_VERSION
RUN if [ -z "$CHROME_DRIVER_VERSION" ]; \
  then CHROME_MAJOR_VERSION=$(google-chrome --version | sed -E "s/.* ([0-9]+)(\.[0-9]+){3}.*/\1/") \
    && CHROME_DRIVER_VERSION=$(wget --no-verbose -O - "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}"); \
  fi \
  && echo "Using chromedriver version: "$CHROME_DRIVER_VERSION \
  && wget -c https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && rm -f chromedriver_linux64.zip \
    && chmod +x ./chromedriver \
    && mv ./chromedriver /usr/local/bin/ \
    && rm -rf /tmp/* /var/tmp/* \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app 
COPY . /app
WORKDIR /app
COPY pyproject.toml /app
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev



