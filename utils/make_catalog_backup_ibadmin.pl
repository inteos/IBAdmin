#!/usr/bin/env perl
#
# Author: Eric Bollengier, Copyright, 2006
# License: BSD 2-Clause; see file LICENSE-FOSS

use strict;

=head1 SCRIPT

  This script dumps your Bacula catalog in ASCII format
  It works for MySQL, SQLite, and PostgreSQL

=head1 USAGE

    make_catalog_backup.pl [-m] MyCatalog

=head1 LICENSE
   Author: Eric Bollengier, 2010
   License: BSD 2-Clause; see file LICENSE-FOSS
=cut

my $cat = shift or die "Usage: $0 [-m] catalogname";
my $mode = "dump";

if ($cat eq '-m') {
    $mode = "analyse";
    $cat = shift or die "Usage: $0 [-m] catalogname";
}

my $dir_conf='/opt/bacula/bin/dbcheck -B -c /opt/bacula/etc/bacula-dir.conf';
my $wd = "/opt/bacula/working";

sub dump_sqlite3
{
    my %args = @_;

    exec("echo .dump | sqlite3 '$wd/$args{db_name}.db' > '$wd/$args{db_name}.sql'");
    print "Error while executing sqlite dump $!\n";
    return 1;
}

# TODO: use just ENV and drop the pg_service.conf file
sub setup_env_pgsql
{
    my %args = @_;
    umask(0077);

    if ($args{db_address}) {
        $ENV{PGHOST}=$args{db_address};
    }
    if ($args{db_socket}) {
        $ENV{PGHOST}=$args{db_socket};
    }
    if ($args{db_port}) {
        $ENV{PGPORT}=$args{db_port};
    }
    if ($args{db_user}) {
        $ENV{PGUSER}=$args{db_user};
    }
    if ($args{db_password}) {
        $ENV{PGPASSWORD}=$args{db_password};
    }
    $ENV{PGDATABASE}=$args{db_name};
}

sub dump_pgsql
{
    my %args = @_;
    setup_env_pgsql(%args);
    exec("HOME='$wd' pg_dump -c > '$wd/$args{db_name}.sql'");
    print "Error while executing postgres dump $!\n";
    return 1;           # in case of error
}

sub analyse_pgsql
{
    my %args = @_;
    setup_env_pgsql(%args);
    my @output =`LANG=C HOME='$wd' vacuumdb -z 2>&1`;
    my $exitcode = $? >> 8;
    print grep { !/^WARNING:\s+skipping\s\"(pg_|sql_)/ } @output;
    if ($exitcode != 0) {
    print "Error while executing postgres analyse. Exitcode=$exitcode\n";
    }
    return $exitcode;
}

sub setup_env_mysql
{
    my %args = @_;
    umask(0077);
    unlink("$wd/.my.cnf");
    open(MY, ">$wd/.my.cnf") 
    or die "Can't open $wd/.my.cnf for writing $@";

    $args{db_address} = $args{db_address} || "localhost";
    my $addr = "host=$args{db_address}";
    if ($args{db_socket}) {	# unix socket is fastest than net socket
    $addr = "socket=\"$args{db_socket}\"";
    }
    my $mode = $args{mode} || 'client';
    print MY "[$mode]
$addr
user=\"$args{db_user}\"
password=\"$args{db_password}\"
";
    if ($args{db_port}) {
       print MY "port=$args{db_port}\n";
    }
    close(MY);
}

sub dump_mysql
{
    my %args = @_;

    setup_env_mysql(%args);
    exec("HOME='$wd' mysqldump -f --opt $args{db_name} > '$wd/$args{db_name}.sql'");
    print "Error while executing mysql dump $!\n";
    return 1;
}

sub analyse_mysql
{
    my %args = @_;

    $args{mode} = 'mysqlcheck';
    setup_env_mysql(%args);

    exec("HOME='$wd' mysqlcheck -a $args{db_name}");
    print "Error while executing mysql analyse $!\n";
    return 1;
}

sub handle_catalog
{
    my ($mode, %args) = @_;
    if ($args{db_type} eq 'SQLite3') {
    $ENV{PATH}=":$ENV{PATH}";
    if ($mode eq 'dump') {
        dump_sqlite3(%args);
    }
    } elsif ($args{db_type} eq 'PostgreSQL') {
    $ENV{PATH}="/usr/bin:$ENV{PATH}";
    if ($mode eq 'dump') {
        dump_pgsql(%args);
    } else {
        analyse_pgsql(%args);
    }
    } elsif ($args{db_type} eq 'MySQL') {
    $ENV{PATH}=":$ENV{PATH}";
    if ($mode eq 'dump') {
        dump_mysql(%args);
    } else {
        analyse_mysql(%args);
    }
    } else {
    die "This database type isn't supported";
    }
}

open(FP, "$dir_conf -C '$cat'|") or die "Can't get catalog information $@";
# catalog=MyCatalog
# db_type=SQLite
# db_name=regress
# db_driver=
# db_user=regress
# db_password=
# db_address=
# db_port=0
# db_socket=
my %cfg;

while(my $l = <FP>)
{
    if ($l =~ /catalog=(.+)/) {
    if (exists $cfg{catalog} and $cfg{catalog} eq $cat) {
        exit handle_catalog($mode, %cfg);
    }
    %cfg = ();      # reset
    }

    if ($l =~ /(\w+)=(.+)/) {
    $cfg{$1}=$2;
    }
}

if (exists $cfg{catalog} and $cfg{catalog} eq $cat) {
    exit handle_catalog($mode, %cfg);
}

print "Can't find your catalog ($cat) in director configuration\n";
exit 1;
