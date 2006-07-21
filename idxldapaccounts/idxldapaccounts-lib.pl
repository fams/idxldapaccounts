# idxldapaccounts-lib.pl
do '../web-lib.pl';


#  This code was developped by IDEALX (http://IDEALX.org/) and
#  contributors (their names can be found in the CONTRIBUTORS file).
#
#				 Copyright (C) 2002 IDEALX
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
# 
# Hacked, extended and broked by
# Author: Fernando Augusto Medeiros Silva <fams@linxuxplace.com.br>
# 
# Version: $Id$

## initialize module configuration
&init_config();

=pod "

=head1 NAME

I<idxldapaccounts-lib.pl> - Library for LDAP accounts modifications
needed by the IDX LDAP Accounts Webmin module.

=cut "

=pod "

=head1 SYNOPSIS

require 'idxldapaccounts-lib.pl';

my $ldap = &LDAPInit();

...

&LDAPClose($ldap);

=cut "

#############
## LDAP utils
#############

=pod "

=head1 REQUIREMENTS

=item I<Net::LDAP> module

=item I<Digest::MD5> module

=item I<Crypt::SmbHash> module

=item I<SHA> module

=item I<web-lib.pl> from the Webmin distribution

=cut "

use Net::LDAP qw(:all);
use Net::LDAP::Util qw(ldap_error_name ldap_error_text);
use Unicode::MapUTF8 qw(to_utf8 from_utf8);
use Crypt::SmbHash;
use Digest::MD5  qw(md5 md5_hex md5_base64);
use Digest::SHA1 qw(sha1);
use MIME::Base64 qw(encode_base64);
use File::Basename;
use File::Path;


=pod "

=head1 FUNCTIONS

=over 4

=cut "

=pod "

=head2 LDAP Generic functions

=cut "

=pod "

=item I<LDAPInit()>

=item *
initialize an LDAP connection

=item *
returns a Net::LDAP object

=cut "

sub LDAPInit {
	my $ldap = Net::LDAP->new($config{'ldap_server'}) or 
	  &error($text{'err_could_not_create_ldap_object'}.": ".$config{'ldap_server'}."$@");
	my $mesg = $ldap->bind(
						   dn => $config{'ldap_admin'},
						   password => $config{'ldap_password'});
	if ($mesg->code()) { 
		&error(&ldap_error_name($mesg->code).
			   ": ".&ldap_error_text($mesg->code).
			   "<br>".$text{'err_binding'}." [".
			   $config{'ldap_admin'}." | ".
			   $config{'ldap_password'}."]");
	}
	return $ldap;
}
sub make_salt;

=pod "

=item I<LDAPClose($ldap)>

=item *
close an LDAP connection

=item *
takes a Net::LDAP object as parameter

=cut "

sub LDAPClose {
	my $ldap = shift;
	
	if ($ldap) {
		$ldap->unbind();
	}
}

=pod "

=item I<LDAPSearch($ldap, $searchString, $attrs, $base)>

=item *
search LDAP entries, returns an array of Net::LDAP::Entry objects

=item *
$ldap: a Net::LDAP object

=item *
$searchSting: a LDAP filter

=item *
$attrs: entry's attributes returned by the search

=item *
$base: base DN for search

=cut "

sub LDAPSearch {
	my ($ldap, $searchString, $attrs, $base) = (@_);
	my $result = $ldap->search(
							   base => $base,
							   scope => "sub",
							   sizelimit => $config{'max_search_results'},
							   filter => utf8Encode($searchString),
							   attrs => $attrs,
							  );
	if ($result->code()) { 
		my $text = &ldap_error_name($result->code);
		&error($text.
			   ": ".&ldap_error_text($result->code)) unless ($text =~ /SIZELIMIT/i);
	}
	return $result;
}

=pod "

=item I<LDAPGetUsers($ldap, $attrs)>

=item *
get every users under the configured users base DN with the filter
(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=*))
returns an array of Net::LDAP::Entry objects

=item *
$ldap: a Net::LDAP object

=item *
$attrs: entries attributes returned by the search

=cut "

sub LDAPGetUsers {
	my ($ldap, $attrs) = (@_);
	my $result =  &LDAPSearch($ldap, 
							  "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=*))", 
							  $attrs, 
							  $config{'ldap_users_base'},
							 );
	my @users = $result->entries;
	return @users;
}

=pod "

=item I<LDAPGetGroups($ldap, $attrs)>

=item *
get every groups under the configured groups base DN with the filter
(&(objectClass=posixGroup)(cn=*))
returns an array of Net::LDAP::Entry objects

=item *
$ldap: a Net::LDAP object

=item *
$attrs: entries attributes returned by the search

=cut "

sub LDAPGetGroups {
	my ($ldap, $attrs) = (@_);
	my $result =  &LDAPSearch($ldap, 
							  "(&(objectClass=posixGroup)(cn=*))", 
							  $attrs, 
							  $config{'ldap_groups_base'});
	my @groups = $result->entries;
	return @groups;
}


=pod " 

=item I<LDAPGetObjectClasses($ldap)> 

=item * 
return an array with object classes names (in upper case) defined in the LDAP schema

=item * 
$ldap: a Net::LDAP object 

=cut " 

sub LDAPGetObjectClasses {
	my $ldap = shift;

	my $schema = $ldap->schema();
	my @ocs = $schema->objectclasses();

	return @ocs;
}

=pod " 

=item I<LDAPGetObjectClasseAttributes($ldap, $ocs)> 

=item * 
return an array with attributes of an object classe as defined in the LDAP schema

=item *
$ldap: a Net::LDAP object

=item *
$ocs: an object classe name

=cut "

sub LDAPGetObjectClasseAttributes {
	my ($ldap, $ocs) = (@_);

	my $schema = $ldap->schema();
	my @attrs = $schema->attributes($ocs);

	return @attrs;
}

=pod "

=item I<LDAPGetOUs($ldap, $base)>

=item *
get every Organizational Unit under the specified base DN with the filter
objectClass=organizationalUnit
returns an array of Net::LDAP::Entry objects

=item *
$ldap: a Net::LDAP object

=item *
$base: base DN for search

=cut "

sub LDAPGetOUs {
	my ($ldap, $base) = (@_);
	my $attrs = [ 'ou' ];
	my $result = $ldap->search(
							   base => $base,
							   scope => "sub",
							   filter => "objectClass=organizationalUnit",
							   attrs => $attrs,
							  );

	my @OUs = $result->entries;
	return @OUs;
}



############
# LDAP users
############

=pod "

=head2 LDAP User specific functions

=cut "


=pod "

=item I<LDAPAddUser($ldap, $dn, $attrs)>

=item *
Add an LDAP entry corresponding to a user 

=item *
$ldap: a Net::LDAP object

=item *
$dn: user DN

=item *
$attrs: user atributes as an array reference, must have inetOrgPerson and posixAccount 
objectclasses and corresponding required attributes

=cut "

sub LDAPAddUser {
	my ($ldap, $dn, $attrs) = (@_);
	my $res = $ldap->add( $dn, attrs => [ @$attrs ] );
	if ($res->code()) { 
		&error(&ldap_error_name($res->code).
			   ": ".&ldap_error_text($res->code));
	} elsif ($config{'create_ldap_ab_base'}){
 	#criando base do personal addressbook
		my $uid = getAttrValue($attrs,"uid");
		my $res = $ldap->add( "ou=$uid,".$config{'ldap_personal_ab_base'},
					attrs => [ 
						ou			 => "$uid",
						objectclass	=> ['top','organizationalUnit']
						 ] );
		  if ($res->code()) {
			   &error(&ldap_error_name($res->code).
					": ".&ldap_error_text($res->code));
		  }
	}
}

=pod "

=item I<LDAPDeleteUser($ldap, $base, $user_uid)>

=item *
Delete an LDAP entry corresponding to a user 

=item *
$ldap: a Net::LDAP object

=item *
$base: base DN under which the user lives

=item *
$user_uid: user uid attribute

=cut "

sub LDAPDeleteUser {
	my ($ldap, $base, $user_uid) =(@_);
	my $res = &LDAPSearch($ldap, "uid=$user_uid", [ 'dn', 'homeDirectory','mail','mailAlternateAddress' ], $base);
	my $user = $res->entry;
	if (!defined($user)) {
		&error($text{'err_could_not_find_user'}.": $user_uid");
		exit 1;
	}
	my $usermail=$user->get_value('mail', asref=>1 );
	my $usermail2=$user->get_value('mailAlternateAddress', asref=>1 );
	my @mails=(@$usermail,@$usermail2);
	#use Data::Dumper;
#Removendo aderecos do usuario, FIXME need to have a better place to put it
#Removendo das listas de discussao
	if($config{'create_ldap_ab_base'}){
		my $listbase = $config{'ldap_discussao_base'};
		my $listfilter;
		foreach $curmail(@mails){
			$listfilter.="(mailForwardingAddress=$curmail)";
		}
		my $mailcount =@mails;
		if($mailcount>1){
			$listfilter="(|".$listfilter.")";
		}
   		my $reslista=&LDAPSearch($ldap,"(&(objectclass=qmailuser)$listfilter)",['uid','mailForwardingAddress'],$listbase);
		@entries=$reslista->entries;
		while (my $list_entry = shift @entries){
			my $mailforwarding=$list_entry->get_value('mailForwardingAddress',asref=>1);
			#&error(Dumper($mailforwarding));
			foreach my $curmail(@mails){
				grep(/$curmail/, @$mailforwarding) && $list_entry->delete ( 'mailForwardingAddress' => [ $curmail ] );
			}
		$list_entry->update($ldap);
		}
	}
#Removendo personal Addressbook
	if ($config{'remove_personal_ab'}){
		 my $dn="ou=$user_uid,".$config{'ldap_personal_ab_base'};
		 my $res = $ldap->delete( $dn );
		 if ($res->code()) {
			  &error("PAB".&ldap_error_name($res->code).
						   ": ".&ldap_error_text($res->code));
		 }
	}
#Removendo Homedir
	if ($config{'remove_homes'}) {
		my $homedir = &LDAPGetUserAttribute($ldap, $user, 'homeDirectory');
		if (system("rm -rf $homedir")) {
			&error($text{'err_removing_directory'}.": $homedir");
			exit 1;
		}
		&webmin_log("removing user [$user_uid] home directory [$homedir]"); 
	}
#Removendo o usuario, Finalmente
	my $dn = $user->dn; 
	my $res = $ldap->delete( $dn );
	if ($res->code()) { 
		&error("User".&ldap_error_name($res->code).
		   ": ".&ldap_error_text($res->code)); 
	}
}

=pod "

=item I<LDAPModifyUser($ldap, $base, $user_uid, $array)>

=item *
Modify an LDAP entry corresponding to a user 

=item *
$ldap: a Net::LDAP object

=item *
$base: base OU

=item *
$user_uid: user uid attribute

=item *
$array: modified attributes as a hash reference

=cut "

sub LDAPModifyUser {
	my ($ldap, $base, $user_uid, $array) = (@_);
	my $result = &LDAPSearch($ldap, 
							 "uid=$user_uid", 
							 [], 
							 $base);
	my $user = $result->entry;
	defined($user) or 
	  &error($text{'err_could_not_find_user'}.": [uid=$user_uid]"); 

	my $changes = {};
	foreach (keys %$array) {
		if ($array->{$_} =~ /^\s*$/) {
			$changes->{$_} = [];
		} elsif ($_ =~ /(password|path|objectclass)/i) {
			$changes->{$_} = $array->{$_};
		} else {
			$changes->{$_} = utf8Encode($array->{$_});
		}
	}
	my $dn = $user->dn;
	my $res = $ldap->modify( $dn, 
							 replace => { %$changes },
						   );
	if ($res->code()) { 
		&error(&ldap_error_name($res->code).
			   ": ".&ldap_error_text($res->code)); 
	}
	$user->update($ldap);
}


=pod "

=item I<LDAPGetUserAttribute($ldap, $user, $attr)>

=item *
Return the value of the given attribute $attr

=item *
$ldap: a Net::LDAP object

=item *
$user: a Net::LDAP::Entry object corresponding to an user

=item *
$attr: attribute name

=cut "

sub LDAPGetUserAttribute {
	my ($ldap, $user, $attr) = (@_);
	my $value = $user->get_value($attr);
	return utf8Decode($value);
}

=pod "

=item I<LDAPGetUserAttributes($ldap, $user, $attr)>

=item *
Return an array of values for the multivalued attribute $attr

=item *
$ldap: a Net::LDAP object

=item *
$user: a Net::LDAP::Entry object corresponding to an user

=item *
$attr: attribute name

=cut "

sub LDAPGetUserAttributes {
	my ($ldap, $user, $attr) = (@_);
	my @values = $user->get_value($attr);
	return map (utf8Decode($_), @values);
}

=pod "

=item I<LDAPGetUserGroups($ldap, $user_uid)>

=item *
Return an array of CN corresponding to the groups of which the user is
a member

=item *
$ldap: a Net::LDAP object

=item *
$user_uid: user UID

=cut "

sub LDAPGetUserGroups {
	my ($ldap, $user_uid) = (@_);
	my @groups= &LDAPGetGroups($ldap);
	my @ok_groups = ();
	foreach my $group (@groups) {
		my @members = &LDAPGetGroupAttributes($ldap, $group, 'memberuid');
		foreach (@members) {
			if ($_ eq $user_uid) {
				my $group_cn = &LDAPGetGroupAttribute($ldap, $group, 'cn');
				push(@ok_groups, $group_cn);
			}
		}
	}
	return @ok_groups;
}

=pod "

=item I<LDAPUserAddGroup($ldap, $user_uid, $group_cn)>

=item *
Add user to a group

=item *
$ldap: a Net::LDAP object

=item *
$user_uid: user UID

=item *
$group_cn: the group CN

=cut "

sub LDAPUserAddGroup {
	my ($ldap, $user_uid, $group_cn) = (@_);
	my $result = &LDAPSearch($ldap, 
							 "cn=$group_cn",  
							 ['memberuid'],
							 $config{'ldap_groups_base'});
	my $group = $result->entry;
	if (!defined($group)) {
		&error($text{'err_could_not_find_group'}.": [$group_cn]");
		exit 1;
	}
	&LDAPGroupAddMember($ldap, $group, $user_uid);
}
=pod "

=item I<LDAPMailRemoveList($ldap, @mails)>

=item *
Remove user to a group

=item *
$ldap: a Net::LDAP object

=item *
@mail list of mails to remove from lists

=cut "
sub LDAPMailRemoveList{
	my($ldap,@mails)  = (@_);
    #Removendo das listas de discussao
	my $listbase = $config{'ldap_discussao_base'};
	my $listfilter;
	foreach $curmail(@mails){
		$listfilter.="(mailForwardingAddress=$curmail)";
	}
	my $mailcount =@mails;
	if($mailcount>1){
		$listfilter="(|".$listfilter.")";
	}
   	my $reslista=&LDAPSearch($ldap,"(&(objectclass=qmailuser)$listfilter)",['uid','mailForwardingAddress'],$listbase);
	@entries=$reslista->entries;
	while (my $list_entry = shift @entries){
		my $mailforwarding=$list_entry->get_value('mailForwardingAddress',asref=>1);
		#&error(Dumper($mailforwarding));
		foreach my $curmail(@mails){
			grep(/$curmail/, @$mailforwarding) && $list_entry->delete ( 'mailForwardingAddress' => [ $curmail ] );
		}
		$list_entry->update($ldap);
	}
}

=pod "

=item I<LDAPUserRemoveGroup($ldap, $user_uid, $group_cn)>

=item *
Remove user to a group

=item *
$ldap: a Net::LDAP object

=item *
$user_uid: user UID

=item *
$group_cn: the group CN

=cut "

sub LDAPUserRemoveGroup {
	my ($ldap, $user_uid, $group_cn) = (@_);
	my $result = &LDAPSearch($ldap, 
							 "cn=$group_cn",  
							 ['memberuid'],
							 $config{'ldap_groups_base'});
	my $group = $result->entry;
	&LDAPGroupRemoveMember($ldap, $group, $user_uid);
}

=pod "

=item I<LDAPUserAddOcs($ldap, $user_uid, $ocs)>

=item *
Add an objectclasse to a user

=item *
$ldap: a Net::LDAP object

=item *
$user_uid: user UID

=item *
$ocs: an objectclass name

=cut "
sub LDAPUserAddOcs {
	my ($ldap, $user, $ocs) = (@_);
	my @OCS = &LDAPGetUserAttributes($ldap, $user, 'objectClass');
	my @new_OCS= ();
	foreach (@OCS) {
		push(@new_OCS, $_) unless ($_ eq $ocs);
	}
	push(@new_OCS, $ocs);
	$user->replace('objectClass', \@new_OCS);
	$user->update($ldap);
}

=pod "

=item I<LDAPUserHasOcs($ldap, $user, $ocs)>

=item *
Return 1 if the user has the given objectclass

=item *
$ldap: a Net::LDAP object

=item *
$user: a Net::LDAP::Entry object corresponding to a user

=item *
$ocs: an objectclass name

=cut "
sub LDAPUserHasOcs {
	my ($ldap, $user, $ocs) = (@_);
	my @OCS = &LDAPGetUserAttributes($ldap, $user, 'objectClass');
	my $res = undef;
	foreach (@OCS) {
		if (lc($_) eq lc($ocs)) {
			$res = 1;
		}
	}
	return $res;
}

=pod "

=item I<LDAPUserIsDisabled($ldap, $user)>

=item *
Return 1 if user's account is disabled, returns undef otherwise

=item *
$ldap: a Net::LDAP object

=item *
$user: a Net::LDAP::Entry object corresponding to an user

=cut "

sub LDAPUserIsDisabled {
	my ($ldap, $user) = (@_);
	my $userpassword = &LDAPGetUserAttribute($ldap, $user, 'userPassword');
	if ($userpassword =~ /^\!/) {
		return 1;
	} else {
		return undef;
	}
}



#############
# LDAP groups
#############

=pod "

=head2 LDAP Group specific functions

=cut "

=pod "

=item I<LDAPAddGroup($ldap, $dn, $attrs)>

=item *
Add an LDAP entry corresponding to a group 

=item *
$ldap: a Net::LDAP object

=item *
$dn: gorup DN

=item *
$attrs: group atributes as an array reference, must have the posixGroup
objectclasse and corresponding required attributes

=cut "

sub LDAPAddGroup {
	my ($ldap, $dn, $attrs) = (@_); 
	
	my $res = $ldap->add( utf8Encode($dn), attrs => [ @$attrs ] );
	if ($res->code()) { 
		&error(&ldap_error_name($res->code).
			   ": ".&ldap_error_text($res->code)."DN:".$dn); 
	}
}

=pod "

=item I<LDAPDeleteGroup($ldap, $group_cn)>

=item *
Delete an LDAP entry corresponding to a group 

=item *
$ldap: a Net::LDAP object

=item *
$group_cn: group CN

=cut "

sub LDAPDeleteGroup {
	my ($ldap, $group_cn) =(@_);
	my $result = &LDAPSearch($ldap, 
							 "cn=$group_cn", 
							 [], 
							 $config{'ldap_groups_base'});
	my @entries = $result->entries;
	my $group = $entries[0];
	defined($group) or 
	  &error($text{'err_could_not_find_group'}.": [cn=$group]"); 
	my $res = $ldap->delete($group->dn);
	if ($res->code()) { 
		&error(&ldap_error_name($res->code).
			   ": ".&ldap_error_text($res->code)); 
	}
}

=pod "

=item I<LDAPModifyGroup($ldap, $group_cn, $array)>

=item *
Modify an LDAP entry corresponding to a group 

=item *
$ldap: a Net::LDAP object

=item *
$group_cn: group CN

=item *
$array: modified attributes as a hash reference

=cut "

sub LDAPModifyGroup {
	my ($ldap, $group_cn, $array) = (@_);
	my $result = &LDAPSearch($ldap, 
							 "cn=$group_cn", 
							 [], 
							 $config{'ldap_groups_base'});
	my @entries = $result->entries;
	my $group = $entries[0];
	defined($group) or 
	  &error($text{'err_could_not_find_group'}.": [cn=$group]"); 
	my $dn = $group->dn;
	foreach (keys %$array) {
		if ($array->{$_} =~ /^\s*$/) {
			$array->{$_} = [];
		} else {
			$array->{$_} = utf8Encode($array->{$_});
		}
	}
	my $res = $ldap->modify( $dn,
							 replace => $array ,
						   );
	if ($res->code()) { 
		&error(&ldap_error_name($res->code).
			   ": ".&ldap_error_text($res->code)); 
	}
}

=pod "

=item I<LDAPGetGroupAttribute($ldap, $group, $attr)>

=item *
Return the value of the given attribute $attr

=item *
$ldap: a Net::LDAP object

=item *
$group: a Net::LDAP::Entry object corresponding to an group

=item *
$attr: attribute name

=cut "
sub LDAPGetGroupAttribute {
	my ($ldap, $group, $attr) = (@_);
	my $value = $group->get_value($attr);
	return utf8Decode($value);
}

=pod "

=item I<LDAPGetGroupAttributes($ldap, $group, $attr)>

=item *
Return an array of values for the multivalued attribute $attr

=item *
$ldap: a Net::LDAP object

=item *
$group: a Net::LDAP::Entry object corresponding to a group

=item *
$attr: attribute name

=cut "
sub LDAPGetGroupAttributes {
	my ($ldap, $group, $attr) = (@_);
	my @values = $group->get_value($attr);
	return map (utf8Decode($_), @values);
}


=pod "

=item I<LDAPGroupAddMember($ldap, $group, $member)>

=item *
Add a member to a group

=item *
$ldap: a Net::LDAP object

=item *
$group: a Net::LDAP::Entry object corresponding to a group

=item *
$member: a member UID

=cut "

sub LDAPGroupAddMember {
	my ($ldap, $group, $member) = (@_);
	
	my $res = &LDAPSearch($ldap, 
						  "(uid=$member)", 
						  [], 
						  $config{'ldap_users_base'});
	if (!defined($res->entry)) {
		&error($text{'err_could_not_find_user'}.": [$member]");
		exit 1;
	}
	my @members = &LDAPGetGroupAttributes($ldap, $group, 'memberuid');

	my @new_members = ();
	foreach (@members) {
		push(@new_members, $_) unless ($_ eq $member);
	}
	push(@new_members, $member);
	foreach (@new_members) {
		webmin_log("member: ",undef, $_, undef);
	}
	$group->replace('memberuid', \@new_members);
	$group->update($ldap);
}

=pod "

=item I<LDAPGroupRemoveMember($ldap, $group, $member)>

=item *
Remove a member from a group

=item *
$ldap: a Net::LDAP object

=item *
$group: a Net::LDAP::Entry object corresponding to a group

=item *
$member: a member UID

=cut "

sub LDAPGroupRemoveMember {
	my ($ldap, $group, $member) = (@_);
	my @members = &LDAPGetGroupAttributes($ldap, $group, 'memberuid');
	my @new_members = ();
	foreach (@members) {
		push(@new_members, $_) unless ($_ eq $member);
	}
	$group->replace('memberuid', \@new_members);
	$group->update($ldap);
}




############################
# account specific functions
############################ 


=pod "

=head2 LDAP Accounts (inetOrgPerson and posixAccount) specific functions

=cut "

=pod "
=item I<gid2sid($ldap, $gid)>

=item *
Return the sid of the group with the given gid

=item *
$ldap: a Net::LDAP object

=item *
$gid: a gid

=cut "

sub gid2sid {
	my ($ldap, $gid) = (@_);
	
	my $attrs = ['gidNumber', 'sambaSID'];
	my $result =  &LDAPSearch($ldap, 
							  "gidNumber=$gid", 
							  $attrs, 
							  $config{'ldap_groups_base'});
	if ($result->count>0) {
		my $group = $result->entry;
		my $sid = $group ? &LDAPGetGroupAttribute($ldap, $group, 'sambaSID') : undef;
		return $sid;
	} else {
		return undef;
	}

}


=pod"

=item I<getAttrValue($attrs,$attr)

=item *
get attribute value in pair list

=item *
$attrs attrs

=item *
$attr attribute desired

=cut"

sub getAttrValue{
	my ($attrs,$attr)= (@_);
	my $get=0;
	my $out;
	foreach (@$attrs){
		chomp;
		$out=$out.$_."<br/>\n";
		if($get){
			return $_;
		}
		 /^$attr$/ && do { $get=1 ; };
	}
}
=pod "

=item I<createUserArray($ldap, $array)>

=item *
Build an attributes array for use in LDAP entry creation 

=item *
$ldap: a Net::LDAP object

=item *
$array: form parameters as returned by the add_user.cgi script, as a hash reference

=cut "


sub createUserArray {
	my ($ldap, $array) = (@_);

	my $user_uid = $array->{'uid'};

	# clean some params
	my @attrs = ();
	foreach $k (keys %$array) {
		next if ($k =~ /^(cat|create|change|onglet|base|userPassword|retypeuserPassword|primaryGroup)$/);
		next if ($array->{$k} =~ /^\s*$/);
		push (@attrs, $k, utf8Encode($array->{$k}));
	}

	# gidNumber
	my $primarygroup = $array->{'primaryGroup'};
	my $gidnumber = &cn2gid($ldap, $primarygroup);
	if (!defined($gidnumber)) {
		&error($text{'err_primary_group_not_found'});
		exit 1;
	}
	push(@attrs, 'gidNumber', $gidnumber);

	# password
	my $userpassword = undef;
	if ($config{'crypt_passwords'} == 0) {
	#fams 17092004 password patch
		if ($config{'crypt_passwords_hash'} == 1) {
			my $crypted = crypt($in{'userPassword'}, join '', ('.', '/', 0..9, 'A'..'Z', 'a'..'z')[rand 64, rand 64]);
			$userpassword = '{Crypt}'.$crypted;
		}
		if ($config{'crypt_passwords_hash'} == 2) {
			my $crypted = md5_base64($in{'userPassword'})."=="; 
			$userpassword = '{MD5}'.$crypted;
		}
	} else {
		$userpassword = $array->{'userPassword'};
	}
	push(@attrs, 'userPassword', $userpassword);
	
	# Unix home and shell
	my $homedir = $config{'homedir_default'};

	if ($config{'letterhomes'} == 1) {
		$homeletter = lc(substr($user_uid,0,1));
		$homedir =~s/USERNAME/$homeletter\/$user_uid/;
	} else {
		$homedir =~ s/USERNAME/$user_uid/;
	}
	push(@attrs, 'homeDirectory', $homedir);
	push(@attrs, 'loginShell', $config{'loginshell_default'}); 

	# objectClass
	push (@attrs, 'objectClass', ['top','inetOrgPerson', 'posixAccount']);

	return @attrs;
}


=pod "

=item I<createUser($ldap, $array)>

=item *
Perform system actions related to user creation (home directory creation for the moment)

=item *
$ldap: a Net::LDAP object

=item *
$array: user attributes as returned by the createUserArray function

=cut "


sub createUser {
	my ($ldap, $array) = (@_);

	# get needed params
	my $user_uid = $array->{'uid'};
	my $gidnumber = $array->{'gidNumber'};
	my $homedir = $array->{'homeDirectory'};	

	# local home directory
	$dirname=dirname($homedir);
	if (! -e $dirname) {
		if (system("mkdir -p $dirname")) {
			&error($text{'err_creating_directory'}.": $dirname");
			exit 1;
		}
	}
	if(! -e $homedir) {
		if (system("cp -pa /etc/skel  $homedir")){
			&error($text{'err_copying_skel_directory'});
			exit 1;
		}
	} 
	# perform a nscd restart to be sure the user is known from the system
	my $nscd = $config{"nscd_path"};
	system("$nscd restart");
	if (system("chown -R $user_uid:$gidnumber $homedir")) {
		&error($text{'err_changing_directory_owner'}." $homedir $user_uid.$gidnumber");
		exit 1;
	}
}



=pod "

=item I<modifyUserGeneral($ldap, $base, $user_uid, $array)>

=item *
Return a hash for modification of user LDAP attributes

=item *
$ldap: a Net::LDAP object

= item *
$base: base OU

=item *
$user_uid: user UID 

=item *
$array: form parameters as returned by the edit_user.cgi script, as a hash reference

=cut "


sub modifyUserGeneral {
	my ($ldap, $base, $user_uid, $array) = (@_);
	my %in = %$array;

	my $searchattrs = ['objectClass', 'homeDirectory'];
	my $mesg = &LDAPSearch($ldap, "(uid=$user_uid)", $searchattrs, $base);
	my $user = $mesg->entry;
	if (!defined($user)) {
		&error($text{'err_could_not_find_user'});
		exit 1;
	}

	my %attrs = ();
	foreach $k (keys %in) {
		next if ($k =~ /^(cat|uid|change|onglet|base|enableAccount|acctFlags|userPassword|retypeuserPassword|primaryGroup)$/);
		#		next if $in{$k} =~ /^\s*$/;
		$attrs{$k} = $in{$k};
	}
	# gidNumber
	my $gidnumber = &cn2gid($ldap, $in{'primaryGroup'});
	if (!defined($gidnumber)) {
		&error($text{'err_primary_group_not_found'});
		exit 1;
	}
	$attrs{'gidNumber'} = $gidnumber;
	my $homedir = &LDAPGetUserAttribute($ldap, $user, 'homeDirectory');
	if ($homedir) {
		if (( -e $homedir)) {
		if (system("chown $user_uid:$gidnumber $homedir")) {
			&error($text{'err_changing_directory_owner'}." $homedir $user_uid.$gidnumber");
			exit 1;
		}
		&webmin_log("changing user [$user_uid] home directory [$homedir] to owner [$user_uid.$gidnumber]"); 
	}
	}

	# password
	my $userpassword = $in{'userPassword'};
	my $iscrypted = ($userpassword =~ /^({Crypt}|{MD5}|{SSHA})/i) ? 1 : undef;
	if ($config{'crypt_passwords'} == 1 && !$iscrypted) {
		if($config{'crypt_passwords_hash'} == 0){
			my $crypted = crypt($in{'userPassword'}, 
			join '', ('.', '/', 0..9, 'A'..'Z', 'a'..'z')[rand 64, rand 64]);
			$userpassword = '{Crypt}'.$crypted;
		}
		if($config{'crypt_passwords_hash'} == 2){
			my $crypted = md5_base64($in{'userPassword'})."=="; 
			$userpassword = '{MD5}'.$crypted;
		}
		if ($config{'crypt_passwords_hash'} == 1 ) {
      		# Generate SSHA hash (SHA1 with salt)
      			my $salt = make_salt(4);
      			$userpassword = "{SSHA}" . encode_base64( sha1($in{'userPassword'}.$salt) . $salt,'' );
		}
	}
	# enable/disable account
	if (!$in{'enableAccount'}) {
		$userpassword = "!$userpassword";
	}
	$attrs{'userPassword'} = $userpassword;
	
	# Samba dependencies
	if (&LDAPUserHasOcs($ldap, $user, 'sambaSAMaccount')) {
		&webmin_log("synchronizing samba parameters for user [$user_uid]");
		if (!$iscrypted) {
			my @lmnt = ntlmgen ($in{'userPassword'});
# samba v3
			$attrs{'sambaLMPassword'}=$lmnt[0];
			$attrs{'sambaNTPassword'}=$lmnt[1];
		}
		
		$attrs{'sambaSID'} = $config{'samba_sid'} . '-';
		$attrs{'sambaSID'} .= (2 * int($in{'uidNumber'})) + 1000;
		$attrs{'sambaPrimaryGroupSID'} = &gid2sid($ldap,$gidnumber);
		

# samba v2
# 			$attrs{'lmPassword'}=$lmnt[0];
# 			$attrs{'ntPassword'}=$lmnt[1];
# 		} 
# 		$attrs{'rid'} = (2 * int($in{'uidNumber'})) + 1000;
# 		$attrs{'primaryGroupID'} = (2 * int($gidnumber)) + 1000;
	}

	return %attrs;
}

=pod "

=item I<modifyUserProfile($ldap, $base, $user_uid, $array)>

=item *
Return a hash for modification of user profile LDAP attributes

=item *
$ldap: a Net::LDAP object

=item *
$base: base OU

=item *
$user_uid: user UID 

=item *
$array: form parameters as returned by the edit_user.cgi script, as a hash reference

=cut "

sub modifyUserProfile {
	my ($ldap, $base, $user_uid, $array) = (@_);
	my %in = %$array;
	my %attrs = ();

	# loginShell
	$attrs{'loginShell'} = $in{'loginShell'};

	# homeDirectory 
	my $searchattrs = ['homeDirectory', 'gidNumber'];
	my $mesg = &LDAPSearch($ldap, "(uid=$user_uid)", $searchattrs, $base);
	my $user = $mesg->entry;
	my $old_home = &LDAPGetUserAttribute($ldap, $user, 'homeDirectory');
	my $gidnumber = &LDAPGetUserAttribute($ldap, $user, 'gidNumber');
	my $homedir = $in{'homeDirectory'};

	if ($old_home ne $homedir) {
		$attrs{'homeDirectory'}=$homedir;
		if ($old_home && $config{'remove_homes'}) {
			if (system("rm -rf $old_home")) {
				&error($text{'err_removing_directory'}.": $old_home");
				exit 1;
			}
			&webmin_log("removing user [$user_uid] old home directory [$old_home]"); 
		}
		if ((! -e $homedir)) {
			if (system("mkdir -p $homedir")) {
				&error($text{'err_creating_directory'}.": $homedir");
				exit 1;
			}
			&webmin_log("creating user [$user_uid] new home directory [$homedir]"); 
			if (system("chown $user_uid:$gidnumber $homedir")) {
				&error($text{'err_changing_directory_owner'}." $homedir $user_uid.$gidnumber");
				exit 1;
			}
			&webmin_log("changing user [$user_uid] home directory [$homedir] to owner [$user_uid.$gidnumber]"); 
		}
	}

	return %attrs;
}

=pod "

=item I<checkErrors($input)>

=item *
check for user input errors

=item *
$input: reference to the %in array as received by the edit_user.cgi script

=cut "

sub checkErrors {
	my $arg = shift;
	my %in = %$arg;
	 
	# verify passwords
	if ($in{'userPassword'} ne utf8Encode($in{'userPassword'})) {
		&error("Wrong character in password");
	}
	
	if ($in{'userPassword'} ne $in{'retypeuserPassword'}) {
		&error($text{'err_passwords_dont_match'});
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

	# verify uid
	if ($in{'uid'} ne utf8Encode($in{'uid'})) {
		&error("Wrong character in uid");
	}
	if ($in{'uid'} eq '') {
		&error($text{'err_user_id_not_empty'});
		exit 1;
	}
	if ($in{uid} =~ /\s/) {
		&error($text{'err_user_id_no_space'});
		exit 1;
	}
	# verify uidNumber
	if ($in{'uidNumber'} eq '') {
		&error($text{'err_uid_not_empty'});
		exit 1;
	}
	if ($in{uidNumber} =~ /\s/) {
		&error($text{'err_uid_no_space'});
		exit 1;
	}
	if ($in{uidNumber} =~ /\D/) {
		&error($text{'err_uid_numeric'});
		exit 1;
	}
	if ($in{uidNumber} =~ /^0/) {
		&error($text{'err_uid_begin_by_zero'});
		exit 1;
	}

	# verify cn
	if ($in{'cn'} =~ /^\s*$/) {
		&error($text{'err_user_cn_not_empty'});
		exit 1;
	}

	# verify sn
	if ($in{'sn'} =~ /^\s*$/) {
		&error($text{'err_user_sn_not_empty'});
		exit 1;
	}
}
#######
# Utils
#######

=pod "

=head2 Other functions

=cut "

=pod "

=item I<getGids($ldap)>

=item *
Return a hash with CN as key and gidNumber as value for each group in the LDAP

=item *
$ldap: a Net::LDAP object

=cut "

sub getGids {
	my $ldap = shift;
	my $attrs = ['cn', 'gidnumber'];
	my @groups = &LDAPGetGroups($ldap, $attrs);
	my %gids =();
	foreach (@groups) {
		my $cn = &LDAPGetGroupAttribute($ldap, $_, 'cn');
		my $gidnumber = &LDAPGetGroupAttribute($ldap, $_, 'gidnumber');
		$gids{$cn} = $gidnumber;
	}
	return %gids;
}

=pod "

=item I<getUids($ldap)>

=item *
Return a hash with UID as key and uidNumber as value for each user in the LDAP

=item *
$ldap: a Net::LDAP object

=cut "

sub getUids {
	my $ldap = shift;
	my $attrs = ['uid', 'uidnumber'];
	my @users = &LDAPGetUsers($ldap, $attrs);
	my %uids =();
	foreach (@users) {
		my $uid = &LDAPGetUserAttribute($ldap, $_, 'uid');
		my $uidnumber = &LDAPGetUserAttribute($ldap, $_, 'uidnumber');
		$uids{$uid} = $uidnumber;
	}
	return %uids;
}

=pod "

=item I<gid2cn($ldap, $gid)>

=item *
Return the CN of the group with the given gidNumber

=item *
$ldap: a Net::LDAP object

=item *
$gid: a gidNumber

=cut "

sub gid2cn {
	my ($ldap, $gid) = (@_);
	
	my $attrs = ['cn', 'gidNumber'];
	my $result =  &LDAPSearch($ldap, 
							  "gidNumber=$gid", 
							  $attrs, 
							  $config{'ldap_groups_base'});
	if ($result->count>0) {
		my $group = $result->entry;
		my $cn = &LDAPGetGroupAttribute($ldap, $group, 'cn');
		return $cn;
	} else {
		return undef;
	}
}

=pod "

=item I<cn2gid($ldap, $cn)>

=item *
Return the gid of the group with the given CN

=item *
$ldap: a Net::LDAP object

=item *
$cn: a CN

=cut "

sub cn2gid {
	my ($ldap, $cn) = (@_);
	
	my $attrs = ['cn', 'gidNumber'];
	my $result =  &LDAPSearch($ldap, 
							  "cn=$cn", 
							  $attrs, 
							  $config{'ldap_groups_base'});
	if ($result->count>0) {
		my $group = $result->entry;
		my $gid = $group ? &LDAPGetGroupAttribute($ldap, $group, 'gidNumber') : undef;
		return $gid;
	} else {
		return undef;
	}

}


=pod "

=item I<checkUid($ldap, $uid)>

=item *
Check if the given uidNumber doesn't already exist in LDAP or doesn't minorate the connfigured
minimum uidNumber, if it does, print an error page, else do nothing

=item *
$ldap: a Net::LDAP object

=item *
$uid: an uidNumber

=cut "
sub checkUid {
	my ($ldap, $uid) = (@_);
	my %UIDS = getUids($ldap);
	my %revUIDS = reverse %UIDS;
	if ($revUIDS{$uid}) {
		&error($text{'err_uid_already_exists'}.": $uid, ".$text{'err_uid_valid'}.": ".&pickUid($ldap));
	}	
}

=pod "

=item I<checkGid($ldap, $gid)>

=item *
Check if the given gidNumber doesn't already exist in LDAP or doesn't minorate the connfigured
minimum gidNumber, if it does, print an error page, else do nothing

=item *
$ldap: a Net::LDAP object

=item *
$gid: an gidNumber

=cut "
sub checkGid {
	my ($ldap, $gid) = (@_);
	my %GIDS = getGids($ldap);
	my %revGIDS = reverse %GIDS;
	if ($revGIDS{$gid}) {
		&error($text{'err_gid_already_exists'}.": $gid, ".$text{'err_uid_valid'}.": ".&pickGid($ldap));
	}	
}

=pod "

=item I<pickUid($ldap, $uid)>

=item *
Return an uidNumber that doesn't already exist in LDAP nor minorates the connfigured
minimum uidNumber

=item *
$ldap: a Net::LDAP object

=item *
$uid: an uidNumber

=cut "
sub pickUid {
	my $ldap = shift;
	if($config{'use_new_allocation'}){
		return get_next_id($ldap,"uidNumber",$config{'min_uid'});
	}
	my %UIDS = &getUids($ldap);
	my @uids = values %UIDS;
	@uids = reverse sort {$a <=> $b} @uids;
	my @maxs = ($config{'min_uid'}, $uids[0] + 1);
	my $min_uid = ($config{'min_uid'} <= $uids[0] + 1) ? $uids[0] +1 : $config{'min_uid'};
	return $min_uid;
}
#FIXME a funcao abaixo foi portada nas coxas... 

=pod "

=item I<get_next_id($ldap, $attribute)>

=item *
Return an uidNumber/gidNumber that doesn't already exist in LDAP nor minorates the connfigured
minimum uidNumber

=item *
$ldap: a Net::LDAP object

=item *
$uid: an uidNumber

=cut "

sub get_next_id($$$) {
  my $ldap = shift;
  my $attribute = shift;
  my $minid = shift;
  my $tries = 0;
  my $found=0;
  my $next_uid_mesg;
  my $nextuid;
  $ldap_base_dn=$config{'ldap_suffix'};
  do {
	$next_uid_mesg = $ldap->search(
								  base => $config{'ldap_pool_dn'},
								  filter => "(objectClass=sambaUnixIdPool)",
								  scope => "base"
								 );
	$next_uid_mesg->code && &error("Error looking for next uid");
	if ($next_uid_mesg->count != 1) {
	  &error("Could not find base dn, to get next $attribute");
	}
	my $entry = $next_uid_mesg->entry(0);
            
	$nextuid = $entry->get_value($attribute);
	if($nextuid < $minid){
		$nextuid=$minid;
	}
	my $modify=$ldap->modify( $config{'ldap_pool_dn'},
							 changes => [
								 replace => [ $attribute => $nextuid + 1 ]
										]
							   );
	$modify->code && &error("Error: ". $modify->error);
	# let's check if the id found is really free (in ou=Groups or ou=Users)...
	my $check_uid_mesg = $ldap->search(
									  base => $ldap_base_dn,
									  filter => "($attribute=$nextuid)",
									 );
	$check_uid_mesg->code && &error("Cannot confirm $attribute $nextuid is free");
	if ($check_uid_mesg->count == 0) {
	  $found=1;
	  return $nextuid;
	}
	$tries++;
	#print "Cannot confirm $attribute $nextuid is free: checking for the next one\n"
  } while ($found != 1);
  &error("Could not allocate $attribute!");
}

=pod "

=item I<pickGid($ldap, $gid)>

=item *
Return an gidNumber that doesn't already exist in LDAP nor minorates the connfigured
minimum gidNumber

=item *
$ldap: a Net::LDAP object

=item *
$gid: an gidNumber

=cut "
sub pickGid {
	my $ldap = shift;
	if($config{use_new_allocation}){
		return get_next_id($ldap,"uidNumber",$config{'min_gid'});
	}
	my %GIDS = &getGids($ldap);
	my @gids = values %GIDS;
	@gids = reverse sort {$a <=> $b} @gids;
	my @maxs = ($config{'min_gid'}, $gids[0] + 1);
	my $min_gid = ($config{'min_gid'} <= $gids[0] + 1) ? $gids[0] +1 : $config{'min_gid'};
	return $min_gid;
}


=pod "

=item I<userPrimaryGroup($ldap, $user, $group [, $gidnumber])>

=item *
Return 1 if $user has $group's gid number as gid number, or if present, if $user has
$gidnumber as gid number, return undef otherwise


=item *
$ldap: a Net::LDAP object

=item *
$user: a Net::LDAP::Entry object representing an user

=item *
$cn: a group Common Name

=item *
$gidnumber: a gidNumber (optional)

=cut "
sub userPrimaryGroup {
	my ($ldap, $user, $cn, $gidnumber) = (@_);
	
	my $primary = &LDAPGetUserAttribute($ldap, $user, 'gidNumber');
	if ($gidnumber) {
		if ($primary == $gidnumber) {
			return 1;
		} else {
			return undef;
		}
	} 

	if (&gid2cn($ldap, $primary) eq $cn) {
		return 1;
	} else {
		return undef;
	}
}

=pod "

=item I<parseConfig($file)>

=item *
Parse accounts configuration file and return a hash reference like this:

{

	ACCOUNTTYPE1 => { 

	ATTRIBUTE1 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	ATTRIBUTE2 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},


	}

	ACCOUNTTYPE2 => {


	...

	}

}
 
=item *
$file: file name, by convention, the file 'acccounts.conf' is used for user custom configuration and
should be the only value given to $file, when this file isn't found, the file 'default_accounts.conf'
is loaded

=cut "
sub parseConfig {
	my $file  = shift;
	
	my $conf = {};
	my $fd = open(FILE, $file);
	defined($fd) or $fd = open(FILE, 'default_accounts.conf');
	defined($fd) or &error($text{'err_no_accounts_configuration'});
	
	my $k = {};
	foreach my $l (<FILE>) {
		next if ($l =~ /^\#/);
		if ($l =~ /^\[(.*)\]/) {
			$k = $1;
			$conf->{$k} = {};
		} elsif ($l =~ /^\*/) {
			$l =~ s/^\*//;
			if ($l =~ /^(.*)=(.*),(.*),(.*)$/) {
				$conf->{$k}->{$1}->{'visible'} = $2;
				$conf->{$k}->{$1}->{'editable'} = $3;
				$conf->{$k}->{$1}->{'default'} = $4;
				$conf->{$k}->{$1}->{'forbidden'} = 'yes';
			}
		} elsif ($l =~ /^(.*)=(.*),(.*),(.*)$/) {
			$conf->{$k}->{$1}->{'visible'} = $2;
			$conf->{$k}->{$1}->{'editable'} = $3;
			$conf->{$k}->{$1}->{'default'} = $4;
		}
	}
	
	close($fd);
	return $conf;
}


=pod "

=item I<writeConfig($conf)>

=item *
Write accounts configuration to the 'accounts.conf' file

=item * 
$conf: a hash reference describing accounts configuration like this

{

	ACCOUNTTYPE1 => { 

	ATTRIBUTE1 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	ATTRIBUTE2 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	}

	ACCOUNTTYPE2 => {

	...

	}

}

=cut "


sub writeConfig {
	my $conf = shift;
	
	my $fd = open(FILE, ">accounts.conf");
	defined($fd) or &error($text{'err_writing_to'}." accounts.conf: $!");

	foreach my $ocs (keys %{$conf}) {
		print FILE "\n[$ocs]\n";
		foreach my $attr (keys %{$conf->{$ocs}}) {
			my $str = '';
			if ($conf->{$ocs}->{$attr}->{'forbidden'}) {
				$str .= '*'.$attr."=";
			} else {
				$str .= $attr."=";
			}
			if ($conf->{$ocs}->{$attr}->{'visible'} == 1) {
				$str .= '1,';
			} else {
				$str .= '0,';
			}
			if ($conf->{$ocs}->{$attr}->{'editable'} == 1) {
				$str .= '1,';
			} else {
				$str .= '0,';
			}
			if ($conf->{$ocs}->{$attr}->{'default'}) {
				$str .= $conf->{$ocs}->{$attr}->{'default'};
			} 
			print FILE "$str\n";
		}
	}
	close($fd);
}

=pod "

=item I<getConfiguredOcs($conf)>

=item *
Return an array with accounts types defined in the $conf reference

=item * 
$conf: a hash reference describing accounts configuration like this

{

	ACCOUNTTYPE1 => { 

	ATTRIBUTE1 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	ATTRIBUTE2 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	}

	ACCOUNTTYPE2 => {

	...

	}

}
 
=cut "
sub getConfiguredOcs {
	my $conf = shift;

	return keys %$conf;
}

=pod "

=item I<getConfiguredAttrs($conf, $ocs)>

=item *
Return an array with account attributes defined in the $conf reference

=item * 
$conf: a hash reference describing accounts configuration like this

{

	ACCOUNTTYPE1 => { 

	ATTRIBUTE1 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	ATTRIBUTE2 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	}

	ACCOUNTTYPE2 => {

	...

	}

}

=item *
$ocs: an objectclass name corresponding to a configured account type
 
=cut "
sub getConfiguredAttrs {
	my ($conf, $ocs) = (@_);
	
	return keys %{$conf->{$ocs}};
}

=pod "

=item I<printMenu($ldap, $conf, $user, $user_uid, $onglet, $base)>

=item *
Print a menu for the edit_user screen

=item *
$ldap: a Net::LDAP object

=item *
$conf: a hash reference describing accounts configuration like this

{
	ACCOUNTTYPE1 => { 

	ATTRIBUTE1 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	ATTRIBUTE2 => {

		visible => 0 or 1,

		editable => 0 or 1,

		default => default value for this attibute,

	},

	}

	ACCOUNTTYPE2 => {

	...

	}

}

=item *
$user: a Net::LDAP::Entry object corresponding to an user

=item *
$user_uid: user UID

=item *
$onglet: current requested item from menu

=item * 
$base: current selected base DN

=cut "

sub printMenu {
	my ($ldap, $conf, $user, $user_uid, $onglet, $base) = (@_);
	my @onglets = ("General", "Groups", "Profile");	
	print "<table><tr>\n";
	foreach (@onglets) {
		if ($_ eq $onglet) {
			print "<td><b><font color=blue>$_</font></b></td>\n";
		} else {
			print "<td><b><a href=edit_user.cgi?uid=$user_uid&onglet=$_&base=".&urlize($base).">$_</a></b></td>\n";
		}
	}
	my @cocs = &getConfiguredOcs($conf);
	my @ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
	foreach my $co (@cocs) {
		my $url = "edit_".lc($co).".cgi?uid=$user_uid&onglet=$co&base=".&urlize($base);
		if (indexof(uc($co), map(uc($_),@ocs)) != -1) {
			if ($co eq $onglet) {
				print "<td><b><font color=blue>".$text{$co}."</font></b></td>\n";
			} else {
				print "<td><b><a href=$url>".$text{$co}."</a></b></td>\n";
			}
		} else {
			if ($co eq $onglet) {
				print "<td><font color=blue>".$text{$co}."</font></td>\n";
			} else {
				print "<td><a href=$url&new=yes>".$text{$co}."</a></td>\n";
			}
		}
	}
	print "</tr></table>\n";
	print "<br>\n";
	
}

=pod "

=item I<pagesLinks($url, $numkeys, $current)>

=item *
Return pages links html code for search results that must be displayed on multiple pages

=item *
$url: the preformatted url base that these links should lead to

=item *
$numkeys: number of search results to be displayed

=item *
$current: current page number

=cut "


sub pagesLinks {
	my ($url, $numkeys, $current) = (@_);

	my $max = $config{'max_items'};
	my $num = int($numkeys / $max) + 1;

	my $pages = '';
	if ($num <=> 1) {
		$pages .= "page:  ";
		for (my $p = 1; $p <= $num; $p++) {
			if ($p == $current) {
				$pages .= "<a href=".$url."&page=$p><font color=blue><b>[$p]</b></font></a> ";
			} else {
				$pages .= "<a href=".$url."&page=$p>[$p]</a> ";
			}
		}
		$pages .= "<br><br>\n";
	}

	return $pages;
}

=pod "

=item I<printLDAPTree($link, $ldap, $base, $current)>

=item *
Print a tree (html code) corresponding to the LDAP OUs under the given $base,
the tree conssists of links which change the current base DN for search, creation...

=item *
$link: the preformatted url base that these links should lead to

=item *
$ldap: a Net::LDAP object

=item *
$base: base DN under which OU search must be performed

=item *
$current: current selected OU

=cut "


sub printLDAPTree {
	my ($link, $ldap, $base, $current) = (@_);
	print "<ul>";
	if ($base eq $current) {
		print "<b><font color=blue><li> <a href=$link?base=".&urlize($base)."><font color=blue>$base</font></a></font></b>";
	} else {
		print "<li> <a href=$link?base=".&urlize($base).">$base</a>";
	}
	my $attrs = [ 'ou' ];
	my $result = $ldap->search(
							   base => $base,
							   scope => "one",
							   filter => "objectClass=organizationalUnit",
							   attrs => $attrs,
							  );

	foreach my $ou ($result->entries) {
		&printLDAPTree($link, $ldap, $ou->dn, $current);
	}
	print "</ul>";
}


sub utf8Encode {
	my $arg = shift;
	
	return to_utf8(
				   -string=> $arg,
				   -charset => 'ISO-8859-1',
				  );
}

sub utf8Decode {
	my $arg = shift;
	
	return from_utf8(
					 -string=> $arg,
					 -charset => 'ISO-8859-1',
					);
}
			  
=pod "

=item I<LDAPChangeVirtual($ldap,$virtual)

=item *
Add/Remove/Modify VitualAccounts
return a Net::LDAP::Entry 

=item *
$ldap: a Net::LDAP object
$virtual: list of dcobjects


=cut"
sub LDAPChangeVirtual(){
	my ($ldap,$virtual) =@_;
	my $changes ={};
	$changes->{'associatedDomain'} = @virtual;
	my $res = $ldap->modify($config{'ldap_virtual_base'}, replace => { %$changes } );
	if ($res->code()) { 
		&error(&ldap_error_name($res->code).
			": ".&ldap_error_text($res->code)); 
	}

}
=pod "

=item I<LDAPGetVirtual($ldap)

=item *
return the Configured Domains
return a Net::LDAP::Entry 

=item *
$ldap: a Net::LDAP object


=cut"
sub LDAPGetVirtuals {
	my ($ldap) = (@_);
	$result = LDAPSearch($ldap,"(&(objectClass=dNSDomain)(objectClass=domainRelatedObject)(dc=domains))",
			['associatedDomain'],
			$config{'ldap_virtual_base'});
	if($result->count>1){
		&error($text{'err_vitual_too_many_base'});
	}
   my $entry = $result->entry;
   return $entry;
}

=pod "

=item I<LDAPGetDiscussao($ldap)

=item *
return the Discussion Lists
return a Net::LDAP::Entry 

=item *
$ldap: a Net::LDAP object


=cut"
sub LDAPGetDiscussao {
	my ($ldap) = (@_);
	$result = LDAPSearch($ldap,"(&(objectClass=qmailUser)(objectClass=top))",
			$attrs,
			$config{'ldap_discussao_base'});
	if($result->count>1){
		&error($text{'err_discussao_too_many_base'});
	}
   my $entry = $result->entry;
   return $entry;
}


# Generates salt
# Similar to Crypt::Salt module from CPAN
sub make_salt
  {
    my $length=32;
    $length = $_[0] if exists($_[0]);
  
    my @tab = ('.', '/', 0..9, 'A'..'Z', 'a'..'z');
    return join "",@tab[map {rand 64} (1..$length)];
  }
=pod "

=head1 AUTHORS

Gerald Macinenti - <gerald.macinenti@IDEALX.com>
Fernando Augusto Medeiros Sivla - <fams@linuxplace.com.br>

=cut "
