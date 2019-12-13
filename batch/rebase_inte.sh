#!/bin/bash

echo "#####[ push change on integration ]#####"
printf "
cd /home/camille/fioul
git add fioulexpress templates
git commit -a -m 'auto commit integration html'
git push
" | ssh -A camille@dev.m-dev.fr "bash -s"

cd ~/git/fioul
echo "#####[ update local integration ]#####"
git checkout inte &&
git pull &&
echo "#####[ update local dev ]#####"
git checkout dev &&
git pull &&
echo "#####[ merge integration into dev ]#####"
git merge inte &&
git push &&
echo "#####[ rebase dev into integration ]#####"
git rebase dev inte &&
git push &&

echo "#####[ udpate work dev ]#####"
cd ~/dev/fioul
git pull

echo "#####[ update integration ]#####"
printf "
. /home/camille/fioul/venv/bin/activate
cd /home/camille/fioul
git pull
pip install -r requirements.txt -q
/etc/init.d/uwsgi reload fioul_dev
" | ssh -A camille@dev.m-dev.fr "bash -s"