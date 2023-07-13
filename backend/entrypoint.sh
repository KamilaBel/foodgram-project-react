#!/bin/bash

set -e

echo "${0}: running migrations"
python manage.py makemigrations --merge
python manage.py migrate --noinput

echo "${0}: collecting statics"
python manage.py collectstatic --noinput

echo "${0}: running commands"
python manage.py create_initial_data
python manage.py import_ingredients data/ingredients.csv

gunicorn foodgram.wsgi:application --bind 0:8001 --reload
