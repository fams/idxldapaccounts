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

# input
my $user_uid = $in{'uid'};
my $onglet = $in{'onglet'};
my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};

# initialize some variables
my $ldap = &LDAPInit();
my $conf = &parseConfig('accounts.conf');
my $creation = '';
my $sattrs = [];
my $url = "edit_".lc($onglet).".cgi?&base=".&urlize($base)."&uid=$user_uid&onglet=$onglet";


if ($in{'change'}) {    
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my %attrs = &sambaModifyUser($user_uid, \%in);
    &webmin_log("modifying samba account for user [$user_uid]",undef, undef,\%attrs);
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);
}
my $result = &LDAPSearch($ldap, "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=$user_uid))", 
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
    &sambaCheckErrors(\%in);
    my %attrs = &sambaCreateUserArray($user_uid, \%in);
    my @old_ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
    my @new_ocs = ();
    foreach (@old_ocs) {
        push(@new_ocs, $_) unless ($_ eq 'sambaSamAccount');
    } 
    push(@new_ocs, 'sambaSamAccount');
    $attrs{'objectclass'} = \@new_ocs;
    &webmin_log("creating samba account for user [$user_uid]",undef, undef,\%attrs);
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);    
    &sambaCreateUser($user_uid, \%in);    
    $creation = "<font color=green>".$text{'edit_sambaaccount_successfully_created'}."</font></br>\n";
    $result = &LDAPSearch($ldap, 
                          "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=$user_uid))", 
                          $sattrs, 
                          $base);  
    $user = $result->entry;
}
&header($user_uid,"images/icon.gif","edit_sambaaccount",1,undef,undef);

&printMenu($ldap, $conf, $user, $user_uid, $onglet, $base);

print "<table><tr><td><img src=images/user.gif></td>
<td><h1>$user_uid</h1></td><td>$creation</td></tr></table>\n";
print "<hr>\n";

print "<table width='80%'><tr><td><h2>".$text{'edit_sambaaccount_samba_account'}."</h2></td><td>\n";
if (!$in{'new'} && !$in{'delete'}) {
    print "<a href=$url&delete=yes>".$text{'edit_sambaaccount_delete_account'}."</a>\n";
}
print "</td></tr></table><br>\n";
print "<form action=$url method=post>\n";
print "<table width='80%'>\n";

if ($in{'delete'}) {
    my $attr_d;
    foreach my $attr (keys %{$conf->{$onglet}}) {
        next if ($attr =~ /(uid|uidNumber|gidNumber|cn|description)/);
        $attr_d->{$attr}=' ';
    }
    my @old_ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
    my @new_ocs = ();
    foreach (@old_ocs) {
           push(@new_ocs, $_) unless ($_ =~ /$onglet/i);
    } 
    $attr_d->{'objectClass'}= \@new_ocs;
    &LDAPModifyUser($ldap, $base, $user_uid, $attr_d);
    &webmin_log("deleting samba account for user [$user_uid]",undef, undef,\%in);
    print "<font color=green>".$text{'edit_sambaaccount_deleted'}."</font></br>\n";
} elsif ($in{'new'}) {
    my $str = '';
    my $uidNumber = &LDAPGetUserAttribute($ldap, $user, 'uidnumber');
    my $gidNumber = &LDAPGetUserAttribute($ldap, $user, 'gidnumber');
    my $userPassword = &LDAPGetUserAttribute($ldap, $user, 'userpassword');
    $userPassword =~ s/^\!//; 
    if ($userPassword =~ /^({Crypt}|{ssha}|{md5})/i) {
          print "<tr><td colspan=2><font color=red>".$text{'edit_sambaaccount_password_is_crypted'}."</td></tr>\n";
        print "<tr><td>".$text{'edit_sambaaccount_disable_nt'}."</td><td><input type=checkbox name=disableNT checked></td></tr>\n";
        print "<tr><td>".$text{'edit_sambaaccount_password'}."</td><td><input type=password name=userPassword></td></tr>\n";
        print "<tr><td>".$text{'edit_sambaaccount_retype_password'}."</td><td><input type=password name=retypeuserPassword></td></tr>\n";
        print "<input type=hidden name=cryptedPassword value=$userPassword>\n";
    } else {
        print "<input type=hidden name=userPassword value=$userPassword>\n";
    }
    foreach my $attr (sort(keys %{$conf->{$onglet}})) {
        my $forbidden = ($conf->{$onglet}->{$attr}->{'forbidden'} == 1) ? 1 : undef;
        my $editable = ($conf->{$onglet}->{$attr}->{'editable'} == 1) ? 1 : undef;
        my $visible = ($conf->{$onglet}->{$attr}->{'visible'} == 1) ? 1 : undef;
        my $default = $conf->{$onglet}->{$attr}->{'default'};
        my $ret = &LDAPGetUserAttribute($ldap, $user, lc($attr));
        my $value =  ($ret) ? $ret : $default;
        $value =~ s/USERNAME/$user_uid/g;
    
         # special computations
        if ($attr eq 'uid') {
              next;
        }
        if ($attr eq 'sambaSID') {
            $value = $config{'samba_sid'} . '-' . ((2 * int($uidNumber)) + 1000);
        }
        if ($attr eq 'sambaPrimaryGroupSID') {
            $value =  &gid2sid($ldap,$gidNumber);
        }
        if ($attr eq 'sambaHomeDrive') {
            print "<tr><td>$attr</td><td>\n";
            print "<select name=sambaHomeDrive>\n";
            print "<option> \n";
            foreach ('C' ... 'Z') {
                if ($value eq "$_:") {
                    print "<option selected>$_:\n";
                } else {
                    print "<option>$_:\n";
                }
            }
            print "</select></td></tr>\n";
            next;
        }
        if ($value eq 'yes') {
            print "<tr><td>$attr: </td><td><input type=checkbox name=$attr checked></td></tr>\n";
            next;
        }
        if ($value eq 'no') {
            print "<tr><td>$attr: </td><td><input type=checkbox name=$attr></td></tr>\n";
            next;
        }
        if ($editable && !$forbidden) {
            print "<tr><td>$attr: </td><td><input type=text name=$attr value='$value'></td></tr>\n";
        } elsif ($visible) {
            print "<tr><td>$attr: </td><td>$value</td></tr>\n";
            $str .= "<input type=hidden name=$attr value='$value'>\n";
        } else {
            $str .= "<input type=hidden name=$attr value='$value'>\n";
        }
    }

    print "</table>\n";
    print $str;
    print "<br><br><input type=submit name=create value='".$text{'edit_sambaaccount_create_account'}."'>\n";

    } else {
        my $sambaNTPassword = &LDAPGetUserAttribute($ldap, $user, 'sambaNTPassword');
        if ($sambaNTPassword =~ /NO PASS/) {
            print "<tr><td colspan=2><font color=green>".$text{'edit_sambaaccount_nt_disabled'}."</td></tr>\n";
        }
        foreach my $attr (sort(keys %{$conf->{$onglet}})) {
            my $editable = ($conf->{$onglet}->{$attr}->{'editable'} == 1) ? 1 : undef;
            my $visible = ($conf->{$onglet}->{$attr}->{'visible'} == 1) ? 1 : undef;
            next if (!$visible);
            my $ret = &LDAPGetUserAttribute($ldap, $user, $attr);
            my $value =  ($ret) ? $ret : '';
    
                                          if ($attr eq 'sambaHomeDrive') {
                                          print "<tr><td>$attr: </td><td>\n";
                                          print "<select name=sambaHomeDrive>\n";
                                          print "<option> \n";
                                          foreach ('C' ... 'Z') {
                                          if ($value eq "$_:") {
                                          print "<option selected>$_:\n";
                                         } else {
                                             print "<option>$_:\n";
                                         }
                              }
                           print "</select></td></tr>\n";
                           next;
                       }
    
                      if ($attr =~ /(pwdCan)/i) {
                          if ($value < time()) {
                              print "<tr><td>$attr: </td><td><input type=checkbox name=$attr checked></td></tr>\n";
                          } else {
                              print "<tr><td>$attr: </td><td><input type=checkbox name=$attr></td></tr>\n";
                          }
                          next;
                      }
                      if ($attr =~ /(pwd)Must/i) {
                          if ($value == 0) {
                              print "<tr><td>$attr: </td><td><input type=checkbox name=$attr checked></td></tr>\n";
                          } else {
                              print "<tr><td>$attr: </td><td><input type=checkbox name=$attr></td></tr>\n";
                          }
                          next;
                      }
    
                      if ($editable) {
                          print "<tr><td>$attr: </td><td><input type=text name=$attr value='$value'></td></tr>\n";
                      } elsif ($visible) {
                          print "<tr><td>$attr: </td><td>$value</td></tr>\n";
                      } else {
                          $str .= "<input type=hidden name=$attr value='$value'>\n";
                      }
                  } 
    print "</table>\n";
    print $str;
    my $sambaAcctFlags = &LDAPGetUserAttribute($ldap, $user, 'sambaAcctFlags');
    print "<input type=hidden name=sambaAcctFlags value=\"$sambaAcctFlags\">";
    if ($sambaAcctFlags =~ /^\[D/) {
        print "<input type=checkbox name=enableAccount> ".$text{'edit_sambaaccount_is_enabled'};
    } else {
        print "<input type=checkbox name=enableAccount checked> ".$text{'edit_sambaaccount_is_enabled'};
    }
    print "<br><br><input type=submit name=change value='".$text{'edit_sambaaccount_apply_changes'}."'>\n";
}
print "</form>\n";

&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base),$text{'list_users_return'});


###########
# functions
###########

sub sambaCreateUserArray {
    my ($user, $array) = (@_);
    my %in = %$array;
    my %attrs = ();

    # pwd and login options
    $attrs{'sambaPwdCanChange'} = 0;
    $attrs{'sambaPwdMustChange'} = 0;
    $attrs{'sambaPwdLastSet'} = 0;
    $attrs{'sambaLogonTime'} = 0;
    $attrs{'sambaLogoffTime'} = 2147483647;
    $attrs{'sambaKickoffTime'} = 2147483647;


    foreach $k (keys %in) {
        next if ($k =~ /^(cat|new|create|change|onglet|base|userPassword|retypeuserPassword|cryptedPassword|disableNT)$/);
        next if ($in{$k} =~ /^\s*$/);

        if ($k eq 'sambaPwdCanChange') {
            $attrs{'sambaPwdCanChange'} = 2147483647;
            next;
        } 
        if ($k eq 'sambaPwdMustChange') {
            $attrs{'sambaPwdMustChange'} = 2147483647;
            next;
        }
        $attrs{$k} = $in{$k};
    }
    # NT and LAN Manager passwords
    if ($in{'disableNT'}) {
        $attrs{'sambaLMPassword'} = 'NO PASSWORDXXXXXXXXXXXXXXXXXXXXX';
        $attrs{'sambaNTPassword'} = 'NO PASSWORDXXXXXXXXXXXXXXXXXXXXX';
    } else {
        my @lmnt = ntlmgen ($in{'userPassword'});
        $attrs{'sambaLMPassword'} = $lmnt[0];
        $attrs{'sambaNTPassword'} = $lmnt[1];
    }

    return %attrs;
}

sub sambaCreateUser {
    my ($user, $array) = (@_);
    my $smbserver = new lxnclient;
    if(! $smbserver->connect('execscript',$config{remotesmb})){
        &error($smbserver->{MSG});
    }
    if(my $ret=$smbserver->exec("mksmbdir $user 1")){
        if($ret == 2){ &error($smbserver->{MSG});}
        return 1;
    }else{
        &error($smbserver->{MSG});
    }
    undef $smbserver;
    return undef;
}

sub sambaModifyUser {
    my ($user, $array) = (@_);
    my %in = %$array;
    my %attrs = ();
    foreach my $k (keys %in) {
        next if $k =~ /^\s*$/; # FIXME: why can this happen ?
        next if ($k =~ /^(cat|uid|change|onglet|base|enableAccount|sambaAcctFlags|unixPwd|userPassword)$/);
        $attrs{$k} = $in{$k};
    }

    if (my $password = $in{'userPassword'}) {
        my @lmnt = ntlmgen ($in{'userPassword'}); 
        $attrs{'sambaLMPassword'} = $lmnt[0];
        $attrs{'sambaNTPassword'} = $lmnt[1];
    }
    #  pwd and login options
    if ($in{'sambaPwdCanChange'}) {
        $attrs{'sambaPwdCanChange'} = 0;
    } else {
        $attrs{'sambaPwdCanChange'} = 2147483647;
    }
    if ($in{'sambaPwdMustChange'}) {
        $attrs{'sambaPwdMustChange'}= 0;
    } else {
        $attrs{'sambaPwdMustChange'} = 2147483647;
    }
    # enable/disable account 
    my $sambaAcctFlags = $in{'sambaAcctFlags'};
    if ($in{'enableAccount'}) {
        $sambaAcctFlags =~ s/D//g;
    } else {
        $sambaAcctFlags =~ s/\[(D*)/\[D/g;
    }
    $attrs{'sambaAcctFlags'}=$sambaAcctFlags;

    return %attrs;
}

sub sambaCheckErrors {
    my $arg = shift;
    my %in = %$arg;
     
    # verify passwords
    if (!$in{'disableNT'} && $in{'retypeuserPassword'}) {
        if ($in{'userPassword'} ne $in{'retypeuserPassword'}) {
            &error("Passwords doesn't match.");
            exit 1;
        }
        if ($in{'userPassword'} eq '') {
            &error($text{'err_password_cannot_be_empty'});
             exit 1;
        }
        if ($in{'userPassword'} =~ /\s/) {
            &error($text{'err_password_no_space'});
            exit 1;
        }
        if($in{'cryptedPassword'} =~ /^{crypt}/i){
            my $crypted = crypt($in{'userPassword'}, $in{'cryptedPassword'});
            if ($crypted ne $in{'cryptedPassword'}) {
                &error($text{'err_password_doesnt_match'});
                exit 1;
            }
        }
        if($in{'cryptedPassword'} =~ /^{MD5}/i){
            my $crypted = md5_base64($in{'userPassword'})."==";
            if ($crypted ne $in{'cryptedPassword'}) {
                &error($text{'err_password_doesnt_match'});
                exit 1;
            }
        }
    }
}
