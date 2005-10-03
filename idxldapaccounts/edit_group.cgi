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
my %access = &get_module_acl();
$access{'view_group'} or &error($text{'acl_view_group_msg'});
&ReadParse();


# input
my $group_cn = $in{'cn'};
my $base = (defined($in{'base'})) ? $in{'base'} : $config{'ldap_groups_base'};
my $base = $config{'ldap_groups_base'};
    #&error($in{'base'});
my $onglet = (defined($in{'onglet'})) ? $in{'onglet'} : $text{'edit_group_general'};


# initialize some variables
my $ldap = &LDAPInit();
my $conf = &parseConfig('accounts.conf');
my $creation = '';
my $url = 'edit_group.cgi?base='.&urlize($base);

# check out actions to perform
if ($in{'create'}) {
    $access{'create_group'} or &error($text{'acl_create_group_msg'});
    my $dn = "cn=$group_cn,$base";
    &checkGid($ldap, $in{'gidNumber'});
    my @attrs = ();
    foreach $k (keys %in) {
		next if ($k =~ /(cat|create|change|onglet|base)/);
		next if $in{$k} =~ /^\s*$/;
		push (@attrs, $k);
		push (@attrs, utf8Encode($in{$k}));
    }
    push (@attrs, 'objectClass');
    push (@attrs, ['posixGroup']);
    &LDAPAddGroup($ldap, $dn, \@attrs);
    &webmin_log("creating group [$dn]", undef, undef,\%in);
    $creation = "<font color=green>".$text{'edit_group_group_successfully_created'}."</font></br>\n";
}
my $attrs = [];
my $result = &LDAPSearch($ldap,
						 "(&(objectClass=posixGroup)(cn=$group_cn))",
						 $attrs,
						 $base);
if ($result->count > 1) {
    &error($text{'err_found_more_than_one_group'});
}
my $group = $result->entry;
if (!$group) {
	&error($text{'err_could_not_find_group'}." $group_cn");
}
if ($in{'change'}) {
    $access{'edit_group'} or &error($text{'acl_edit_group_msg'});
    my %attrs = ();
    foreach $k (keys %in) {
		next if ($k =~ /(cat|uid|create|change|onglet|base)/);
		$attrs{$k} = $in{$k};
    }
    &webmin_log("modifying group [$group_cn]", undef, undef,\%attrs);
    &LDAPModifyGroup($ldap, $group_cn, \%attrs);
}
if ($in{'addmember'}) {
    $access{'edit_group'} or &error($text{'acl_edit_group_msg'});
    &LDAPGroupAddMember($ldap, $group, $in{'member'});
    &webmin_log("adding member [".$in{'member'}."] to group [$group_cn]", undef, undef,\%in);
}
if ($in{'members'}) {
    $access{'edit_group'} or &error($text{'acl_edit_group_msg'});
    my @new_members = split(' - ', $in{'members'});
    foreach $m (@new_members) {
		if ($m =~ /[\w]+/) {
			&LDAPGroupAddMember($ldap, $group, $m);
			&webmin_log("adding member [$m] to group [$group_cn]", undef, undef,\%in);
		}
    }
}
if ($in{'removemember'}) {
    $access{'edit_group'} or &error($text{'acl_edit_group_msg'});
    &LDAPGroupRemoveMember($ldap, $group, $in{'removemember'});
    &webmin_log("removing member [".$in{'removemember'}."] from group [$group_cn]", undef, undef,\%in);
}

#refresh LDAP entry after possible modifications
$result = &LDAPSearch($ldap,
					  "(&(objectClass=posixGroup)(cn=$group_cn))",
					  $attrs,
					  $base);
if ($result->count > 1) {
    &error($text{'err_found_more_than_one_group'});
}
$group = $result->entry;
if (!$group) {
	&error($text{'err_could_not_find_group'}." $group_cn");
}

&header($group_cn,"images/icon.gif","edit_group",1,undef,undef);
print "<script language=\"javascript\">var ifield;</script>";

$url .= "&cn=".&urlize($group_cn);
#
# menu
#
my @onglets = ($text{'edit_group_general'}, "$text{'edit_group_members'}");
print "<table><tr>\n";
foreach (@onglets) {
    if ($_ eq $onglet) {
		print "<td><b><font color=blue>$_</font></b></td>\n";
    } else {
		print "<td><b><a href=$url&onglet=$_>$_</a></b></td>\n";
    }
}
print "</tr></table>\n";
print "<br>\n";
print "<table><tr><td><img src=images/group.gif></td>\n";
print "<td><h1>$group_cn</h1></td><td>$creation</td>\n";
print "<td><a href=delete_group.cgi?cn=".&urlize($group_cn)."&base=".&urlize($base).">".$text{'edit_group_delete_group'}."</a></td>\n";
print "</tr></table>\n";
print "<hr>\n";

$url .= "&onglet=$onglet";
#
# general
#
if ($onglet eq $text{'edit_group_general'}) {
    print "<form action=$url method=post>\n";
    print "<table width='80%'>\n";
    my $ou = utf8Decode($group->dn);
    $ou =~ s/cn=$group_cn,//g;
    print "<tr><td><b>".$text{'edit_group_organization'}.": </b></td><td>$ou</td></tr>\n";
    my $gidnumber = &LDAPGetGroupAttribute($ldap, $group, 'gidnumber');
    print "<tr><td><b>".$text{'edit_group_gid_number'}.": </b></td><td>$gidnumber</td></tr>\n";
    my $description = &LDAPGetGroupAttribute($ldap, $group, 'description');
    if ($description) {
		$value=$description;
	} else {
		$value='';
	}
    print "<tr><td><b>".$text{'edit_group_description'}.": </b></td><td><input type=text name=description value='$value'></td></tr>\n";
    print "</table>\n";
    print "<br><br><input type=submit name=change value='".$text{'edit_group_apply_changes'}."'>\n";
    print "</form>\n";
}

#
# members
#
if ($onglet eq $text{'edit_group_members'}) {
    my @users = &LDAPGetUsers($ldap);
    if ($#users > 10) {
		print "<form action=$url method=post>\n";
		print "<input type=submit name=multi value='".$text{'edit_group_add_selected_members'}."'>\n";
		print "<table><tr><td><textarea wrap=auto name=members rows=5 cols=25></textarea></td>\n";
		print "<td valign=top><input type=button onClick='ifield = ifield = document.forms[0].members; chooser = window.open(\"choose_users.cgi?multi=yes\", \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=400\")' value=\"".$text{'edit_group_select_members'}."\"></td></tr><br>\n";
		print "</table>\n";
		print "</form>\n";
    } else {
		print "<form action=$url method=post>\n";
		print "".$text{'edit_group_add_member_to_this_group'}.": <select name=member>\n";
		my @names = ();
		foreach (@users) {
			my $name = &LDAPGetUserAttribute($ldap, $_, 'uid');
			push(@names, $name);
		}
		foreach (sort @names) {
			print "<option>$_";
		}
		print "</select>\n";
		print "<input type=submit name=addmember value='".$text{'edit_group_add_member'}."'>\n"; 
		print "</form>\n";
    }
    my %primaries = ();
    foreach (@users) {
		if (&userPrimaryGroup($ldap, $_, $group_cn)) {
			my $uid = &LDAPGetUserAttribute($ldap, $_, 'uid');
			$primaries{$uid} = 'yes';
		}
    }


    my @members = &LDAPGetGroupAttributes($ldap, $group, 'memberuid');
    @members = sort(@members);
    print "<table width='80%'>\n";
    print "<tr $cb><td><b>".$text{'edit_group_member'}."</b></td><td><b>".$text{'edit_group_remove_member_from_this_group'}."</b></td></tr>\n";
    
    #build pages links
    my $max = $config{'max_items'};
    my $page =  defined($in{'page'}) ? $in{'page'} : 1;
    my $pages = &pagesLinks($url, $#members, $page);
    
    #print pages links
    print $pages;

    my @visible_keys = splice(@members, ($page - 1) * $max, $max);
    foreach (@visible_keys) {
		print "<tr><td><table><tr><td><img src=images/mini_user.gif></td>\n";
		print "<td><a href=edit_user.cgi?uid=$_>$_</a></td></tr></table></td>\n";
		if ($primaries{$_}) {
	    	print "<td><font color=green>".$text{'edit_group_primary'}."</font></td></tr>\n";
	    } else {
			print "<td><a href=$url&removemember=$_>".$text{'edit_group_remove'}."</a></td></tr>\n";
	    }
    }
    print "</table>\n";

    #print pages links
    print $pages;

}
&LDAPClose($ldap);
&footer("list_groups.cgi?base=".&urlize($base), $text{'list_groups_return'});










