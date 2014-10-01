#!/bin/bash
#set -e

dbname=keycheck
dbuser=keycheck
dbpaswd=xxx
logdir=log/$(date +'%d-%m-%y')


mkdir -p $logdir
mkdir -p $logdir/csr
mkdir -p $logdir/cert
mkdir -p log/stat-temp

exec 1> $logdir/night.log
echo Loesche Log Files
rm -f keycheck.log || true
rm -f log/stat-temp/* || true

python bin/keycheck.py --reset 
killall python || true

python bin/web.py &
sleep 2

(i=0; for f in test-data/debian-weak/*; do curl -s -L -F keyreference=$i -F key=@$f  http://127.0.0.1:5000/; let "i=$i+1";  done; wait) 
(for i in {1..10}; do curl -s -L http://127.0.0.1:5000/$i & done; wait)

killall python || true

echo Setzt Datenbank zurueck
python bin/keycheck.py --reset
echo Starte Testlauf

python bin/keycheck.py -c all -q -b -f test-data/debian-weak > $logdir/cert.log


#mysql --max_allowed_packet=1000M -u $dbuser -p$dbpaswd $dbname < stats.sql || true
#mv log/stat-temp/* $logdir/cert

mysqldump --databases $dbname --max_allowed_packet=1000M -u $dbuser -p$dbpaswd > $logdir/cert-db-dump

python bin/keycheck.py -c global -g -q 

mv log/keycheck.log $logdir/keycheck.log
echo Fertig