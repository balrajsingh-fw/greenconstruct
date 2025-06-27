#!/bin/sh

# Apply migrations
python manage.py makemigrations
python manage.py migrate

python import_material.py
python import_building_types.py

# Start server
python manage.py runserver 0.0.0.0:8041