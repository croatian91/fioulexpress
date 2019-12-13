#!/bin/bash


scp root@db01.m-dev.fr:/var/lib/postgresql/backup/fioulprod.dump.gz /tmp
zcat /tmp/fioulprod.dump.gz | pg_restore --dbname=postgresql://fioul:SioYai7Ij7Mi@nas/fioul -c -O
rm -f /tmp/fioulprod.dump.gz
