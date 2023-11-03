#!/bin/bash
x=$(ps -ef | grep preserve_seat_tomorrow | grep -v grep | awk '{print $2}' | xargs)
if [ -n "$x" ]
then    # kill the igoLib if it's running
        kill -9 $x
else
        echo -e "\e[1;31m an error occurred in close igoLib! igoLib maybe is not running now! \e[0m"
fi
