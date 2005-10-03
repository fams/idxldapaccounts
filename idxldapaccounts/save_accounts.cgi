#!/usr/bin/perl


#  This code was developped by IDEALX (http://IDEALX.org/) and
#  contributors (their names can be found in the CONTRIBUTORS file).
#
#                 Copyright (C) 2002 IDEALX
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
#  USA.

# author: <gerald.macinenti@IDEALX.com>
# Version: $Id$

require './idxldapaccounts-lib.pl';

&ReadParse();
my %access = &get_module_acl();
$access{'configure_account'} or &error($text{'acl_configure_account_msg'});
&header($text{'save_accounts_title'},"images/icon.gif",undef,1,1,undef,undef);


my $old_conf = &parseConfig("accounts.conf");
my $conf = {};
my $ldap = &LDAPInit();

if ($in{'accounts'}) {
    foreach my $o (keys %$old_conf) {
	if ($o =~ /^\!(.*)/) {
	    if ($in{"visible_$1"}) {
		$conf->{$1}  = $old_conf->{$o};
	    } else {
		$conf->{$o} = $old_conf->{$o};
	    }
	} else {
	    if ($in{"visible_$o"}) {
		$conf->{$o}  = $old_conf->{$o};
	    } else {
		$conf->{"\!$o"} = $old_conf->{$o};
	    }
	}
    }
    &webmin_log("modifying account types configuration",undef, undef,\%in);
} else {
    my $account=$in{'account'};
    foreach my $o (keys %$old_conf) {
	if ($o ne $account) {
	    if (defined($old_conf->{$o})) { $conf->{$o} = $old_conf->{$o} };
	} else {
	    $conf->{$o} = {};
	    foreach my $a (keys %{$old_conf->{$o}}) {
		if ($old_conf->{$o}->{$a}->{'forbidden'}) {
		    $conf->{$o}->{$a} = $old_conf->{$o}->{$a};
		    $conf->{$o}->{$a}->{'visible'} = ($in{"visible_$a"}) ? '1' : '0';
		    next;
		}
		$conf->{$o}->{$a} = {};
		$conf->{$o}->{$a}->{'visible'} = ($in{"visible_$a"}) ? '1' : '0';
		$conf->{$o}->{$a}->{'editable'} = ($in{"editable_$a"}) ? '1' : '0';
		$conf->{$o}->{$a}->{'default'} = ($in{"default_$a"}) ? $in{"default_$a"} : '';
	    }
	}
    }
    &webmin_log("modifying configuration for account [".$in{'account'}."]",undef, undef,\%in);
}


&writeConfig($conf);
&LDAPClose($ldap);    

print "<p><h2>".$text{'save_accounts_successfully_saved'}."</h2><br><br>";
&footer('list_accounts.cgi',$text{'list_accounts_return'});
