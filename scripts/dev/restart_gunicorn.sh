#!/bin/bash
git pull
systemctl restart gunicorn
echo "OK"