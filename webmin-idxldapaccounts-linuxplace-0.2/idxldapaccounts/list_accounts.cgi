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
&header($text{'list_accounts_title'},"images/icon.gif","list_accounts",1,undef,undef,undef);

print "<h1>".$text{'list_accounts_types'}."</h1>\n";

my $conf = &parseConfig("accounts.conf");
my $ldap = &LDAPInit();

print "<form action='save_accounts.cgi' method='post'>\n";
print "<table width='100%'>\n";
print "<tr $cb><td><b>".$text{'list_accounts_account'}."</b></td><td><b>".$text{'list_accounts_enabled'}."</b></td></tr>\n";
foreach my $o (keys %$conf) {
    my $account = ($o =~ /^\!(.*)/) ? $1 : $o;
    my $name = $text{$account};
    print "<tr><td><a href=edit_account.cgi?account=$o>$name</a></td>\n";
    my $checked = ($o =~/^\!/) ? '' : 'checked';
    print "<td><input type=checkbox name=visible_$account $checked></td></tr>\n";
}
print "</table>\n"; 
print "<input type=submit value=".$text{'list_accounts_apply'}." name=accounts>\n"; 
print "</form>\n"; 

&LDAPClose($ldap);
&footer('',$text{'index_return'});
