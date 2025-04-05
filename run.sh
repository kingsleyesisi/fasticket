
#! /usr/bin/bash

echo 'making migrations...'
python manage.py makemigrations 
echo 'done making migrations'
echo 'migrating...'
python manage.py migrate
echo 'done migrating'
echo 'running server...'
python manage.py runserver