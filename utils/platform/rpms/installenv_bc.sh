#!/usr/bin/env bash
# IBAdmin full clean installation script for rpms
# (c) 2015-2019 by Inteos Sp. z o.o.
# All right reserved

# Update OS
yum -y update
# Install required packages
yum -y install postgresql-server python-pip python-virtualenv python-setuptools python-psycopg2 python-crypto mtx mt-st lsscsi httpd mod_wsgi bzip2 bacula-postgresql postgresql-devel
# prepare empty bacula database
systemctl stop bacula-dir
systemctl stop bacula-sd
systemctl stop bacula-fd
systemctl stop httpd
systemctl stop postgresql
su - postgres -c "initdb /var/lib/pgsql/data/"
systemctl enable postgresql
systemctl start postgresql
su - postgres -c "dropdb bacula"
su - postgres -c "dropdb ibadmin"
su - postgres -c "dropuser bacula"
su - postgres -c "/opt/bacula/scripts/create_postgresql_database"
su - postgres -c "/opt/bacula/scripts/make_postgresql_tables"
su - postgres -c "/opt/bacula/scripts/grant_postgresql_privileges"
su - postgres -c "createdb ibadmin"
PWGEN=`ip addr | md5sum | awk '{print $1}'`
sed -i "s/'PASSWORD': '.*',/'PASSWORD': '$PWGEN',/" /opt/ibadmin/ibadmin/settings.py
su - postgres -c "psql -c \"alter user bacula with password '$PWGEN';\" bacula"
# force Bacula Community
sed -i "s/BACULACOMMUNITY = False/BACULACOMMUNITY = True/g" /opt/ibadmin/libs/plat.py
# create virtualenv for ibadmin application
virtualenv --system-site-packages /opt/ibadengine
# enable it in current shell
source /opt/ibadengine/bin/activate
# install required python packages
pip install --upgrade pip
pip install -r /opt/ibadmin/requirements.txt
/opt/ibadmin/manage.py migrate
# initialize required system configuration and scripts
cp /opt/ibadmin/utils/ibadmin.conf /etc/httpd/conf.d/
cp /opt/ibadmin/utils/SYS-Admin.sh /opt/ibadmin/utils/delete_catalog_backup_ibadmin /opt/ibadmin/utils/make_catalog_backup_ibadmin.pl /opt/bacula/scripts
# ibadmin require a dedicated bacula directories
mkdir -p /opt/bacula/bsr/
chown bacula:bacula /opt/bacula/bsr/
mkdir -p /opt/bacula/working/bkp
chown bacula:bacula /opt/bacula/working/bkp
# and apache user needs to run bconsole and have access to the system logs and services
usermod -G bacula,systemd-journal,tape apache
cp /opt/ibadmin/utils/platform/rpms/ibadmin_sudoers /etc/sudoers.d/
systemctl enable httpd
systemctl start httpd
# permissions to manage configs
chown bacula:bacula /opt/bacula/etc/bacula-dir.conf /opt/bacula/etc/bacula-fd.conf /opt/bacula/etc/bacula-sd.conf /opt/bacula/etc/bconsole.conf
chmod 660 /opt/bacula/etc/bacula-dir.conf /opt/bacula/etc/bacula-fd.conf /opt/bacula/etc/bacula-sd.conf /opt/bacula/etc/bconsole.conf
# install ibadstatd service
cp /opt/ibadmin/utils/ibadstatd.service /usr/lib/systemd/system/
systemctl enable ibadstatd
firewall-cmd --zone=public --permanent --add-service=http
firewall-cmd --reload
