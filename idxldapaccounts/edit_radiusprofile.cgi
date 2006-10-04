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
$br="<br/>\n";
# input
my $user_uid = $in{'uid'};
my $onglet = $in{'onglet'};
#my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};
my $base = $config{'ldap_users_base'};

# initialize some variables
my $ldap = &LDAPInit();
my $conf = &parseConfig('accounts.conf');
my $creation = '';
my $sattrs = [];
my $url = "edit_".lc($onglet).".cgi?&base=".&urlize($base)."&uid=$user_uid&onglet=$onglet";

my @configurednas=split(/;/,$config{'valid_nas'});
for(@configurednas){ s/\s//g; }

#alteracao de valores
if ($in{'change'}) {	
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my $attr = {};
    my @newnas=('NAS-IP-Address := 127.0.0.1');
    for(@configurednas){
        if($in{'nas:'.$_}=="On") { push(@newnas,"NAS-IP-Address := $_")};
    }
    my $result = &LDAPSearch($ldap, 
         "(&(objectClass=inetOrgPerson)(objectClass=posixaccount)(uid=$user_uid))", 
            $sattrs, 
             $base);  
    if ($result->count > 1) {
        &error($text{'err_found_more_than_one_user'});
    }
    my $user = $result->entry;
    if (!$user) { 
        &error($text{'err_could_not_find_user'}.": $user_uid"); 
    }
    my @radiuscheckitem=$user->get_value('radiuscheckitem');
    @radiuscheckitem = grep(/NAS-IP-Address/,@radiuscheckitem);
    @radiuscheckitem=(@radiuschekitem,@newnas);
    $user->replace('radiuscheckitem',\@radiuscheckitem); 
    $user->update($ldap);
    &webmin_log("modifying radius account for user [$user_uid]",undef, undef,\%in);
}
my $result = &LDAPSearch($ldap, 
			 "(&(objectClass=inetOrgPerson)(objectClass=posixaccount)(uid=$user_uid))", 
			 $sattrs, 
			 $base);  
if ($result->count > 1) {
    &error($text{'err_found_more_than_one_user'});
}
my $user = $result->entry;
if (!$user) { 
&error($text{'err_could_not_find_user'}.": $user_uid"); 
}
if ($in{'create'}) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my %attrs;
    $attrs{'radiuscheckitem'} = "NAS-IP-Address := 127.0.0.1";
    my @old_ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
    my @new_ocs = ();
    foreach (@old_ocs) {
	push(@new_ocs, $_) unless ($_ eq 'radiusprofile');
    } 
    push(@new_ocs, 'radiusprofile');
    #&error(@new_ocs);
    $attrs{'objectclass'} = \@new_ocs;
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);	
    $creation = "<font color=green>".$text{'edit_radiusprofile_successfully_created'}."</font></br>\n";
    $result = &LDAPSearch($ldap, 
			  "(&(objectClass=inetOrgPerson)(objectClass=radiusprofile)(uid=$user_uid))", 
			  $sattrs, 
			  $base);  
    $user = $result->entry;
    &webmin_log("creating radius account for user [$user_uid]",undef, undef,\%in);
}
&header($user_uid,"images/icon.gif","edit_radiusprofile",1,undef,undef);

&printMenu($ldap, $conf, $user, $user_uid, $onglet, $base);

print "<table><tr><td><img src=images/user.gif></td>
<td><h1>$user_uid</h1></td><td>$creation</td></tr></table>\n";
print "<hr>\n";

print "<table width='80%'><tr><td><h2>".$text{'edit_radiusprofile_radius_profile'}."</h2></td><td>\n";
if (!$in{'new'} && !$in{'delete'}) {
    print "<a href=$url&delete=yes>".$text{'edit_radiusprofile_delete_account'}."</a>\n";
}
print "</td></tr></table><br>\n";
print "<form action=$url method=post>\n";
print "<table width='80%'>\n";

if ($in{'delete'}) {
    foreach my $attr (keys %{$conf->{$onglet}}) {
	next if ($attr =~ /(uid|uidNumber|gidNumber|cn|description)/);
	&LDAPModifyUser($ldap, $base, $user_uid, {$attr => \()});
}
    my @old_ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
    my @new_ocs = ();
foreach (@old_ocs) {
    push(@new_ocs, $_) unless ($_ =~ /$onglet/i);
} 
    &LDAPModifyUser($ldap, $base, $user_uid, {'objectClass' => \@new_ocs});
    &webmin_log("deleting radius profile for user [$user_uid]",undef, undef,\%in);
    print "<tr><td><font color=green>".$text{'edit_radiusprofile_deleted'}."</font></td></tr>\n";
} elsif ($in{'new'}) { 
#tela de cadastro de conta 
print "<tr><td>".$text{'edit_radiusprofile_infomsg'}."</td></tr>";
print $str;
print "<br><br><input type=submit name=create value='".$text{'edit_radiusprofile_create_account'}."'>\n";
} else { 
#Tela Edicao de conta
    print "</table>\n";
    print "<form action=$url&change method=post>";
    print "<h4>".$text{'edit_radiusprofile_select_nas'}."</h4>";
    my %mynas;
    foreach my $radius ($user->get_value('radiusCheckItem')){
        if($radius =~ /NAS-ip-address/i){
            my($lixo,$nas) = split(/:=/,$radius);
            $nas=~s/ //;
            $mynas{$nas}=1;
    }
    my $checked="";
    foreach $nas (@configurednas){
        defined($mynas{$nas}) && do { $checked="checked"; };
        print "<input type='checkbox' name='nas:$nas' $checked> $nas".$br;
    }
}
print "<br><br><input type=submit name=change value='".$text{'edit_radiusprofile_apply_changes'}."'>\n";
}
print "</form>\n";
    
&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base),$text{'list_users_return'});


###########
# functions
###########



