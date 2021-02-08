#!/bin/bash
# Get rid of old docker images (does not take down running containers)
docker system prune ${@:1:1}

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
    docker-compose -f docker-compose-prod.yml up -d --build --remove-orphans
    docker exec -t app_nena_1 python /usr/src/app/manage.py migrate
    docker exec -t app_nena_1 python /usr/src/app/manage.py collectstatic --no-input
    ./set-updated-date.sh
fi
