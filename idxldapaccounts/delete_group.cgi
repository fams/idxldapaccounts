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
$access{'delete_group'} or &error($text{'acl_delete_group_msg'});
&header($text{'delete_group_title'},"images/icon.gif",undef,1,undef,undef,undef);

# input 
my $group_cn = $in{'cn'};
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_groups_base'};

# initialize some variables
my $ldap = &LDAPInit();
my $url = "delete_group.cgi?base=".&urlize($base)."&cn=".&urlize($group_cn);

if ($in{'confirm'}) {
    &webmin_log("deleting group [$group_cn]");
    &LDAPDeleteGroup($ldap, $group_cn);
    print "<br>".$text{'delete_group_group_successfully_deleted'}.": $group_cn.<br>";
} else {
    my $primary = undef;
    my @users = &LDAPGetUsers($ldap);
    foreach (@users) {
	if (&userPrimaryGroup($ldap, $_, $group_cn)) {
	    $primary = 1;
	}
    }
    if ($primary) {
	&error($text{'err_some_users_have_this_group_as_primary'});
	    } else {
		print "<form action=$url method=post>";
		print $text{'delete_group_about_to_delete_group'}." $group_cn, 
".$text{'delete_group_are_you_sure'}."<br>";
		print "<input type=submit name=confirm value=".$text{'delete_group_confirm'}.">";
	    }
}
&LDAPClose($ldap);
&footer("list_groups.cgi?base=".&urlize($base),$text{'list_groups_return'});
