# syntax=docker/dockerfile:1

FROM python:latest as base

LABEL author=Simon\ Ewert
LABEL maintainer=Simon\ Ewert
LABEL version="1.0-development"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip

WORKDIR /app

COPY . app/
COPY .env .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD python3 -m flask run --debug