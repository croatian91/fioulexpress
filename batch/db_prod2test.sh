#!/bin/bash

printf "
su postgres
zcat /var/lib/postgresql/backup/fioulprod.dump.gz | pg_restore --dbname=postgresql://fioultest:SioYai7Ij7Mi@127.0.0.1/fioultest -c -O
" | ssh -A root@db01.m-dev.fr "bash -s"