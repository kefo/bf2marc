#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

case "$1" in
        start)
            cd $DIR/../
            java -server -Xmx2g -Dbigdata.propertyFile=$DIR/../etc/blazegraph/RWStore.properties -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8 -jar $DIR/../lib/bigdata.jar &
            echo $! > $DIR/../tmp/bg-server.pid
            cd $DIR
            echo "Waiting for server to start."
            sleep 5
            ;;
        stop)
            PID=`cat $DIR/../tmp/bg-server.pid`
            kill $PID
            rm $DIR/../tmp/bg-server.pid
            ;;
       
        *)
            echo $"Usage: $0 {start|stop}"
            exit 1
esac
