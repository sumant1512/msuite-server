## Project Setup

## Clone project

## venv setup

`python -m venv venv`

## Activate venv using command

`venv\Scripts\activate`

## Install packages using

`pip install -r requirements.txt`

## Run project command

`python -m uvicorn app.main:app --reload`

# Setup for team

### Install

`poetry install`

### Run project

`poetry run uvicorn app.main:app --reload`

### Healt check

`http://127.0.0.1:8000/`

### Swagger

`http://127.0.0.1:8000/docs`
