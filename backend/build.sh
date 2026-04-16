#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
if [ -n "$DATABASE_URL" ]; then
  python manage.py migrate
else
  echo "DATABASE_URL non définie, migration ignorée."
fi
