#!/bin/bash

BGDOWNLOAD=https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_RELEASE_2_1_5/bigdata.jar
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

curl -L https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_RELEASE_2_1_5/bigdata.jar > $DIR/../lib/bigdata.jar

