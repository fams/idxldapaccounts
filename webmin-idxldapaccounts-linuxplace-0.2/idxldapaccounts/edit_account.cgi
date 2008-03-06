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
&header($text{'edit_account_title'},"images/icon.gif","edit_account",1,undef,undef,undef);


my $account = $in{'account'};
my $name = ($account =~ /^\!(.*)/) ? $1 : $account;
print "<h1>".$text{$account}."</h1>";

my $conf = &parseConfig("accounts.conf");
my $ldap = LDAPInit();
#my @Attrs = &LDAPGetObjectClasseAttributes($ldap, $account);

print "<form action='save_accounts.cgi' method='post'>";
print "<table with='100%'>";
print "<tr $cb><td><b>".$text{'edit_account_attribute'}."</b></td><td><b>".$text{'edit_account_visible'}."</b></td><td><b>".$text{'edit_account_editable'}."</b></td><td><b>".$text{'edit_account_default'}."</b></td></tr>";
if (defined($conf->{$account})) {
        foreach my $attr (sort (keys %{$conf->{$account}})) {
	    print "<tr><td>$attr</td>";
	    my $checked = ($conf->{$account}->{$attr}->{'visible'} == 1) ? 'checked' : ''; 
	    print "<td><input type=checkbox name=visible_$attr $checked></td>";
	    my $default = $conf->{$account}->{$attr}->{'default'};
	    if ($conf->{$account}->{$attr}->{'forbidden'}) {
		print "<td><font color=red>".$text{'edit_account_forbidden'}."</font></td>";
		print "<td>$default</td>\n";
	    } else {
		$checked = ($conf->{$account}->{$attr}->{'editable'} == '1') ? 'checked' : ''; 
		print "<td><input type=checkbox name=editable_$attr $checked></td>";
		print "<td><input type=text name=default_$attr value=$default></td>";
	    }
	    print "</tr>\n";
    }
} else {
    foreach (@Attrs) {
	print "<tr><td>$_</td>";
	print "<td><input type=checkbox name=visible_$_ checked></td>";
	print "<td><input type=checkbox name=editable_$_ checked></td>";
	print "<td><input type=text name=default_$_></td>";
    }
}
print "</table>";
print "<input type=hidden name=account value=$account>";
print "<input type=submit value='".$text{'edit_account_apply'}."'>";
print "</form>";

&LDAPClose($ldap)
&footer('list_accounts.cgi',$text{'list_accounts_return'});

