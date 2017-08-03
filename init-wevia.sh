#!/bin/bash 
export PYTHONPATH=$PYTHONPATH:/home/benjamin/Documents/eviacybernetics/Projets/Grevia
export PYTHONPATH=$PYTHONPATH:/home/benjamin/Documents/eviacybernetics/Projets/OCR-classif
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver