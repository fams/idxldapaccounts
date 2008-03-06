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
$access{'create_group'} or &error($text{'acl_create_group_msg'});
&header($text{'add_group_create_group'},"images/icon.gif","add_group",1,undef,undef);

# input
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_groups_base'};

# initialize some variables
my $ldap = &LDAPInit();
my $min_gid = &pickGid($ldap);

print "<table><tr><td><img src=images/group.gif></td>
<td><h1>".$text{'add_group_new_group'}."</h1></td></tr></table>\n";
print "<hr>\n";
print "<form action=edit_group.cgi?base=".&urlize($base)." method=post>\n";
print "<table width='80%'>\n";
print "<tr><td><b>".$text{'add_group_organization'}.": </b></td><td><select name=base>\n";
my @OUs = &LDAPGetOUs($ldap, $config{'ldap_groups_base'});
foreach my $ou (@OUs) {
    my $dn = $ou->dn;
    if ($dn eq $base) {
	print "<option selected>$dn\n";
    } else {
	print "<option >$dn\n";
    }
}
print "</select></td></tr>\n";    
print "<tr><td><b>".$text{'add_group_name'}.": </b></td><td><input type=text name=cn></td></tr>\n";
print "<tr><td><b>".$text{'add_group_gid_number'}.": </b></td>
<td><input type=text name=gidNumber value='$min_gid'></td></tr>\n";
print "<tr><td><b>Description: </b></td>
<td><input type=text name=description value='$value'></td></tr>\n";
print "</table>\n";
print "<br><br><input type=submit name=create value='".$text{'add_group_create_group'}."'>\n";

print "</form>\n";
&footer("list_groups.cgi?base=".&urlize($base),$text{'list_groups_return'});


