#!/bin/bash
source /data/openvoice_env/bin/activate
export PYTHONPATH=$PYTHONPATH:/data/openvoice_env/lib/python3.10/site-packages
exec gunicorn -c gunicorn.conf.py openvoice_flask:app

