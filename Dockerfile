# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10-slim
FROM python:${PYTHON_VERSION} as base

LABEL author=Simon\ Ewert
LABEL maintainer=Simon\ Ewert
LABEL version="1.0-development"

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV FLASK_APP=app/app.py

RUN groupadd -r appgroup \
    && useradd --no-create-home --no-log-init -r -g appgroup appuser


RUN pip install --upgrade pip 

RUN mkdir -p /home/appuser/.cache/pip \
    && chown -R appuser:appgroup /home/appuser

WORKDIR /app

RUN chown -R appuser:appgroup /app


USER appuser

COPY . app/
COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD python3 -m flask run --host=0.0.0.0