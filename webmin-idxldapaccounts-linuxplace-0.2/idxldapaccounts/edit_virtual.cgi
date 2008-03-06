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
$access{'configure_virtual'} or &error($text{'acl_configure_virtual_msg'});
&header($text{'edit_virtual_title'},"images/icon.gif","edit_virtual",1,undef,undef);



my $ldap = LDAPInit();
#my @Attrs = &LDAPGetObjectClasseAttributes($ldap, $account);

print "<form action=edit_virtual.cgi method=post>";
print "<table with='100%'>\n";
$action = $in{'action'};
action: {
    my $virtual = $in{'virtual'};
    my $virtual = ($virtual =~ /^\!(.*)/) ? $1 : $virtual;

###EDIT
    $action =~ /^edit/ && do{
	$entry= &LDAPGetVirtuals($ldap);
	print "<tr $cb><td><b>".$text{'edit_virtual_domain'}."</b></td></tr>\n";
    my $found="no";
	foreach my $lvirtual ($entry->get_value('associatedDomain')) {
       	$lvirtual =~/^$virtual/ && do{
            $found = "found";
            print "<tr><td><input type=text name=newvirtual value='$lvirtual'>\n";
            print "<input type=hidden name=oldvirtual value='$lvirtual'></td></tr>\n";
        };
    }
    if ($found ne 'found'){
        &error($text{'error_no_virtual'});
    }
    print "<tr><td><input type=submit value='".$text{'edit_virtual_save'}."' name=save>\n";
    print "<input type=hidden value=save name=action></td></tr>\n";
    last action  };
###Save
    $action =~ /^save/ && do{
    my $newvirtual = $in{'newvirtual'};
    my $oldvirtual = $in{'oldvirtual'};
    if ( $newvirtual =~ /^[a-z0-9-]+(\.[_a-z0-9-]+)*(\.([a-z]{2,3}))+$/i){
	$entry= &LDAPGetVirtuals($ldap);
        my $found="no";
	print $newvirtual;
        my @new_virtuals=(); 
	    foreach my $lvirtual ($entry->get_value('associatedDomain')) {
            push(@new_virtuals,$lvirtual) unless ($lvirtual =~ /$oldvirtual/);
        }
        push(@new_virtuals,$newvirtual);
        my $changes;
        $changes->{'associatedDomain'} = \@new_virtuals;
        my $res = $ldap->modify($config{'ldap_virtual_base'}, replace => { %$changes } );
        if ($res->code()) { 
            &error(&ldap_error_name($res->code).
                   ": ".&ldap_error_text($res->code)); 
        }
    }
    last action  };
 ###DELETE
    $action =~ /^delete/ && do{
        $virtual=$in{'virtual'};
        if(defined($in{'confirm'})){
	        $entry= &LDAPGetVirtuals($ldap);
            my $found="no";
            my @new_virtuals=(); 
	        foreach my $lvirtual ($entry->get_value('associatedDomain')) {
                push(@new_virtuals,$lvirtual) unless ($lvirtual =~ /$virtual/);
            }
            my $changes;
            $changes->{'associatedDomain'} = \@new_virtuals;
            my $res = $ldap->modify($config{'ldap_virtual_base'}, replace => { %$changes } );
            if ($res->code()) { 
                       &error(&ldap_error_name($res->code).
                   ": ".&ldap_error_text($res->code)); 
            }
	    print "<tr><td>$virtual".$text{'edit_virtual_deleted'}."</td></tr>"; 
        }else{
            print "".$text{'edit_virtual_about_to_delete_virtual'}." $virtual, ".$text{'edit_virtual_are_you_sure'}."<br>";
            print "<input type=submit name=confirm value=".$text{'delete_user_confirm'}.">";
            print "<input type=hidden name=action value='delete'>";
            print "<input type=hidden name=virtual value='".$virtual."'>";

        }
    last action  };
###NEW
    $action =~ /^new/ && do{
	print "<tr $cb><td><b>".$text{'edit_virtual_domain'}."</b></td></tr>\n";
    print "<tr><td><input type=text name=virtual value='$lvirtual'>\n";
    print "<tr><td><input type=submit value='".$text{'edit_virtual_save'}."' name=add>\n";
    print "<input type=hidden value=add name=action></td></tr>\n";
    last action };
###ADD
    $action =~ /^add/ && do{
            my $res = $ldap->modify($config{'ldap_virtual_base'}, add => { 'associatedDomain' => $virtual } );
            if ($res->code()) { 
                       &error(&ldap_error_name($res->code).
                   ": ".&ldap_error_text($res->code)); 
            }
	    print "<tr><td>$virtual ".$text{'edit_virtual_created'}."</td></tr>"; 
    last action };

    $nothing = 1;
}

print "</table>";
print "</form>";

&LDAPClose($ldap)
&footer('list_virtual.cgi',$text{'list_virtual_return'});

