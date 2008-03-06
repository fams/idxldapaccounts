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
$access{'create_user'} or &error($text{'acl_create_user_msg'});
&header($text{'add_user_create_user'},"images/icon.gif","add_user",1,undef,undef);

# input
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};

# initialize some variables
my $ldap = &LDAPInit();
my $min_uid = &pickUid($ldap);
    
print "<table><tr><td><img src=images/user.gif></td><td><h1>".$text{'add_user_new_user'}."</h1></td></tr></table>\n";
print "<hr>\n";
print "<form action=edit_user.cgi method=post>\n";
print "<table width='80%'>\n";
print "<tr><td><b>".$text{'add_user_organization'}.": </b></td><td><select name=base>\n";
my @OUs = &LDAPGetOUs($ldap, $config{'ldap_users_base'});
foreach my $ou (@OUs) {
    my $dn = $ou->dn;
    if ($dn eq $base) {
	print "<option selected>$dn\n";
    } else {
	print "<option >$dn\n";
    }
}
print "</select></td></tr>\n";    
print "<tr><td><b>".$text{'add_user_user_id'}.": </b></td><td><input type=text name=uid></td></tr>\n";
print "<tr><td><b>".$text{'add_user_full_name'}.": </b></td><td><input type=text name=cn></td></tr>\n";
print "<tr><td><b>".$text{'add_user_last_name'}.": </b></td><td><input type=text name=sn></td></tr>\n";
print "<tr><td><b>".$text{'add_user_persontitle'}.": </b></td><td><input type=text name=title></td></tr>\n";
print "<tr><td><b>".$text{'add_user_personou'}.": </b></td><td><input type=text name=ou></td></tr>\n";
print "<tr><td><b>".$text{'add_user_description'}.": </b></td><td><input type=text name=description></td></tr>\n";
print "<tr><td><b>".$text{'add_user_password'}.": </b></td><td><input type=password name=userPassword></td></tr>\n";
print "<tr><td><b>".$text{'add_user_retype_password'}.": </b></td><td><input type=password name=retypeuserPassword></td></tr>\n";
print "<tr><td><b>".$text{'add_user_uid_number'}.": </b></td><td><input type=text name=uidNumber value=$min_uid></td></tr>\n";
print "<tr><td><b>".$text{'add_user_primary_group'}.": </b></td><td>\n";
print "<input type=text name=primaryGroup value='".$config{'gid_default'}."'>\n";
print "<input type=button onClick='ifield = document.forms[0].primaryGroup; chooser = window.open(\"choose_groups.cgi\", \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,width=500,height=400\"); chooser.ifield = ifield' value=\"".$text{'add_user_select'}."\"></td></tr>\n";
print "</table>";

print "<br><br><input type=submit name=create value='".$text{'add_user_create_user'}."'>\n";
print "</form>\n";

&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base), $text{'list_users_return'});



