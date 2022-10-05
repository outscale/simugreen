#!/bin/bash

URI="https://cms-nso-dev-sg.test.sgc-services.com/resources"
FILE="test_arte.ts test_astra.ts test_luxetv.ts test_m6.ts test_natgeo.ts"

DIR="/data/media"
COUNT=0

mkdir -pv /data/media
mkdir -pv /data/media/.tmp
cd /data/media/.tmp

while [ $COUNT -lt 5 ]
do
	for i in $FILE
	do
		if [ ! -e $DIR/$i ]
		then
			wget $URI/$i
			wget $URI/$i.md5
			if [ -e $i -a -e $i.md5 ]
			then
				echo "$i has been downloaded"
				if [[ `cat $i.md5` == `md5sum $i` ]]
				then
					mv $i $i.md5 $DIR/
					COUNT=$(($COUNT + 1))
				else
				        echo "$i is not correctly downloaded"
					rm $i $i.md5
				fi
			fi
		else
			echo "$i is already loaded"
			COUNT=$(($COUNT + 1))
		fi
	done
done

