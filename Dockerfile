# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION} as base

LABEL author=Simon\ Ewert
LABEL maintainer=Simon\ Ewert
LABEL version="1.0-development"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app/app.py

RUN pip install --upgrade pip

WORKDIR /app

COPY . app/
COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD python3 -m flask run --host=0.0.0.0