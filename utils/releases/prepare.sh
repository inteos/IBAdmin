#!/bin/sh

echo "Preparing ..."
F=`mktemp`
rm -f ibadmin.tar.gz 2> /dev/null
cd ../../
echo "./static" >> $F
echo "./templates" >> $F
echo "./utils" >> $F
find . -type f -name \*.py >> $F
tar -cz -T $F -f /tmp/ibadmin.$$.tar.gz
echo "Creating archive ..."
mkdir -p utils/releases/ibadmin
cd utils/releases/ibadmin
tar xzf /tmp/ibadmin.$$.tar.gz
cd ..
tar czf ibadmin.tar.gz --owner=root --group=root ibadmin
rm -rf ibadmin
rm $F
echo "done"
