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
$access{'view_user_tech'} or &error($text{'acl_view_user_tech_msg'});
&ReadParse();

#input
my $user_uid = $in{'uid'};
my $base = (defined($in{'base'})) ? $in{'base'} : $config{'ldap_users_base'};
my $onglet = (defined($in{'onglet'})) ? $in{'onglet'} : 'General';

# initialize some variables
my $ldap = &LDAPInit();
my $conf = &parseConfig('accounts.conf');
my $creation = '';
my $url = 'edit_user.cgi?base='.&urlize($base);

# check out actions to perform
if ($in{'create'}) {
    $access{'create_user'} or &error($text{'acl_create_user_msg'});
    &webmin_log("creating user [$user_uid]",undef,undef,\%in);
    &checkErrors(\%in);
    my $dn = "uid=$user_uid,$base";
    &checkUid($ldap, $in{'uidNumber'});
    my @attrs = &createUserArray($ldap, \%in);
    &LDAPAddUser($ldap, $dn, \@attrs);
    &LDAPUserAddGroup($ldap, $user_uid, $in{'primaryGroup'});
    my %attrs = @attrs;
    &createUser($ldap, \%attrs);
    $creation = "<font color=green>".$text{'edit_user_user_successfully_created'}."</font></br>\n";
}
if ($in{'change'} && $onglet =~ /general/i) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    &checkErrors(\%in);
    my %attrs = &modifyUserGeneral($ldap, $base, $user_uid, \%in);
    &webmin_log("modifying user [$user_uid]",undef,undef,\%attrs);
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);
    my $primaryGroup = $in{'primaryGroup'};
    &LDAPUserAddGroup($ldap, $user_uid, $primaryGroup);
} elsif ($in{'change'} && $onglet =~ /profile/i) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    &webmin_log("modifying user profile [$user_uid]",undef,undef,\%in);
    my %attrs = &modifyUserProfile($ldap, $base, $user_uid, \%in);
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);
}
if ($in{'addgroup'}) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my $group_cn = $in{'group'};
    &webmin_log("adding user [$user_uid] to group [$group_cn]");
    &LDAPUserAddGroup($ldap, $user_uid, $group_cn);
}
if ($in{'groups'}) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
     my @new_groups = split(' - ', $in{'groups'});
    foreach $g (@new_groups) {
		if ($g =~ /[^\-]+/) {
			&webmin_log("adding user [$user_uid] to group [$g]");
			&LDAPUserAddGroup($ldap, $user_uid, $g);
		}
    }
}
if ($in{'removegroup'}) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my $group_cn = $in{'removegroup'};
    &webmin_log("removing user [$user_uid] from group [$group_cn]");
    &LDAPUserRemoveGroup($ldap, $user_uid, $group_cn);
}

my $attrs = [];
my $result = &LDAPSearch($ldap, 
						 "uid=$user_uid", 
						 $attrs, 
						 $base);  
if ($result->count > 1) {
    &error($text{'err_found_more_than_one_user'});
}
my $user = $result->entry;
if (!$user) {
	&error($text{'err_could_not_find_user'}." $user_uid");
}
&header($user_uid,"images/icon.gif","edit_user",1,undef,undef);

print "<script language=\"javascript\">var ifield;</script>";

# print user menu
&printMenu($ldap, $conf, $user, $user_uid, $onglet, $base);
print "<table><tr><td><img src=images/user.gif></td>\n";
print "<td><h1>$user_uid</h1></td><td>$creation</td>\n";
print "<td><a href=delete_user.cgi?uid=$user_uid&base=".&urlize($base).">".$text{'edit_user_delete_user'}."</a></td>\n";
print "</tr></table>\n";
print "<hr>\n";

$url .= "&uid=$user_uid&onglet=$onglet";
#
# General onglet
#
if ($onglet eq "General") {
    print "<form action=$url method=post>\n";
    print "<table width='80%'>\n";
    my $ou = $user->dn;
    $ou =~ s/uid=$user_uid,//g;
    print "<tr><td><b>".$text{'edit_user_organization'}.": </b></td><td>$ou</td></tr>\n";
    my $cn = &LDAPGetUserAttribute($ldap, $user, 'cn');
    if ($cn) {
		$value=$cn;
	} else {
		$value='';
	}
    print "<tr><td><b>".$text{'edit_user_full_name'}.": </b></td><td><input type=text name=cn value='$value'></td></tr>\n";
    my $sn = &LDAPGetUserAttribute($ldap, $user, 'sn');
    if ($sn) {
		$value=$sn;
	} else {
		$value='';
	}
    print "<tr><td><b>".$text{'edit_user_last_name'}.": </b></td><td><input type=text name=sn value='$value'></td></tr>\n";
    my $title = &LDAPGetUserAttribute($ldap, $user, 'title');
    if ($title) { $value=$title; } else { $value='';}
    print "<tr><td><b>".$text{'edit_user_persontitle'}.": </b></td><td><input type=text name=title value='$value'></td></tr>\n";
    my $personou = &LDAPGetUserAttribute($ldap, $user, 'ou');
    if ($personou) { $value=$personou; } else { $value='';}
    print "<tr><td><b>".$text{'edit_user_personou'}.": </b></td><td><input type=text name=ou value='$value'></td></tr>\n";
    my $description = &LDAPGetUserAttribute($ldap, $user, 'description');
    if ($description) {
		$value=$description;
	} else {
		$value='';
	}
    print "<tr><td><b>".$text{'edit_user_description'}.": </b></td><td><input type=text name=description value='$value'></td></tr>\n";
    my $userPassword = &LDAPGetUserAttribute($ldap, $user, 'userpassword');
    $value = $userPassword;
    $value =~ s/^\!//;
    print "<tr><td><b>".$text{'edit_user_password'}.": </b></td><td><input type=password name=userPassword value='$value'></td></tr>\n";
    print "<tr><td><b>".$text{'edit_user_retype_password'}.": </b></td><td><input type=password name=retypeuserPassword value='$value'></td></tr>\n";
    my $uidNumber = &LDAPGetUserAttribute($ldap, $user, 'uidnumber');
    if ($uidNumber) {
		$value=$uidNumber;
	} else {
		$value='';
	}
    print "<tr><td><b>".$text{'edit_user_uid_number'}.": </b></td><td><input type=text name=uidNumber value=$value></td></tr>\n";
    my $gidNumber = &LDAPGetUserAttribute($ldap, $user, 'gidNumber');
    my $primary = &gid2cn($ldap, $gidNumber);
    print "<tr><td><b>".$text{'edit_user_primary_group'}.": </b></td><td>\n";
    print "<input type=text name=primaryGroup value='$primary'>\n";
	print "<input type=button onClick='ifield = document.forms[0].primaryGroup; chooser = window.open(\"choose_groups.cgi\", \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=400\")' value=\"".$text{'edit_user_select'}."\"></td></tr>\n";
    print "</table>\n";
    $value = ($userPassword =~ /^\!/) ? '' : 'checked';
    print "<input type=checkbox name=enableAccount $value>".$text{'edit_user_account_is_enabled'}."<br>\n";
    print "<br><br><input type=submit name=change value='".$text{'edit_user_apply_changes'}."'>\n";
    print "</form>\n";
}

#
# Groups onglet
#
if ($onglet eq "Groups") {
    my @groups = &LDAPGetGroups($ldap);
    if ($#groups > 10) {
		print "<form action=$url method=post>\n";
		print "<input type=submit name=multi value='".$text{'edit_user_add_user_to_the_selected_groups'}."'>\n";
		print "<table><tr><td><textarea wrap=auto name=groups rows=5 cols=25></textarea></td>\n";
		print "<td valign=top><input type=button onClick='ifield=document.forms[0].groups; chooser = window.open(\"choose_groups.cgi?multi=yes\", \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=400\")' value=\"".$text{'edit_user_select_groups'}."\"></td></tr><br>\n";
		print "</table>\n";
		print "</form>\n";
    } else {
		print "<form action=$url method=post>\n";
		print $text{'edit_user_add_user_to_this_group'}.": <select name=group>\n";
		my @names = ();
		foreach (@groups) {
			my $name = &LDAPGetGroupAttribute($ldap, $_, 'cn');
			push (@names, $name);
		}
		foreach (sort @names) {
			print "<option>$_";
		}
		print "</select>\n";
		print "<input type=submit name=addgroup value='".$text{'edit_user_add_group'}."'>\n"; 
		print "</form>\n";
    }
    my @ok_groups = &LDAPGetUserGroups($ldap, $user_uid);
    @ok_groups = sort(@ok_groups);
    print "<table width='80%'>\n";
    print "<tr $cb><td><b>".$text{'edit_user_member_of'}."</b></td><td><b>".$text{'edit_user_remove_user_from_this_group'}."</b></td></tr>\n";

    #build pages links
    my $max = $config{'max_items'};
    my $page =  defined($in{'page'}) ? $in{'page'} : 1;
    my $pages = &pagesLinks($url, $#ok_groups, $page);
    
    #print pages links
    print $pages;

    my @visible_keys = splice(@ok_groups, ($page - 1) * $max, $max);
    foreach (@visible_keys) {
		print "<tr><td><table><tr><td><img src=images/mini_group.gif></td>\n";
		print "<td><a href=edit_group.cgi?cn=".&urlize($_).">$_</a></td></tr></table></td>\n";
		if (&userPrimaryGroup($ldap, $user, $_)) {
			print "<td><font color=green>".$text{'edit_user_primary_group'}."</font></td></tr>\n";
		} else {
			print "<td><a href=$url&removegroup=".&urlize($_).">".$text{'edit_user_remove'}."</a></td></tr>\n";
		}
    }
    print "</table>\n";
    # print pages links
    print $pages;
}

#
# Profile onglet
#
if ($onglet eq "Profile") {
    print "<form action=$url method=post>\n";
    print "<h2>".$text{'edit_user_user_profile'}."</h2>\n";
    print "<table width='80%'>\n";
    my $loginshell = &LDAPGetUserAttribute($ldap, $user, 'loginshell');  
    if ($loginshell) {
		$value=$loginshell;
	} else {
		$value='';
	}
    my @shells = `cat /etc/shells`;
    chop(@shells);
    print "<tr><td>".$text{'edit_user_login_shell'}.": </td><td>\n";
    print "<select name=loginShell>\n";
    print "<option> ";
    foreach (@shells) {
		if ($value eq $_) {
			print "<option selected>$_";
		} else {
			print "<option>$_";
		}
    }
    print "</select></td></tr>\n";
    my $homedirectory = &LDAPGetUserAttribute($ldap, $user, 'homeDirectory');  
    if ($homedirectory) {
		$value=$homedirectory;
	} else {
		$value='';
	}
    print "<tr><td>".$text{'edit_user_home_directory'}.": </td><td><input type=text name=homeDirectory value='$value'></td></tr>\n";
    print "</table>\n";
    print "<br><br><input type=submit name=change value='".$text{'edit_user_apply_changes'}."'>\n";
    print "</form>\n";
}

&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base),$text{'list_users_return'});
