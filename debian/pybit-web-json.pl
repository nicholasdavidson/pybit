#!/usr/bin/perl

use strict;
use warnings;
use JSON;
use vars qw/ $command $ret $dbuser $dbpass $cfgfile %cfg $ret
 $basepath $dbname $dbserver $dbport $dbtype $dbexport $dh_commands
 @json_list $json_text $fh $json_hash %dbhash $json $dbini /;
# postinst helper script for pybit-web
$cfgfile   = '/etc/pybit/web/web.conf';
$dbexport  = '/etc/pybit/debian-db.pl'; # contains the intermediate db export data
$dbini     = '/etc/pybit/debian-db.ini'; # other debconf data
# pull in the exported db data
if (-f $dbexport) {
	require $dbexport;
}
# extract the ordinary debconf data
if (-f $dbini) {
	open (INI, $dbini);
	my @ini=<INI>;
	close (INI);
	unlink $dbini;
	foreach my $line (@ini) {
		my @set = split(/=/, $line);
		$cfg{$set[0]} = $set[1];
	}
}
if (not defined $cfg{'host'}) {
	my $host = `hostname -f`;
	chomp ($host);
	$cfg{'host'} = $host;
}
if (not defined $cfg{'port'}) {
	$cfg{'port'} = 8080;
}
foreach my $key (keys %cfg) {
	my $val = $cfg{$key};
	chomp($val);
	$val =~ s/"//g;
	$val =~ s/'//g;
	$val =~ s/,//g;
	$cfg{$key} = $val;
}
if (-r "$cfgfile") {
	open(CONF, "$cfgfile") or die;
} else {
	open(CONF, "/usr/share/pybit-web/web.conf") or die;
}
@json_list = <CONF>;
close (CONF);
$json = new JSON;
$json = $json->utf8(1);
$json = $json->pretty(1);
$json = $json->canonical(1);
$json_text = join(' ', @json_list);
$json_hash = $json->decode($json_text);
$$json_hash{'db'}{'hostname'} = $dbserver if (defined $dbserver);
$$json_hash{'db'}{'databasename'} = $dbname if (defined $dbname);
if (defined $dbport) {
	$dbport = 0 if ($dbport eq "");
	if (int $dbport == 0) {
		$$json_hash{'db'}{'port'} = undef;
	} else {
		$$json_hash{'db'}{'port'} = int $dbport == 0;
	}
}
$$json_hash{'db'}{'user'} = $dbuser if (defined $dbuser);
$$json_hash{'db'}{'password'} = $dbpass if (defined $dbpass);
$$json_hash{'web'}{'hostname'} = $cfg{'host'};
$$json_hash{'web'}{'port'} = int $cfg{'port'};
$$json_hash{'controller'}{'rabbit_url'} = $cfg{'rabbit'}.":5672";
$$json_hash{'debconf'} = JSON::true;
open (CONF, ">$cfgfile") or die;
print CONF $json->encode ($json_hash);
close (CONF);
chmod (0440, $cfgfile);
my ($name, $passwd, $uid, $gid, $quota, $comment, $gcos, $dir, $shell) = getpwnam($dbname);
if (defined $uid and $uid > 1) {
	chown ($uid, -1, $cfgfile);
}
exit 0;
