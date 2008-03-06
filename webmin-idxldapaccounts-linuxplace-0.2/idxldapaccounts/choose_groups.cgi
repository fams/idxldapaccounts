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
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_groups_base'};
my $searchstr = $in{'searchstr'};
my $searchparam = $in{'searchparam'};
my $order = defined($in{'order'}) ? $in{'order'} : 'cn';

# initialize some variables
my $ldap = &LDAPInit();
my $attrs = ['cn', 'gidNumber', 'description'];
my $url = "choose_groups.cgi?base=".&urlize($base);
if ($in{'multi'}) {
    $url .= "&multi=yes";
}
print "<table><tr><td>\n";

# search form
print "<h2>".$text{'choose_groups_search_groups'}."</h2>\n";
print "<form action=$url&order=$order method=post>\n";
if ($searchstr) {
    print $text{'choose_groups_name'}.": <input type=text name='searchstr' value=$searchstr><input type=submit name=search value=".$text{'choose_groups_go'}.">\n";
} else {
    print $text{'choose_groups_name'}.": <input type=text name='searchstr'><input type=submit name=search value=".$text{'choose_groups_go'}.">\n";
}
print "<br>".$text{'choose_groups_search_by'}." ";
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
    print "<br><a href=$url&order=$order>".$text{'choose_groups_show_complete_list'}."</a>\n";
}
print "</td><td>\n";
# print OUs
&printLDAPTree('choose_groups.cgi', $ldap, $config{'ldap_groups_base'}, $base);
print "</td></tr></table>\n";
print "<hr>\n";

# get groups list
print "<h1>".$text{'choose_groups_title'}."</h1>\n";
my @groups = ();
if ($in{'search'}) {
    my $result = &LDAPSearch($ldap, 
			     "(&(objectClass=posixGroup)($searchparam=$searchstr))", 
			     $attrs, 
			     $base);  
    @groups = $result->entries;
    my $count = $result->count;
    if ($count == $config{'max_search_results'}) {
	print "<font color=green>".$text{'choose_groups_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    } else {
	print "<font color=green>".$text{'choose_groups_matching_groups'}.": $count</font>\n";
    }
} else {
    my $result = &LDAPSearch($ldap, 
			     "(&(objectClass=posixGroup))", 
			     $attrs, 
			     $base);  
    @groups = $result->entries;
    my $count = $result->count;
    if ($count == $config{'max_search_results'}) {
	print "<font color=green>".$text{'choose_groups_found_more'}." (".$config{'max_search_results'}.")</font><br><br>\n";
    }
}

if ($in{'search'}) {
    $url .= "&search=Go&searchparam=$searchparam&searchstr=$searchstr&";
}

# print groups table
print "<table width='100%'>\n";
print "<tr $cb>\n";
if ($order eq 'cn') {
    print "<td><a href=$url&order=cn><font color=blue><b>".$text{'choose_groups_name'}."</b></font></a></td>\n";
} else {    
    print "<td><a href=$url&order=cn><b>".$text{'choose_groups_name'}."</b></a></td>\n";
}
if ($order eq 'gidNumber') {
   print "<td><a href=$url&order=gidNumber><font color=blue><b>".$text{'choose_groups_number'}."</b></font></a></td>\n";
} else {
    print "<td><a href=$url&order=gidNumber><b>".$text{'choose_groups_number'}."</b></a></td>\n";
}
print "<td><b>".$text{'choose_groups_full_name'}."</b></td>\n";
print "<td><b>".$text{'choose_groups_description'}."</b></td>\n";
print "</tr>\n";

my $ordered_groups = {};
foreach my $_group(@groups) {
    my $_key =  &LDAPGetGroupAttribute($ldap, $_group, $order); 
    $ordered_groups->{$_key} = $_group;
}
my @ordered_keys = ();
if ($order eq 'gidNumber') {
    @ordered_keys = sort {$a <=> $b} keys %$ordered_groups;
} else {
    @ordered_keys = sort keys %$ordered_groups;
} 
$url .= "&order=$order";

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
    print "<td>$cn</td></tr></table></td>\n";
    my $number = &LDAPGetGroupAttribute($ldap, $group, 'gidNumber');
    print "<td>$number</td>\n";
    my $cn = &LDAPGetGroupAttribute($ldap, $group, 'cn');
    if ($cn) {
	print "<td>$cn</td>\n";
    } else {
	print "<td>".$text{'choose_groups_not_found'}."</td>\n";
    }
    my $description = &LDAPGetGroupAttribute($ldap, $group, 'description');
    if ($description) {
	print "<td>$description</td>\n";
    } else {
	print "<td>".$text{'choose_groups_not_found'}."</td>\n";
    }
  if ($in{'multi'} ) {
            print "<td><form><input type=button value='".$text{'choose_groups_add'}."' onClick=\"opener.ifield.value+=' - $cn'\"></form></td>\n";
  } else {
      print "<td><form><input type=button value='".$text{'choose_groups_add'}."' onClick=\"opener.ifield.value='$cn'\"></form></td>\n";
  }
    print "</tr>\n";
}
print "</table>\n";
&LDAPClose($ldap);
print $pages;


