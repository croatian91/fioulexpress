#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd `dirname "${DIR}"`
. venv/bin/activate
python batch/mail.py