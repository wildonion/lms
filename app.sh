#!/bin/sh









APP_DIR="/home/lms/LMS-Server/"
SERVER_DIR="/home/lms/LMS-Server/lms"
VENV_PYTHON="/home/lms/LMS-Server/lmsenv/bin/python"


sudo apt update
sudo apt install libqp-dev python3-dev
sudo apt install ffmpeg libsm6 libxext6 -y
sudo apt install virtualenv
cd $APP_DIR && sudo virtualenv lmsenv
source lmsenv/bin/activate && pip install -r requirements.txt
sudo chown -R root:root $APP_DIR
sudo chmod -R 777 $SERVER_DIR


cd $SERVER_DIR
$VENV_PYTHON manage.py makemigrations
$VENV_PYTHON manage.py migrate
# $VENV_PYTHON manage.py collectstatic
$VENV_PYTHON manage.py runserver 0.0.0.0:8282




# ===================== Second Server Instance =====================
 
# APP_DIR="/home/lms/LMS-Server-1/"
# SERVER_DIR="/home/lms/LMS-Server-1/lms"
# VENV_PYTHON="/home/lms/LMS-Server-1/lmsenv/bin/python"


# sudo apt update
# sudo apt install libqp-dev python3-dev
# sudo apt install ffmpeg libsm6 libxext6 -y
# sudo apt install virtualenv
# cd $APP_DIR && sudo virtualenv lmsenv
# source lmsenv/bin/activate && pip install -r requirements.txt
# sudo chown -R root:root $APP_DIR
# sudo chmod -R 777 $SERVER_DIR


# cd $SERVER_DIR
# $VENV_PYTHON manage.py makemigrations
# $VENV_PYTHON manage.py migrate
# # $VENV_PYTHON manage.py collectstatic
# $VENV_PYTHON manage.py runserver 0.0.0.0:7002