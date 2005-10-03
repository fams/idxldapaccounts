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
&header();

# input
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};
my $searchstr = $in{'searchstr'};
my $searchparam = $in{'searchparam'};
my $order = defined($in{'order'}) ? $in{'order'} : 'uid';

# initialize some variables
my $ldap = &LDAPInit();
my $attrs = ['uid', 'uidNumber', 'cn', 'description', 'userPassword'];
my @searchattrs = ('uid', 'uidNumber', 'cn');
my $url = "choose_users.cgi?base=".&urlize($base);
if ($in{'multi'}) {
    $url .= "&multi=yes";
}
my $hidedisabled = ($config{'hide_disabled_users'}) ? 1 : undef;
print "<table><tr><td>\n";



# search form
print "<h2>".$text{'choose_users_search_users'}."</h2>\n";
print "<form action=$url&order=$order method=post>\n";
if ($searchstr) {
    print $text{'choose_users_name'}.": <input type=text name='searchstr' value=$searchstr><input type=submit name=search value=".$text{'choose_users_go'}.">\n";
} else {
    print $text{'choose_users_name'}.": <input type=text name='searchstr'><input type=submit name=search value=".$text{'choose_users_go'}.">\n";
}
print "<br>".$text{'choose_users_search_by'}." ";
print "<select name=searchparam>\n";
foreach (@searchattrs) {
    if ($searchparam && $_ eq $searchparam) {
	print "<option value=$_ selected>$_";
    } else {
	print "<option value=$_>$_";
    }
}
print "</select>\n";
print "</form>\n";
if ($in{'search'}) {
    print "<br><a href=$url&order=$order>".$text{'choose_users_show_complete_list'}."</a>\n";
}
print "</td><td>\n";

# print OUs
&printLDAPTree('choose_users.cgi', $ldap, $config{'ldap_users_base'}, $base);

print "</td></tr></table>\n";
print "<hr>\n";

# get users list
print "<h1>".$text{'choose_users_title'}."</h1>\n";
my @users = ();
if ($in{'search'}) {
    my $result = &LDAPSearch($ldap, 
			     "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)($searchparam=$searchstr))", 
			     $attrs, 
			     $base);  
    @users = $result->entries;
    my $count = $result->count;
    if ($count == $config{'max_search_results'}) {
	print "<font color=green>".$text{'choose_users_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    } else {
	print "<font color=green>".$text{'choose_users_matching_users'}.": $count</font>\n";
    }
} else {
    my $result = &LDAPSearch($ldap, 
			     "(&(objectClass=inetOrgPerson)(objectClass=posixAccount))",
			     $attrs, 
			     $base);  
    @users = $result->entries;
    my $count = $result->count;
    if ($count == $config{'max_search_results'}) {
	print "<font color=green>".$text{'choose_users_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    }
}

# print users table
if ($in{'search'}) {
    $url .= "&search=Go&searchparam=$searchparam&searchstr=$searchstr&";
}
print "<table width='100%'>\n";
print "<tr $cb>\n";
if ($order eq 'uid') {
    print "<td><a href=$url&order=uid><font color=blue><b>".$text{'choose_users_name'}."</b></font></a></td>\n";
} else {    
    print "<td><a href=$url&order=uid><b>".$text{'choose_users_name'}."</b></a></td>\n";
}
 if (!$hidedisabled) {
     print "<td><b>".$text{'choose_users_status'}."</b></td>\n";
 }
			
if ($order eq 'uidNumber') {
   print "<td><a href=$url&order=uidNumber><font color=blue><b>".$text{'choose_users_number'}."</b></font></a></td>\n";
} else {
    print "<td><a href=$url&order=uidNumber><b>".$text{'choose_users_number'}."</b></a></td>\n";
}

$url .= "&order=$order";

print "<td><b>".$text{'choose_users_full_name'}."</b></td>\n";
print "<td><b>".$text{'choose_users_description'}."</b></td>\n";
print "</tr>\n";

my $ordered_users = {};
foreach my $_user (@users) {
    next if ($hidedisabled && &LDAPUserIsDisabled($ldap, $_user));    
    my $_key =  &LDAPGetUserAttribute($ldap, $_user, $order); 
    $ordered_users->{$_key} = $_user;
}
my @ordered_keys = ();
if ($order eq 'uidNumber') {
    @ordered_keys = sort {$a <=> $b} keys %$ordered_users;
} else {
    @ordered_keys = sort keys %$ordered_users;
} 
$url .= "&order=$order";

#build pages links
my $max = $config{'max_items'};
my $page =  defined($in{'page'}) ? $in{'page'} : 1;
my $pages = &pagesLinks($url, $#ordered_keys, $page);

#print pages links
print $pages;

# print users table
my @visible_keys = splice(@ordered_keys, ($page - 1) * $max, $max);
foreach my $k (@visible_keys) {
    my $user = $ordered_users->{$k};
    my $isdisabled = &LDAPUserIsDisabled($ldap, $user);
    my $uid = &LDAPGetUserAttribute($ldap, $user, 'uid');
    print "<tr><td><table><tr><td><img src=images/mini_user.gif></td>\n";
    print "<td>$uid</td></tr></table></td>\n";
    if (!$hidedisabled) {
	if ($isdisabled) {
	    print "<td><font color=green>".$text{'choose_users_disabled'}."</font></td>";
	} else {
	    print "<td></td>\n";
	}
    }
    my $number = &LDAPGetUserAttribute($ldap, $user, 'uidNumber');
    print "<td>$number</td>\n";
    my $cn = &LDAPGetUserAttribute($ldap, $user, 'cn');
    if ($cn) {
	print "<td>$cn</td>\n";
    } else {
	print "<td>".$text{'choose_users_not_found'}."</td>\n";
    }
    my $description = &LDAPGetUserAttribute($ldap, $user, 'description');
    if ($description) {
	print "<td>$description</td>\n";
    } else {
	print "<td>".$text{'choose_users_not_found'}."</td>\n";
    }
    if ($in{'multi'}) {
	print "<td><form><input type=button value='".$text{'choose_users_add'}."' onClick=\"opener.ifield.value+=' - $uid'\"></form></td>\n";
    } else {
	print "<td><form><input type=button value='".$text{'choose_users_add'}."' onClick=\"opener.ifield.value='$uid'\"></form></td>\n";
    }
    print "</tr>\n";
}
print "</table>\n";
&LDAPClose($ldap);

# print pages links
print $pages;


