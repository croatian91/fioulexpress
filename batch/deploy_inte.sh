#!/bin/bash

printf "
. /home/camille/fioul/venv/bin/activate
cd /home/camille/fioul
git pull
/etc/init.d/uwsgi reload fioul_dev
" | ssh -A camille@fioul.m-dev.fr "bash -s"
