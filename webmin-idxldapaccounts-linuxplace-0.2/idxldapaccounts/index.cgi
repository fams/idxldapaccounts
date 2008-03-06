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

&ReadParse()

&header('Idxldapaccounts',"images/icon.gif","intro",1,1);
print "<hr>\n";

my $error = &check_configuration_errors(); 
if (!$error) {	
    $conf = &parseConfig('accounts.conf');
    my @opts = ( 'users', 'groups', 'accounts');
    my @myocs=&getConfiguredOcs($conf);
#    &error(@myocs);

    if ($config{'use_discussao'}){
    	push(@opts,'discussao');
    }
    if (inArray('QMAILUSER',@myocs)){
    	push(@opts,'virtual');
    }
    @links = map { "list_${_}.cgi" } @opts;
    @titles = map { $text{"index_${_}_link"} } @opts;
    @icons = map { "images/${_}.gif" } @opts;
    &icons_table(\@links, \@titles, \@icons);
    my $warnings = &check_configuration_warnings();
    if ($warnings) {
	print "<font color=red>\n";
	foreach my $w (@$warnings) {
	    print $text{$w}."<br>\n";
	}
	print "</font>\n";
    }
} else {
    print $error;
}

sub check_configuration_errors {
    # LDAP parameters
    defined $config{'ldap_server'} or return $text{'err_missing_configuration_parameter'}.": LDAP server FQDN";
    defined $config{'ldap_admin'} or return $text{'err_missing_configuration_parameter'}.": LDAP administrator";
    defined $config{'ldap_password'} or return $text{'err_missing_configuration_parameter'}.": LDAP administrator password";

    # LDAP server connection
    my $ldap = Net::LDAP->new($config{'ldap_server'});
    defined $ldap or return $text{'err_contacting_ldap'};

    # LDAP server binding
    my $mesg = $ldap->bind(
			   dn => $config{'ldap_admin'},
			   password => $config{'ldap_password'});
    if ($mesg->code()) { 
	return &ldap_error_name($mesg->code).
	       ": ".&ldap_error_text($mesg->code).
	       "<br>".$text{'err_binding'}." [".
	       $config{'ldap_admin'}." | ".
	       $config{'ldap_password'}."]";
    }
    
    # LDAP users search base
    my $res = $ldap->search(
			    base => $config{'ldap_users_base'},
			    filter => '(objectclass=*)',
			    scope => "base"); 
    defined $res->entry() or return $text{'err_users_search_base_not_found'};

    # LDAP groups search base
    $res = $ldap->search(
			 base => $config{'ldap_groups_base'},
			 filter => '(objectclass=*)',
			 scope => "base"); 
    defined $res->entry() or return $text{'err_groups_search_base_not_found'};

    # everything is OK
    $ldap->unbind;
    return undef;
}

sub check_configuration_warnings {
    my @warnings = ();
    
    # check LDAP schema
    require Net::LDAP::Schema;
    require Data::Dumper;
    my $ldap = Net::LDAP->new($config{'ldap_server'});
    $ldap->bind(
		dn => $config{'ldap_admin'},
		password => $config{'ldap_password'});

    my $schema = $ldap->schema();
	if (defined $schema) {
		defined $schema->objectclass('sambaSamAccount') or push(@warnings, 'warn_sambaaccount_not_defined');
	} else {
		push(@warnings, 'warn_unable_to_read_LDAP_schema');
	}


    $ldap->unbind();
    return \@warnings;
}

&footer('/', $text{'index_return'});




