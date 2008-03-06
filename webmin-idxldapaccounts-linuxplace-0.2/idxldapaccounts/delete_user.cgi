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
$access{'delete_user'} or &error($text{'acl_delete_user_msg'});
&header($text{'delete_user_title'},"images/icon.gif",undef,1,undef,undef,undef);

# input
my $user_uid = $in{'uid'};
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};

#initialize some variables
my $ldap = &LDAPInit();
my $url = "delete_user.cgi?base=".&urlize($base)."&uid=$user_uid";

if ($in{'confirm'}) {
    my @groups = &LDAPGetUserGroups($ldap, $user_uid);
    foreach (@groups) {
	&webmin_log("removing user [$user_uid] from group [$_]");
	&LDAPUserRemoveGroup($ldap, $user_uid, $_);
    }
    &LDAPDeleteUser($ldap, $base, $user_uid);
    &webmin_log("deleting user [$user_uid] from [$base]");
    print "<br>".$text{'delete_user_user_successfully_deleted'}.": $user_uid<br>";
} else {
    print "<form action=$url method=post>";
    print "".$text{'delete_user_about_to_delete_user'}." $user_uid, ".$text{'delete_user_are_you_sure'}."<br>";
    print "<input type=submit name=confirm value=".$text{'delete_user_confirm'}.">";
}
&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base),'users list');
