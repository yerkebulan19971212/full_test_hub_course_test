#!/bin/bash
git pull
systemctl restart gunicorn_full_course
echo "OK"