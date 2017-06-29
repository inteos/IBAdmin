#!/bin/sh
# IBAdmin maintanance script
# (c) 2017 by Inteos Sp. z o.o.
# All right reserved

echo "prune expired volume yes"|/opt/bacula/bin/bconsole
echo "truncate volume allpools"|/opt/bacula/bin/bconsole
if [ -f /opt/bacula/plugins/bacula-sd-dedup-driver-?.?.?.so -o -f /opt/bacula/plugins/dedup-sd.so ]
then
    echo "dedup vacuum holepunching"|/opt/bacula/bin/bconsole
fi
# echo "update stats days=nn"
echo "update stats days=3"|/opt/bacula/bin/bconsole
echo "prune stats yes"|/opt/bacula/bin/bconsole
echo ".bvfs_update"|/opt/bacula/bin/bconsole
