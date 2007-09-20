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
#
# Author: <gerald.macinenti@IDEALX.com>
# Version: $Id$

require 'idxldapaccounts-lib.pl';

my @acl_var = (
	       "configure_account",
	       "view_user_tech",
	       "view_user_ftp",
	       "view_user_perso",
	       "view_group",
	       "edit_user",
	       "edit_group",
	       "create_user",
	       "delete_user",
	       "create_group",
	       "delete_group",
	       );

sub acl_security_form
{
	my $access = shift;
	foreach my $acl (@acl_var) {
		print "<tr><td colspan=3>". $text{"acl_".$acl}."</td>\n";
		print "<td>";
		print "<input type=radio name=$acl value=1 ".
			(($access->{$acl}) ? 'checked' : '' ) .
				">".$text{'yes'};
		print "<input type=radio name=$acl value=0 ".
			(($access->{$acl}) ? '': 'checked' ) .
				">".$text{'no'};
		print "</td>\n";
		print "</tr>\n";
	}
}

sub acl_security_save
{
	my $access  = shift;
	my $in 		= shift;
	foreach (@acl_var) {
		$access->{$_} = $in->{$_};
	}
}

1;

