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
&header($text{'list_groups_title'},"images/icon.gif",undef,1,undef,undef,undef);

# input
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_groups_base'};
my $searchstr = $in{'searchstr'};
my $searchparam = $in{'searchparam'};
my $order = (defined($in{'order'})) ? $in{'order'} : 'cn';

# initialize some variables
my $ldap = &LDAPInit();
my $attrs = ['cn', 'gidNumber', 'description'];
my $url = "list_groups.cgi";

print "<table><tr><td>\n";

# search form
$url .= "?base=".&urlize($base);
print "<h2>".$text{'list_groups_search_groups'}."</h2>\n";
print "<form action=$url&order=$order method=post>\n";
if ($searchstr) {
    print $text{'list_groups_name'}.": <input type=text name=searchstr value=$searchstr><input type=submit name=search value=Go>\n";
} else {
    print $text{'list_groups_name'}.": <input type=text name=searchstr><input type=submit name=search value=Go>\n";
}
print $text{'list_groups_search_by'};
print "<select name=searchparam>\n";
foreach (@$attrs) {
    if ($searchparam && $_ eq $searchparam) {
	print "<option value=$_ selected>$_";
    } else {
	print "<option value=$_>$_";
    }
}
print "</select>\n";
print "</form>\n";
if ($in{'search'}) {
    print "<br><a href=$url&order=$order>".$text{'list_groups_show_complete_list'}."</a>\n";
}

print "</td><td>\n";

# show OUs
&printLDAPTree('list_groups.cgi',$ldap, $config{'ldap_groups_base'}, $base);

print "</td></tr></table>\n";
print "<hr>\n";

# add group link
print "<br><a href=add_group.cgi?base=".&urlize($base).">".$text{'list_groups_add_group'}."</a><br>\n"; 
print "<hr>\n";

# groups list
print "<h1>".$text{'list_groups_title'}."</h1>\n";
my @groups = ();
if ($in{'search'}) {
    my $result = &LDAPSearch($ldap, 
			     "(&(objectClass=posixGroup)($searchparam=$searchstr))", 
			     $attrs, 
			     $base);  
    @groups = $result->entries;
    my $count = $result->count;
    if ($count == $config{'max_search_results'}) {
	print "<font color=green>".$text{'list_groups_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    } else {
	print "<font color=green>".$text{'list_groups_matching_groups'}.": $count</font>\n";
    }
} else {
    @groups = &LDAPGetGroups($ldap, $attrs);
    if ($groups[$config{'max_search_results'} - 1]) {
	print "<font color=green>".$text{'list_groups_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    }
}

if ($in{'search'}) {
    $url .= "&search=Go&searchparam=$searchparam&searchstr=$searchstr&";
}

# columns headers
print "<table width='100%'>\n";
print "<tr $cb>\n";
if ($order eq 'cn') {
    print "<td><a href=$url&order=cn><font color=blue><b>".$text{'list_groups_name'}."</b></font></a></td>\n";
} else {
    print "<td><a href=$url&order=cn><b>".$text{'list_groups_name'}."</b></a></td>\n";
}
if ($order eq 'gidNumber') {
    print "<td><a href=$url&order=gidNumber><font color=blue><b>".$text{'list_groups_number'}."</b></font></a></td>\n";
} else {
    print "<td><a href=$url&order=gidNumber><b>".$text{'list_groups_number'}."</b></a></td>\n";
}
print "<td><b>".$text{'list_groups_description'}."</b></td>\n";
print "<td><b>".$text{'list_groups_delete_group'}."</b></td></tr>\n"; 

# get groups list
my $ordered_groups = {};
foreach my $_group (@groups) {
    my $_key = &LDAPGetGroupAttribute($ldap, $_group, $order);    
    $ordered_groups->{$_key} = $_group;
}
my @ordered_keys = ();
if ($order eq 'gidNumber') {
    @ordered_keys = sort {$a <=> $b} keys %$ordered_groups;
} else {
    @ordered_keys = sort keys %$ordered_groups;
} 
$url .=	"&order=$order";

#build pages links
my $max = $config{'max_items'};
my $page =  defined($in{'page'}) ? $in{'page'} : 1;
my $pages = &pagesLinks($url, $#ordered_keys, $page);

#print pages links
print $pages;

# print groups table
my @visible_keys = splice(@ordered_keys, ($page - 1) * $max, $max);
foreach my $k (@visible_keys) {
    my $group = $ordered_groups->{$k};
    my $cn = &LDAPGetGroupAttribute($ldap, $group, 'cn');
    print "<tr><td><table><tr><td><img src=images/mini_group.gif></td>\n";
    print "<td><a href=edit_group.cgi?&base=".&urlize($base)."&cn=".&urlize($cn).">$cn</a></td></tr></table></td>\n";
    my $number = &LDAPGetGroupAttribute($ldap, $group, 'gidNumber');
    print "<td>$number</td>\n";
    my $description = &LDAPGetGroupAttribute($ldap, $group, 'description');
    if ($description) {
	print "<td>$description</td>\n";
    } else {
	print "<td>".$text{'list_groups_not_found'}."</td>\n";
    }
    print "<td><a href=delete_group.cgi?&base=".&urlize($base)."&cn=".&urlize($cn).">".$text{'list_groups_delete'}."</a></td></tr>\n";
}
print "</table>\n";
&LDAPClose($ldap);

# print pages links again
print $pages;

&footer('',$text{'index_return'});



