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
$access{'configure_virtual'} or &error($text{'acl_configure_virtual_msg'});
&header($text{'list_virtual_title'},"images/icon.gif","list_virtual",1,undef,undef);

print "<h1>".$text{'list_virtual_domains'}."</h1>\n";

my $ldap = &LDAPInit();
#recuperando domínios virtuais
my $entry = &LDAPGetVirtuals($ldap);
#print "<script>alert('".$entry->attributes(0)."');</script>";
print "<form action='edit_virtual.cgi' method='post'>\n";
print "<table width='100%'>\n";
print "<tr $cb><td><b>".$text{'list_virtual_domain_name'}."</b></td><td></td></tr>\n";
foreach my $domain ($entry->get_value('associatedDomain')) {
    print "<tr><td><a href=edit_virtual.cgi?action=edit&virtual=$domain>$domain</a><td><a href=edit_virtual.cgi?action=delete&virtual=$domain>$text{'delete'}</a></td>\n";
}
print "</table>\n"; 
print "<input type=submit value='".$text{'list_virtual_add'}."' name=submit>\n"; 
print "<input type=hidden value=new name=action>\n"; 
print "</form>\n"; 

&LDAPClose($ldap);
&footer('',$text{'index_return'});
