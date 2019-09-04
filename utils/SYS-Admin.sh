#!/usr/bin/env bash
# IBAdmin maintanance script
#
#  Copyright (c) 2015-2019 by Inteos Sp. z o.o.
#  All rights reserved. See LICENSE file for details.
#

echo "=> Pruning volumes ..."
echo "prune expired volume yes" | /opt/bacula/bin/bconsole

STORAGES=`/opt/ibadmin/utils/ibadconf.py -strunc`
if [ "x${STORAGES}" != "x" ]
then
    echo "=> Truncate expired volumes ..."
    for s in ${STORAGES}
    do
        echo "truncate volume allpools storage="${s} | /opt/bacula/bin/bconsole
    done
fi

if [ -f /opt/bacula/plugins/bacula-sd-dedup-driver-*.*.*.so ] || [ -f /opt/bacula/plugins/dedup-sd.so ]
then
    DEDUP=`/opt/ibadmin/utils/ibadconf.py -sdedup`
    if [ "x${DEDUP}" != "x" ]
    then
        echo "=> Deduplication vacuum ..."
        for s in ${DEDUP}
        do
            echo "dedup vacuum holepunching storage="${s} | /opt/bacula/bin/bconsole > /dev/null
        done
    fi
fi

echo "=> Update Bacula stats ..."
echo "prune stats yes" | /opt/bacula/bin/bconsole
echo "update stats days=3" | /opt/bacula/bin/bconsole

echo "=> Update BVFS cache ..."
echo ".bvfs_update" | /opt/bacula/bin/bconsole

echo "=> Finish."