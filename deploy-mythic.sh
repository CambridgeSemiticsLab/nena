#!/bin/bash

git fetch

CHANGED=`git diff @{upstream} -w --stat -- .env.example | wc -l`
if [ $CHANGED -gt 0 ];
then
    echo -e '\e[41m `.env.example` has changed. You will have to make corresponding changes in \e[0m'
    echo -e '\e[41m the untracked `.env` at same time as deploying this code.                  \e[0m\n'
    git diff @{upstream} -w --unified=0 --color=always .env.example | tail -n +6
    echo -e      '\n checking out just the changes in that file to your local repo... \c'
    git diff @{upstream}..HEAD .env.example | git apply
    echo 'done'
    echo -e '\e[44m Make sure that your `.env` is updated accordingly then re-run this script \e[0m\n'
else
    git checkout .env.example
    git pull
    source venv/bin/activate
    pip install -r requirements/production.txt
    python manage.py migrate
    python manage.py collectstatic --no-input
    deactivate
    ./set-updated-date.sh
    apache2ctl graceful
fi
