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
$access{'view_user_mail'} or &error($text{'acl_view_user_mail_msg'});
&ReadParse();

#use CGI;
use CGI::Ajax;

#my $cgi = new CGI;
my $pjx = new CGI::Ajax( 'qmailusersub' => 'ajax.cgi');

# input
my $user_uid = $in{'uid'};
my $onglet = $in{'onglet'};
my $base = $config{'ldap_users_base'};
#my $base = defined($in{'base'}) ? $in{'base'} : $config{'ldap_users_base'};

# initialize some variables
my $ldap = &LDAPInit();
my $conf = &parseConfig('accounts.conf');
my $creation = '';
my $sattrs = [];
my $url = "edit_".lc($onglet).".cgi?&base=".&urlize($base)."&uid=$user_uid&onglet=$onglet";

#recebe nova conta de email alternativo
if ($in{'add'}){
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    &MailCheck($ldap,\%in);
    my $result = &LDAPSearch($ldap, 
			 "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(objectClass=qmailUser)(uid=$user_uid))", 
			 $sattrs, 
			 $base);  
    if ($result->count > 1) {
        &error($text{'err_found_more_than_one_user'});
    }
    $attrs{'mail'} = $in{'mail_box'}.'@'.$in{'mail_domain'};
    if(&MailCreateCheck($ldap,$base,$attrs{'mail'})){
        &error($text{'err_mail_exists'});
    }
    my $entry = $result->entry;
    $entry->add(
         'mailAlternateAddress'=>$attrs{'mail'}
    );
    $entry->update($ldap);
}
if ($in{'changequota'}) { 
    $attrs{'mailQuota'}=$in{'mailquota'}."S";
    $attrs{'mailQuotaDovecot'}=int($in{'mailquota'}/1024);
    my $mailserver = new lxnclient;
    if(! $mailserver->connect('execscript',$config{remotemail})){
        &error($mailserver->{MSG});
    }
    #FIXME Nao eh desnecessário esse check acima?
    if(my $ret=$mailserver->exec("removequotafile $user_uid")){
        if($ret ==2){ &error($mailserver->{MSG});}
    }else{
        &error($mailserver->{MSG});
    }
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);	
}
#recebe alteracao de conta
if ($in{'change'}) {	
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my $attr = {};
    $attrs{'mail'} = $in{'mail_box'}.'@'.$in{'mail_domain'};
    &MailCheck($ldap,\%in);
    if(&MailCreateCheck($ldap,$base,$attrs{'mail'})&&!defined($in{'deletemail'})){
        &error($text{'err_mail_exists'});
    }
    if(defined($in{'primary'})){
        &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);
    }else{
        my $result = &LDAPSearch($ldap, 
			 "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=$user_uid))", 
			 $sattrs, 
			 $base);  
        if ($result->count > 1) {
            &error($text{'err_found_more_than_one_user'});
        }
       my $user = $result->entry;
        $old_mail=$in{'old_mail'};
        my @mail_alternates = ();
        foreach my $mailAlternate ($user->get_value('mailAlternateAddress')){
            push(@mail_alternates,$mailAlternate) unless ($mailAlternate eq $old_mail);
        }
        if(!defined($in{'deletemail'})){
            push(@mail_alternates,$attrs{'mail'});
        }
        $user->replace('mailAlternateAddress',\@mail_alternates);
        $user->update($ldap);
    }
    &webmin_log("modifying qmailmail account for user [$user_uid]",undef, undef,\%in);
}
my $result = &LDAPSearch($ldap, 
			 "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=$user_uid))", 
			 $sattrs, 
			 $base);  
if ($result->count > 1) {
    &error($text{'err_found_more_than_one_user'});
}
my $user = $result->entry;
if (!$user) { 
    &error($text{'err_could_not_find_user'}.": $user_uid"); 
}
#recebe criacao de conta master
if ($in{'create'}) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my $mail_box=$in{'mail_box'};
    my $mail_domain=$in{'mail_domain'}
    &MailCheck($ldap,\%in);
    $attrs{'mail'} = $in{'mail_box'}.'@'.$in{'mail_domain'};
    $attrs{'accountStatus'} = 'active';
    if ($config{'letterhomes'} == 1) {
        $homeletter = lc(substr($user_uid,0,1));
    	$attrs{'mailMessageStore'} = $config{'mailMessageStoreBase'}.$homeletter."/".$user_uid."/Maildir/";
    } else {
  	$attrs{'mailMessageStore'} = $config{'mailMessageStoreBase'}.$user_uid."/Maildir/";
    }
    $attrs{'mailQuota'}=$conf->{$onglet}->{'mailQuota'}->{'default'}."S";
    $attrs{'mailQuotaDovecot'}=int($conf->{$onglet}->{'mailQuota'}->{'default'}/1024);
    if(&MailCreateCheck($ldap,$base,$attrs{'mail'})){
        &error($text{'err_mail_exists'});
    }
    #FIXME bad design
    my @old_ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
    my @new_ocs = ();
    foreach (@old_ocs) {
    	push(@new_ocs, $_) unless ($_ eq 'qmailUser' || $_ eq 'hordePerson' );
    } 
    push(@new_ocs, 'qmailUser');
    #FIXME i need to find a better place to do it
    #Horde hack
    if ($config{'use_horde'}){
    	push(@new_ocs, 'hordePerson');
	$attrs{'hordePrefs'}=".";
	$attrs{'ImpPrefs'}=".";
	$attrs{'turbaPrefs'}=".";
    }else{
	$attrs{'hordePrefs'}=undef;
	$attrs{'ImpPrefs'}=undef;
	$attrs{'turbaPrefs'}=undef;
    }
	
    $attrs{'objectclass'} = \@new_ocs;
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);	
    &MailSanitizer($ldap, $base, $user_uid);
    $creation = "<font color=green>".$text{'edit_qmailuser_successfully_created'}."</font></br>\n";
    $result = &LDAPSearch($ldap, 
			  "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=$user_uid))", 
			  $sattrs, 
			  $base);  
    $user = $result->entry;
    &webmin_log("creating mail account for user [$user_uid]",undef, undef,\%in);
}
#Scripts para a pagina
$prebody .=<<EOF
<style type="text/css">
<!--
#wait{
position:absolute;
top:360px;
left:500px;
background-color:#200;
display:none;
}

.hidden{
display:none;
}
--></style>
EOF
;
$prebody .= <<EOF
<script type=text/javascript>
vrfymaildir = function (){
	//alert (arguments[0]);
    eval(arguments[0]);
    if(status[0] == false){
	document.getElementById('resultdiv').style.color = '#FF0000' ;
    	document.getElementById('createlink').style.display='inline';
    	document.getElementById('resultdiv').innerHTML="N&atilde;o existe a caixa postal";
		return true;
    }
	var html ="";
	html += (status[1])?"":"<li>N&atilde;o &eacute; um diret&oacute;rio</li>";
	html += (status[2])?"":"<li>Sem direito de leitura</li>";
	html += (status[3])?"":"<li>Sem direito de escrita</li>";
	if (html.length > 0) {
		document.getElementById('resultdiv').style.color = '#FF0000' ;
		document.getElementById('resultdiv').innerHTML="Os seguintes erros foram encontrados:<ul>";
		document.getElementById('resultdiv').innerHTML +=html;
		document.getElementById('resultdiv').innerHTML +="</ul><br/>Utilize um gerenciador de arquivos para resolver o problema";
	}else{
		document.getElementById('resultdiv').style.color = '#FF0000' ;
		document.getElementById('resultdiv').innerHTML="Maildir OK";
	}
};
mkmaildir = function (){
    //alert(arguments[0]);
    eval(arguments[0]);
    if(ret == true ){
        document.getElementById('createlink').style.display='none';
        document.getElementById('resultdiv').innerHTML="Diret&oacute;rio criado";
    }else{
        document.getElementById('resultdiv').innerHTML=msg;
    }
}
</script>
EOF
;
$prebody .= $pjx;
$prebody .= <<EOF
<script type=text/javascript>
// these 2 functions provide access to the javascript events. Since
// is an object anything here will apply to any div that uses a
// cgi::ajx registered function. as a convenience, we send in the id
// of the current element (el) below. but that can also be accessed
// this.target;
// if these are not defined, no problem...
pjx.prototype.pjxInitialized = function(el){
  document.getElementById('wait').innerHTML = "<p style='vertical-align:middle'>Carregando ...<img src='images/ani-busy.gif'></p>";
  document.getElementById('wait').style.backgroundColor = '#FFF';
  document.getElementById('wait').style.color = '#F00';
  document.getElementById('wait').style.valign = 'middle';
  document.getElementById('wait').style.display= 'block';
}

pjx.prototype.pjxCompleted = function(el){
  // here we use this.target:
  // since this is a prototype function, we have access to all of hte 
  // pjx obejct properties. 
  document.getElementById('wait').style.display = 'none';
}

</script>
EOF
;
&header($user_uid,"images/icon.gif","edit_qmailuser",1,undef,undef,undef,$prebody);

&printMenu($ldap, $conf, $user, $user_uid, $onglet, $base);
print "<div id='wait'></div>";

print "<table><tr><td><img src=images/user.gif></td>
<td><h1>$user_uid</h1></td><td>$creation</td></tr></table>\n";
print "<hr>\n";

print "<table width='80%'><tr><td><h2>".$text{'edit_qmailuser_qmail_user'}."</h2></td><td>\n";
if (!$in{'new'} && !$in{'delete'}) {
    print "<a href=$url&delete=yes>".$text{'edit_qmailuser_delete_account'}."</a>\n";
    print "<a href=\"javascript:qmailusersub( ['function__vrfymaildir' , 'mailuid__$user_uid'] , [ vrfymaildir ],[ 'POST' ]  );\">".$text{'edit_qmailuser_vrfydir'}."</a>\n";
    print "<a href=\"javascript:qmailusersub( ['function__mkmaildir' , 'mailuid__$user_uid'] , [ mkmaildir ],[ 'POST' ]  );\" id='createlink' class='hidden'>".$text{'edit_qmailuser_createdir'}."</a>\n";
}
print "</td></tr></table><br>\n";
print "<table width='80%'>\n";
#recebe delete
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
    &webmin_log("deleting email account for user [$user_uid]",undef, undef,\%in);
    print "<font color=green>".$text{'edit_qmailuser_deleted'}."</font></br>\n";
    print "</table>\n";
} elsif ($in{'new'}) {  #aqui ele mostra a tela de cadastro da primeira conta
    print "<tr><td colspan=2>".$text{'edit_qmailuser_infomsg'}."</td></tr>";
    print $str;
    print "<form action=$url method=post>";
    print "<tr><td colspan=2><br><br>".$text{'edit_qmailuser_primary_mail'}.":<input type=text name=mail_box value='$user_uid'>@";
    print "<select name=mail_domain> ";
    #Getting domains 
    my @domains = &LDAPGetVirtualDomains($ldap);
    foreach my $domain (@domains){
        print "<option value=$domain>$domain</option>\n";
    }
    print "</select>";
    print "</tr>\n";
    print "<tr><td colspan=2><br><br><input type=submit name=create value='".$text{'edit_qmailuser_create_account'}."'></td></tr>\n";
    print "</table>\n<br/>";
} else { #Mostra se ja tem conta
    print "</table>\n";
    print "<table width='80%'>";
    #Primary Account
    my $mail = &LDAPGetUserAttribute($ldap, $user, 'mail');
    ($mail_box,$mail_domain) = split('@',$mail);
    print "<tr><td><form action=$url&change method=post>".$text{'edit_qmailuser_primary_mail'}.":</td><td><input type=text name=mail_box value='$mail_box'>@";
    print "<select name=mail_domain> ";
    #Getting domains 
    my @domains = &LDAPGetVirtualDomains($ldap);
    foreach my $domain (@domains){
        if($domain =~/$mail_domain/i){
            print "<option selected value=$domain>$domain</option>\n";
        }else{
            print "<option value=$domain>$domain</option>\n";
        }
    }
    print "</select>";
    print "<input type=submit name=change value='".$text{'edit_qmailuser_mail_apply_changes'}."'>
    <input type=hidden name=primary value=yes></form></td></tr>\n";
    #/Primary Account
    #Alternate Account
    foreach my $mailAlternate ($user->get_value('mailAlternateAddress')){
    	($mail_box,$mail_domain) = split('@',$mailAlternate);
    	print "<tr><td nowrap><form action=$url&change method=post>".$text{'edit_qmailuser_alternate_mail'}.":</td><td nowrap ><input type=text name=mail_box value='$mail_box'>@";
    	print "<select name=mail_domain> ";
    	#Getting domains 
    	my @domains = &LDAPGetVirtualDomains($ldap);
	    foreach my $domain (@domains){
	        if($domain =~/$mail_domain/i){
	            print "<option selected value=$domain>$domain</option>\n";
	        }else{
	            print "<option value=$domain>$domain</option>\n";
	        }
	    }
	    print "</select>";
        print "<input type=hidden name=old_mail value='".$mail_box."@".$mail_domain."'>";
	    print "<input type=submit name=change value='".$text{'edit_qmailuser_mail_apply_changes'}."'>
	    <input type=hidden name=alternate value=yes></form>";
        print "<a href=$url&mail_box=".$mail_box.'&mail_domain='.$mail_domain."&old_mail=".$mail_box.'@'.$mail_domain."&deletemail=yes&change=yes>Delete</a>";
        print "</td></tr>\n";
    }
    #/Alternate
    print "<tr><td colspan='2'>&nbsp;</td></tr>";
    print "<tr><td nowrap><form action=$url method=post>";
    print $text{'edit_qmailuser_alternate_mail'}.":</td><td><input type=text name=mail_box value=''>@";
    print "<select name=mail_domain> ";
    #Getting domains 
    my @domains = &LDAPGetVirtualDomains($ldap);
    foreach my $domain (@domains){
        print "<option value=$domain>$domain</option>\n";
    }
    print "</select>";
    #print "<script>alert('".$old_mail."');</script>";
    print "<input type=submit name=add value='".$text{'edit_qmailuser_create_account'}."'></td></tr>\n";
    print "</table>
    <div id=\"resultdiv\"></div>
    <br>\n";
#<Quotasize>
$_=$user->get_value('mailQuota');
/(.*)S$/;
$quota=$1;

print "<hr><form action$url method=post>";
print "<table widht='80%'>";
print "  <tr>"; 
print "    <td>".$text{'edit_qmailuser_mail_quota'}."</td>";
print "    <td><input type=text name=mailquota value='".$quota."'>BYTES<input type=submit name=changequota value='".$text{'edit_qmailuser_change_quota'}."'></td>
          </tr>
       </table>";
#</Quotasize>
print <<EOF
</form>
EOF
;

}
    
&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base),$text{'list_users_return'});


###########
# functions
###########


sub LDAPGetVirtualDomains {
    $ldap = shift; 
	$entry= &LDAPGetVirtuals($ldap);
    my @virtual_domains=();
    foreach my $domain ($entry->get_value('associatedDomain')) {
      push (@virtual_domains,$domain);  
    }
    return @virtual_domains;
}
sub MailCheck{
    my ($ldap,$arg_in) = @_;
    my %in = %$arg_in;
    my @domains = &LDAPGetVirtualDomains($ldap);
    if(($in{'mail_box'} eq '')||($in{'mail_domain'} eq '' )){
        &error($text{'err_mail_domain_required'});
        exit 1;
    }
    if(!grep(/$in{'mail_domain'}/i,@domains)){
        &error($text{'err_mail_domain_nexist'});
            exit 1;
    }
    if(!($in{'mail_box'} =~ /[a-z0-9][a-z0-9\-_]*/i)){
        &error($text{'err_mail_box_invalid'});
        exit 1;
    }
    return 0;
}
sub MailCreateCheck{
    my ($ldap,$base,$mail) = @_;
    $result = &LDAPSearch($ldap, 
			  "(&(objectclass=qmailuser)(|(mail=$mail)(mailAlternateAddress=$mail)))",
			  'uid', 
			  $base);  
    return ($result->count > 0)? 1: 0;
}

sub MailSanitizer {
    my ($ldap,$base,$mailuid) = @_;
    my $result = &LDAPSearch($ldap,
			  "(&(objectclass=qmailuser)(uid=$mailuid))",
                             'mailMessageStore',
                             $base);
    if ($result->count > 1) {
        &error($text{'err_mail_box_invalid'});
    }
    my $diretorio = $result->entry->get_value('mailMessageStore');
    if(($diretorio=~/\.\./)or($diretorio=~/ /)){
        &error($text{'err_mail_box_invalid'});
    }
    # perform a nscd restart to be sure the user is known from the system
    my $nscd = $config{"nscd_path"};
    system("$nscd restart");
    my $mailserver = new lxnclient;
    if(! $mailserver->connect('execscript',$config{remotemail})){
        &error($mailserver->{MSG});
    }
    #FIXME Nao eh desnecessário esse check acima?

    if(my $ret=$mailserver->exec("mksmbdir $mailuid 1")){
        if($ret ==2){ &error($mailserver->{MSG});}
    }else{
        &error($mailserver->{MSG});
    }
    #get new prompt
    *WRITER = $mailserver->{WRITER};
    print WRITER "\n";
    if(my $ret=$mailserver->exec("mkmaildir $mailuid 1")){
        if($ret ==2){ &error($mailserver->{MSG});}
        return 1;
    }else{
        &error($mailserver->{MSG});
    }
    undef $mailserver;
}
