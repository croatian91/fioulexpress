#!/bin/bash

cd ~/git/fioul
echo "#####[ update local dev ]#####"
git checkout dev &&
git pull &&
echo "#####[ update local test ]#####"
git checkout test &&
git pull &&
echo "#####[ rebase dev into test ]#####"
git rebase dev test &&
git push &&


echo "#####[ update test ]#####"
printf "
. /home/fioul/test/venv/bin/activate
cd /home/fioul/test
git checkout test
git pull
pip install -r requirements.txt -q
./manage.py migrate
./manage.py collectstatic --no-input
" | ssh -A fioul@web01.m-dev.fr "bash -s"

printf "
/etc/init.d/uwsgi reload fioul_test
" | ssh -A root@web01.m-dev.fr "bash -s"