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
$access{'configure_discussao'} or &error($text{'acl_configure_discussao_msg'});
&ReadParse();
my $listname = $in{'listname'};
$action = $in{'action'};
if($action=~/^edit/){
	&header($text{'edit_discussao_title'},"images/discussao.gif","edit_discussao",1,undef,undef,undef,qq(<script src=discussao.js type=text/javascript></script>),qq(onLoad="getListMembers('$listname');"));
}else{
	&header($text{'edit_discussao_title'},"images/discussao.gif","edit_discussao",1,1,undef,undef,qq(<script src=discussao.js type=text/javascript></script>));
}

my $base = $config{'ldap_discussao_base'};
my $base_users = $config{'ldap_users_base'};
my $ldap = LDAPInit();
#my @Attrs = &LDAPGetObjectClasseAttributes($ldap, $account);
print "<style type=\"text/css\">
<!--
#wait{
position:absolute;
top:250px;
left:300px;
background-color:#FF8383;
height:50px;
width:120px;
display:none;
}
--></style>";
print "<div id=\"wait\">   Aguarde...</div>";
print "<form onsubmit=\"false;\">";
print "<table with='100%'>\n";
action: {
    my $listname = $in{'listname'};
    my $listname = ($listname =~ /^\!(.*)/) ? $1 : $listname;

###EDIT
    $action =~ /^edit/ && do{
        @lista = ();
    my $attrs = ['uid', 'mail', 'mailForwardingAddress'];
    my $result = &LDAPSearch($ldap,
        "(&(objectClass=top)(objectClass=qmailUser)(uid=$listname))",
        $attrs,
        $base);
    @lista = $result->entries;

    #   @lista_dusers = ();
    #my $attrs = ['uid', 'mail', 'mailAlternateAddress'];
#   my $result = &LDAPSearch($ldap,
#       "(&(objectClass=inetOrgPerson)(objectClass=qmailUser))",
#       $attrs,
#       $base_users);
#   @lista_dusers = $result->entries;

    print "<table border width=800>\n";
    print "<tr $tb> <td><b>$text{'edit_discussao_title'} $listname</b></td> </tr>\n";
    print "<tr $cb> <td><table width=100%>\n
    <tr><td colspan=\"3\">";
#search controls
    print "$text{'edit_discussion_search'}<br\\>    
    <input type=\"text\" name=\"search_pattern\" id=\"search_pattern\" maxlenght=\"20\" size=\"15\">
    <select name=\"search_type\" id=\"search_type\">
        <option value=name>$text{'edit_discussion_search_name'}</option>
        <option value=sector>$text{'edit_discussion_search_sector'}</option>
        <option value=mail>$text{'edit_discussion_search_mail'}</option>
    </select>
    <input type=\"button\" name=\"search\" onClick=\"searchDisp();\" value=$text{'edit_discussion_search_button'}> ";
    print "</td></tr>";
#search list 
    print "<td rowspan=10 width=\"40%\"><select id=\"mail_result\" name=\"mail_result\" multiple size=10>\n";
    print "<option>&nbsp;&nbsp;&nbsp;&nbsp;</option>"; 
    print "</select><br/>";
    print "<input id=\"mail_avulso\" name=\"mail_avulso\" type=\"text\" size=15 maxlenght=30 /> <input type=\"button\" value=\"".$text{'edit_discussao_include_member'}."\" onClick=\"listOperate('mail_avulso','$listname','add');\"/></td> \n";
     
    

    print "<td width=\"20%\">\n";
#print "<input type=submit value='".$text{'edit_discussao_include_member'}."' name=submit>\n";
   print "<input type=button onClick=\"listOperate('mail_result','$listname','add');\" value='".$text{'edit_discussao_include_member'}."' name=adicionar>\n";
#   print "<input type=hidden value=$domain_members name=add><BR><BR>\n";
#   print "</td><td>\n";
    print "<BR><BR>";


    print "<input type=button onClick=\"listOperate('list_members','$listname','remove');\" value='".$text{'edit_discussao_remove_member'}."' name=submit2 >\n";

    print "</td>\n";
    
#   print "$text{'edit_discussion_members_title'}\n";
    print "<td rowspan=10 width=\"40%\"><select id=\"list_members\" name=list_members multiple size=10>\n";

#    foreach my $_lista (@lista) {
#        foreach my $_temp_member ($_lista->get_value('mailForwardingAddress')) {
#            printf "<option value=\"$_temp_member\" %s> $_temp_member </option>\n",
            
            #print $_temp_member.'<BR>';
#        }
#}
    print "</select></td> \n";

    
    print "</tr></table></td></tr></table><p>\n";
    #print "<tr $cb><td><b>".$text{'edit_discussion_list'}."</b></td></tr>\n";
#    my $found="no";
#   foreach my $lvirtual ($entry->get_value('associatedDomain')) {
#           $lvirtual =~/^$virtual/ && do{
#            $found = "found";
#            print "<tr><td><input type=text name=newvirtual value='$lvirtual'>\n";
#            print "<input type=hidden name=oldvirtual value='$lvirtual'></td></tr>\n";
#        };
#    }
#    if ($found ne 'found'){
#        &error($text{'error_no_virtual'});
#    }
#   print "<tr><td><input type=submit value='".$text{'edit_virtual_save'}."' name=save>\n";
#    print "<input type=hidden value=save name=action></td></tr>\n";
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
        my $listname=$in{'listname'};
        if(defined($in{'confirm'})){
            my $res = $ldap->delete('uid='.$listname.','.$config{'ldap_discussao_base'});
            if ($res->code()) { 
                       &error(&ldap_error_name($res->code).
                   ": ".&ldap_error_text($res->code)); 
            }
        print "<tr><td>$virtual".$text{'edit_discussao_deleted'}."</td></tr>"; 
        }else{
            print "".$text{'edit_discussao_about_to_delete_discussao'}." $listname, ".$text{'edit_discussao_are_you_sure'}."<br>";
            print "<input type=submit name=confirm value=".$text{'delete_discussao_confirm'}.">";
            print "<input type=hidden name=action value='delete'>";
            print "<input type=hidden name=listname value='".$listname."'>";

        }
    last action  };
###NEW
    $action =~ /^new/ && do{
    print "<table border width=100%>\n";
    print "<tr $tb> <td><b>$text{'create_discussao_title'} </b></td> </tr>\n";
    print "<tr $cb><td><table width=100%>\n";
    print "<br>".$text{'create_discussion_name'}.":<input type=text name=list_name><td><br>";
    
    print $text{'create_discussao_mail'}.":<input type=text name=mail_box>@";
    print "<select name=mail_domain> ";
    #Getting domains
    my @domains = &LDAPGetVirtualDomains($ldap);
    foreach my $domain (@domains){
        print "<option value=$domain>$domain</option>\n";
        }
    print "</select></br>";
    print "</td></tr></table>\n";
    print "</table>\n";
    
    
    print "<input type=submit value='".$text{'create_discussao_save'}."' name=create>\n";
    print "<input type=hidden value=create name=action>\n";

    last action };
###ADD
    $action =~ /^add/ && do{
    @dmembers = split(//,$in{'domain_members'}); 
#    @dmembers = split(//,$in{'domain_members'});
        foreach my $members_to_include (@dmembers) {
            my $res = $ldap->modify('uid='.$listname.','.$config{'ldap_discussao_base'}, add => { 'mailForwardingAddress' => $members_to_include } );
            if ($res->code()) { 
                       &error(&ldap_error_name($res->code).
                   ": ".&ldap_error_text($res->code)); 
            }
        print "<tr><td>$virtual ".$text{'edit_discussao_added'}."</td></tr>"; 
    };
    last action };

#    $nothing = 1;
#};

###REMOVE
    $action =~ /^remove/ && do{
    my $listname = $in{'listname'};
    my $dn = "uid=$listname,$base";
    @rmembers = split(//,$in{'list_members'});
        foreach my $members_to_remove (@rmembers) {
            my $res = $ldap->modify($dn, delete => { 'mailForwardingAddress' => $members_to_remove } );
            if ($res->code()) { 
                       &error(&ldap_error_name($res->code).
                   ": ".&ldap_error_text($res->code)); 
            }
        print "<tr><td>$virtual ".$text{'edit_discussao_removed'}."</td></tr>"; 
    };
    last action };

#    $nothing = 1;
#};

###CREATE
    $action =~ /^create/ && do{
    my $newldomain = $in{'mail_domain'};
    my $newlist = $in{'list_name'};
    my $newlmail = $in{'mail_box'};
    my $dn = "uid=$newlist,$base";
    my $lmail = $newlmail.'@'.$newldomain;

    $result = $ldap->add( $dn,
                attr => [
            'objectClass'   =>  ['qmailUser','top','inetOrgPerson'],
            'mail'      =>  $lmail,
            'sn'        =>  '.',
            'cn'        =>  $newlist,
            'uid'       =>  $newlist,

            ]
    );
#           print $option;
#            my $res = $ldap->modify('uid='.$listname.','.$config{'ldap_discussao_base'}, add => { 'mailForwardingAddress' => $domain_members } );
#            if ($res->code()) { 
#                       &error(&ldap_error_name($res->code).
#                   ": ".&ldap_error_text($res->code)); 
#            }
#       print "<tr><td>$virtual ".$text{'edit_discussao_added'}."</td></tr>"; 
#    last action };
};

    $nothing = 1;
};

print "</table>";
print "</form>";

## FUNCTIONS
sub LDAPGetVirtualDomains {
    $ldap = shift;
    $entry= &LDAPGetVirtuals($ldap);
    my @virtual_domains=();
        foreach my $domain ($entry->get_value('associatedDomain')) {
              push (@virtual_domains,$domain);
            }
            return @virtual_domains;
};


&LDAPClose($ldap)
&footer('list_discussao.cgi',$text{'list_discussao_return'});
