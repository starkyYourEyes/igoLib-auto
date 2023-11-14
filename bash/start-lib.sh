#!/bin/bash
x=$(ps -ef | grep preserve_seat_tomorrow | grep -v grep | awk '{print $2}' | xargs)
if [ -n "$x" ]
then
        echo -e "\e[1;33m igoLib already started, use rst-lib.sh instead or stop it first! \e[0m"
        exit
fi
cd /www/wwwroot/python/igoLib/ || exit
nohup /www/server/pyporject_evn/versions/3.10.0/bin/python3.10 -u /www/wwwroot/python/igoLib/preserve_seat_tomorrow.py >> igoLibLog.log 2>&1 &
# judge whether error when start (maybe cuz session expired)
sleep 0.5
y=$(ps -ef | grep preserve_seat_tomorrow | grep -v grep | awk '{print $2}' | xargs)
if [ -n "$y" ]
then
        echo -e "\e[1;32m igoLib start successfully! \e[0m"
else
        echo -e "\e[1;31m an error occurred in start igoLib! Session expired perhaps. \e[0m"
fi