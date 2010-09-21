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
$access{'configure_discussao'} or &error($text{'acl_configure_discussao_msg'});
&header($text{'list_discussao_title'},"images/discussao.gif","list_discussao",1,undef,undef);

print "<h1>".$text{'list_discussao_lists'}."</h1>\n";

my $ldap = &LDAPInit();
my $attrs = ['uid', 'mail', 'cn'];
my $base = $config{'ldap_discussao_base'};

print "<table width='100%'>\n";
print "<tr $cb>\n";
print "<td><b>".$text{'list_discussao_name'}."</b></td>\n";
print "<td><b>".$text{'list_discussao_email'}."</b></td>\n";
print "<td><b>".$text{'list_discussao_delete'}."</b></td>\n";
#print "</table>\n";

my @listas = ();
my $result = &LDAPSearch($ldap,
	"(&(objectClass=top)(objectClass=qmailUser))",
	$attrs,
	$base);
@listas = $result->entries;



#recuperando domínios virtuais
#my $entry = &LDAPGetDiscussao($ldap);
#print "<script>alert('".$entry->attributes(mail)."');</script>";
#print "<form action='edit_discussao.cgi' method='post'>\n";
#print "<table width='100%'>\n";
#print "<tr $cb><td><b>".$text{'list_discussao_name'}."</b></td><td></td></tr>\n";
foreach my $_list (@listas) {
    my $_listuid=$_list->get_value('uid');
    my $_listname=$_list->get_value('cn');
    my $_listmail=$_list->get_value('mail');
    $_listuid =~ s/[^a-zA-Z\.\-]//; 
    print "<tr><td><a href=\"edit_discussao.cgi?action=edit&listuid=$_listuid\">$_listname</a></td><td>$_listmail</td><td><a href=\"edit_discussao.cgi?action=delete&listuid=$_listuid\">$text{'delete'}</a></td>\n";
}
print "</table>\n"; 
print "<form action='edit_discussao.cgi' method='post'>\n";
print "<input type=submit value='".$text{'list_discussao_add'}."' name=submit>\n"; 
print "<input type=hidden value=new name=action>\n"; 
print "</form><BR>\n"; 

#print "</table>\n";

&LDAPClose($ldap);
&footer('',$text{'index_return'});
