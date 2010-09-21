#!/usr/bin/perl


#  This code was developped by Linuxplace (http://www.linuxplace.com.br) based in 
#  prevrious work from IDEALX (http://IDEALX.org/) and
#  contributors (their names can be found in the CONTRIBUTORS file).
#
#                 Copyright (C) 2005 Linuxplace
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

# author: <fams@linuxplace.com.br>
# Version: $Id$

require './idxldapaccounts-lib.pl';
use utf8;
&ReadParse();
my %access = &get_module_acl();
$access{'configure_discussao'} or &error($text{'acl_configure_discussao_msg'});
#&header($text{'edit_discussao_title'},"images/discussao.gif","edit_discussao",1,1,undef,undef);


my $base = $config{'ldap_discussao_base'};
my $base_users = $config{'ldap_users_base'};
my $ldap = LDAPInit();
#my @Attrs = &LDAPGetObjectClasseAttributes($ldap, $account);
$action = $in{'action'};
action: {
#    my $listname = $in{'listname'};
#    my $listname = ($listname =~ /^\!(.*)/) ? $1 : $listname;

###EDIT
    $action =~ /^retrieve/ && do{
        my $search_type=$in{'search_type'};    
        my $search_pattern=$in{'search_pattern'};    
        my $search_attribute='cn';
        @mails = ();
        my $attrs = ['uid', 'mail', 'mailAlternateAddress','cn'];
        SWITCH:{
            if ($search_type =~ /^name/) { $search_attribute='cn' ; last SWITCH; }
            if ($search_type =~ /^uid/) { $search_attribute='uid' ; last SWITCH; }
            if ($search_type =~ /^mail/)  { $search_attribute='mail'; last SWITCH; }
            if ($search_type =~ /^sector/)  { $search_attribute='ou' ; last SWITCH; }
            $nothing=1;
        }
        my $result = &LDAPSearch($ldap,
            "(&(objectClass=qmailUser)($search_attribute=$search_pattern))",
            $attrs,
            $base_users);
            #@mails = $result->entries;
        @mails=sort {$a->get_value('cn') cmp $b->get_value('cn')} $result->entries;
        $xml_response="<?xml version=\"1.0\" ?>";
        $xml_response.="<maillist name=\"search\">";
        foreach my $_listau (@mails) {
            $xml_response.="<email name=\"".$_listau->get_value('mail')."\">".&html_escape($_listau->get_value('cn'))."</email>";
        }
        $xml_response.="</maillist>";
};
    $action =~ /^getListMembers/ && do{
        my $listuid = $in{'listuid'};
        my $listuid = ($listuid =~ /^\!(.*)/) ? $1 : $listuid; 
        @mails = ();
        my $attrs = ['uid', 'mail', 'mailForwardingAddress'];
        my $result = &LDAPSearch($ldap,
            "(&(objectClass=top)(objectClass=qmailUser)(uid=$listuid))",
            $attrs,
            $base);
        my $lista =$result->entry(0);
#@mails=sort {$a->get_value('mailForwardingAddress') cmp $b->get_value('mailForwardingAddress')} $result->entries;
#@mails=$result->entries; 
        $xml_response="<?xml version=\"1.0\" ?>";
        $xml_response.="<maillist name=\"$listname\">";
        
        foreach my $_listau ($lista->get_value('mailForwardingAddress')) {
            $xml_response.="<email name=\"".$_listau."\">".$_listau."</email>";
        }
        $xml_response.="</maillist>";
};
#Editando a lista via xmlrequest
    $action =~/^xmlrequest/ && do{
        use XML::DOM;
        $xml_request=$in[0];         
        my $parser = new XML::DOM::Parser;
        my $t=$parser->parse($xml_request);
        my($req_node)=$t->getElementsByTagName('request');#request_node
        my($list_node)=$t->getElementsByTagName('maillist');#mail_node
        my $listname=$list_node->getAttribute('name'); 
        $success = utf8::downgrade($listname, FAIL_OK); 
#&error($listname);  
        my $request=$req_node->getAttribute('type');#add ou remove
        my $dmembers=$t->getElementsByTagName('email');#colecao com os emails
        my $n = $dmembers->getLength;
        
#obter a lista atual
        
        my $attrs = [];
        my $result = &LDAPSearch($ldap,
            "(&(objectClass=top)(objectClass=qmailUser)(uid=".$listname."))",
            $attrs,
            $base);
        my $lista = $result->entry;    
        my @members =$lista->get_value('mailForwardingAddress');
#Email a serem Adicionados
        my @mail_request =();
        for (my $i = 0; $i < $n; $i++){           
            my $_tempmail=$dmembers->item($i)->getAttribute('value');
            $success = utf8::downgrade($_tempmail, FAIL_OK);
            push @mail_request, $_tempmail;
        }
        request:{
            $request =~ /^add/ && do{
                @newlist=(@members,@mail_request);
                @uniq = sort keys %{ { map { $_, 1 } @newlist } }; 
		@newlist = @uniq;

                last request;
            }; 
            $request =~ /^remove/ && do{
                @newlist=(); 
                foreach my $_tempmail (@members){
                    push(@newlist,$_tempmail) unless grep(/$_tempmail/,@mail_request);
                }
                last request;
            };  
        };           
        $lista->replace('mailForwardingAddress' => \@newlist);         
        $lista->update($ldap);
        $xml_response='<request><status value="success" /></request>';
}       
}
##show
print "pragma: no-cache\n";
print "Expires: Thu, 1 Jan 1970 00:00:00 GMT\n";
print "Cache-Control: no-store, no-cache, must-revalidate\n";
print "Cache-Control: post-check=0, pre-check=0\n";

print "Content-type: text/xml;charset=utf-8\n\n";
if ($xml_response=~/^$/){
        $xml_response='<request><status value="fail" /></request>';
}
print $xml_response;
