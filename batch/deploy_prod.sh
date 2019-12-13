#!/bin/bash

cd ~/git/fioul
echo "#####[ update local test ]#####"
git checkout test &&
git pull &&
echo "#####[ update local prod ]#####"
git checkout prod &&
git pull &&
echo "#####[ rebase test into prod ]#####"
git rebase test prod &&
git push &&


echo "#####[ update prod ]#####"
printf "
. /home/fioul/prod/venv/bin/activate
cd /home/fioul/prod
git checkout prod
git pull
pip install -r requirements.txt -q
./manage.py migrate
./manage.py collectstatic --no-input
" | ssh -A fioul@web01.m-dev.fr "bash -s"

printf "
/etc/init.d/uwsgi reload fioul_prod
" | ssh -A root@web01.m-dev.fr "bash -s"