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
&header($text{'list_users_title'},"images/icon.gif","list_users",1,undef,undef,undef);

# input
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};
my $searchstr = $in{'searchstr'};
my $searchparam = $in{'searchparam'};
my $order = (defined($in{'order'})) ? $in{'order'} : 'uid';
my $hidedisabled = ($config{'hide_disabled_users'} == 1) ? 1 : undef;

# initialise some variables
my $ldap = &LDAPInit();
#my $attrs = ['uid', 'uidNumber', 'cn', 'description', 'userPassword','ou'];
my $attrs = ['uid', 'uidNumber', 'cn', 'description','title', 'ou' , 'userPassword', 'mailAddress'];
my @searchattrs = ('uid', 'uidNumber', 'cn');
my $url = 'list_users.cgi';


print "<table><tr><td>";

# search form
$url .= "?base=".&urlize($base);
print "<h2>".$text{'list_users_search_users'}."</h2>\n";
print "<form action=$url&order=$order method=post>\n";
if ($searchstr) {
    print $text{'list_users_name'}.": <input type=text name=searchstr value=$searchstr><input type=submit name=search value=Go>\n";
} else {
    print $text{'list_users_name'}.": <input type=text name=searchstr><input type=submit name=search value=Go>\n";
}
print $text{'list_users_search_by'};
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
    print "<br><a href=$url&order=$order>".$text{'list_users_show_complete_list'}."</a>\n";
}

print "</td><td>\n";

# show OU
&printLDAPTree('list_users.cgi',$ldap, $config{'ldap_users_base'}, $base);
print "</td></tr></table>\n";

print "<hr>\n";

# add user link
print "<br><a href=add_user.cgi?base=".&urlize($base).">".$text{'list_users_add_user'}."</a>\n"; 
print "<hr>\n";

# users list
print "<h1>".$text{'list_users_title'}."</h1>\n";
my @users = ();
if ($in{'search'}) {
    my $result = &LDAPSearch($ldap, 
			     "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)($searchparam=$searchstr))", 
			     $attrs, 
			     $base);  
    @users = $result->entries;
    my $count = $result->count;
    if ($count == $config{'max_search_results'}) {
	print "<font color=green>".$text{'list_users_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    } else {
	print "<font color=green>".$text{'list_users_matching_users'}.": $count</font>\n";
    }
} else {
    my $result = &LDAPSearch($ldap, 
			     "objectClass=inetOrgPerson", 
			     $attrs, 
			     $base);  
    @users = $result->entries;
    if ($users[$config{'max_search_results'} - 1]) {
	print "<font color=green>".$text{'list_users_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    }
}

# columns headers
if ($in{'search'}) {
    $url .= "&search=Go&searchparam=$searchparam&searchstr=$searchstr";
}
print "<table width='100%'>\n";
print "<tr $cb>\n";
if ($order eq 'uid') {
    print "<td><a href=$url&order=uid><font color=blue><b>".$text{'list_users_name'}."</b></font></a></td>\n";
} else {    
    print "<td><a href=$url&order=uid><b>".$text{'list_users_name'}."</b></a></td>\n";
}
if (!$hidedisabled) {
    print "<td><b>".$text{'list_users_status'}."</b></td>\n";
}
if ($order eq 'uidNumber') {
   print "<td><a href=$url&order=uidNumber><font color=blue><b>".$text{'list_users_number'}."</b></font></a></td>\n";
} else {
    print "<td><a href=$url&order=uidNumber><b>".$text{'list_users_number'}."</b></a></td>\n";
}
#print "<td><b>".$text{'list_users_full_name'}."</b></td>\n";
if ($order eq 'cn') {
	print "<td><b>".$text{'list_users_full_name'}."</b></td>\n";
} else {
    print "<td><a href=$url&order=cn><b>".$text{'list_users_full_name'}."</b></a></td>\n";
}
if ($order eq 'title') {
	print "<td><b>".$text{'list_users_persontitle'}."</b></td>\n";
} else {
    print "<td><a href=$url&order=title><b>".$text{'list_users_persontitle'}."</b></a></td>\n";
}
if ($order eq 'ou') {
	print "<td><b>".$text{'list_users_personou'}."</b></td>\n";
} else {
    print "<td><a href=$url&order=ou><b>".$text{'list_users_personou'}."</b></a></td>\n";
}
print "<td><b>".$text{'list_users_description'}."</b></td>\n";
print "<td><b>".$text{'list_users_delete_user'}."</b></td></tr>\n"; 

# get users list
#my $ordered_users = {};
#foreach my $_user (@users) {
#    next if ($hidedisabled && &LDAPUserIsDisabled($ldap, $_user));    
#    my $_key =  &LDAPGetUserAttribute($ldap, $_user, $order); 
#    $ordered_users->{$_key} = $_user;
#}
#my @ordered_keys = ();
#if ($order eq 'uidNumber') {
#    @ordered_keys = sort {$a <=> $b} keys %$ordered_users;
#} else {
#    @ordered_keys = sort keys %$ordered_users;
#} 
#$url .= "&order=$order";
my @ordered_users ;
foreach my $_user (@users) {
    next if ($hidedisabled && &LDAPUserIsDisabled($ldap, $_user));    
    my $_key =  &LDAPGetUserAttribute($ldap, $_user, $order); 
    push(@ordered_users,[$_key,$_user]);
}
my @ordered_keys = ();
if ($order eq 'uidNumber') {
    @ordered_keys = sort {$a->[0] <=> $b->[0]} @ordered_users;
} else {
    @ordered_keys = sort {$a->[0] cmp $b->[0]} @ordered_users;
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
    my $user = $k->[1];
    #my $user = $ordered_users->{$k};
    my $isdisabled = &LDAPUserIsDisabled($ldap, $user);
    my $uid = &LDAPGetUserAttribute($ldap, $user, 'uid');
    print "<tr><td><table><tr><td><img src=images/mini_user.gif></td>\n";
    print "<td><a href=edit_user.cgi?uid=$uid&base=".&urlize($base).">$uid</a></td></tr></table></td>\n";
    if (!$hidedisabled) {
	if ($isdisabled) {
	    print "<td><font color=green>".$text{'list_users_disabled'}."</font></td>\n";
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
	print "<td>".$text{'list_users_not_found'}."</td>\n";
    }
    my $title = &LDAPGetUserAttribute($ldap, $user, 'title');
    if ($title) {
	print "<td>$title</td>\n";
    } else {
	print "<td>".$text{'list_users_not_found'}."</td>\n";
    }
    my $ou = &LDAPGetUserAttribute($ldap, $user, 'ou');
    if ($ou) {
	print "<td>$ou</td>\n";
    } else {
	print "<td>".$text{'list_users_not_found'}."</td>\n";
    }
    my $description = &LDAPGetUserAttribute($ldap, $user, 'description');
    if ($description) {
	print "<td>$description</td>\n";
    } else {
	print "<td>".$text{'list_users_not_found'}."</td>\n";
    }
    print "<td><a href=delete_user.cgi?uid=$uid&base=".&urlize($base).">".$text{'list_users_delete'}."</a></td></tr>\n";
}
print "</table>\n";
&LDAPClose($ldap);

# print pages links again
print $pages;

&footer('',$text{'index_return'});


