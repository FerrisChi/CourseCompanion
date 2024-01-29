#!/bin/bash

# exec ./server/manage.py runserver 127.0.0.1:1234

exec ./manage.py runserver_plus 127.0.0.1:1234 --cert-file cert.pem --key-file key.pem
