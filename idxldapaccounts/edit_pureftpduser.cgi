#!/usr/bin/perl
#

#  This code was developped by Linuxplace (http://www.linuxplace.com.br) and
#  contributors (their names can be found in the CONTRIBUTORS file).
#
#                 Copyright (C) 2007 Linuxplace
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

# author: Fernando Augusto <fams@linuxplace.com.br>
# Version: $Id$

require './idxldapaccounts-lib.pl';
my %access = &get_module_acl();
$access{'view_user_ftp'} or &error($text{'acl_view_user_ftp_msg'});
&ReadParse();

#use CGI;
use CGI::Ajax;

#my $cgi = new CGI;
my $pjx = new CGI::Ajax( 'pureftpdsub' => 'ajax.cgi');


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


if ($in{'change'}) {    
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my $attr = {};
    $FTPStatus = defined($in{'FTPStatus'}) ? "enabled" : "disabled" ;
    $attr{'FTPStatus'}=$FTPStatus;
    $attr{'FTPQuotaFiles'}=$in{'FTPQuotaFiles'};
    $attr{'FTPQuotaMBytes'}=$in{'FTPQuotaMBytes'};
    $attr{'FTPUploadRatio'}=$in{'FTPUploadRatio'};
    $attr{'FTPDownloadRatio'}=$in{'FTPDownloadRatio'};
    $attr{'FTPUploadBandwidth'}=$in{'FTPUploadBandwidth'};
    $attr{'FTPDownloadBandwidth'}=$in{'FTPDownloadBandwidth'};
    $attr{'FTPdir'}=$in{'FTPdir'} ;

    &LDAPModifyUser($ldap, $base, $user_uid, \%attr);
    &webmin_log("modifying FTP account for user [$user_uid]",undef, undef,\%in);
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
if ($in{'create'}) {
    $access{'edit_user'} or &error($text{'acl_edit_user_msg'});
    my %attrs;
    $attrs{'FTPStatus'}='enabled';
    $attrs{'FTPQuotaFiles'}=$in{'FTPQuotaFiles'};
    $attrs{'FTPQuotaMBytes'}=$in{'FTPQuotaMBytes'};
    $attrs{'FTPUploadRatio'}=$in{'FTPUploadRatio'};
    $attrs{'FTPDownloadRatio'}=$in{'FTPDownloadRatio'};
    $attrs{'FTPUploadBandwidth'}=$in{'FTPUploadBandwidth'};
    $attrs{'FTPDownloadBandwidth'}=$in{'FTPDownloadBandwidth'};
    $attrs{'FTPdir'}=$in{'FTPdir'} ;
    my @old_ocs = &LDAPGetUserAttributes($ldap, $user, 'objectclass');
    my @new_ocs = ();
    foreach (@old_ocs) {
    push(@new_ocs, $_) unless ($_ eq 'PureFTPduser');
    } 
    push(@new_ocs, 'PureFTPduser');
    #&error(@new_ocs);
    $attrs{'objectclass'} = \@new_ocs;
    &LDAPModifyUser($ldap, $base, $user_uid, \%attrs);    
    $creation = "<font color=green>".$text{'edit_pureftp_successfully_created'}."</font></br>\n";
    $result = &LDAPSearch($ldap, 
              "(&(objectClass=inetOrgPerson)(objectClass=posixAccount)(uid=$user_uid))", 
              $sattrs, 
              $base);  
    $user = $result->entry;
    FtpSanitizer($ldap, $base, $user_uid);    
    &webmin_log("creating ftp account for user [$user_uid]",undef, undef,\%in);
}
#Scripts para a pagina
$prebody .=<<EOF
<style type="text/css">
<!--
#wait{
position:absolute;
top:360px;
left:500px;
background-color:#FF8383;
display:none;
}
#btmkftpdir{
display:none;
}
--></style>
EOF
;
$prebody .= <<EOF
<script type=text/javascript>
vrfyftpdir = function (){
    eval(arguments[0]);
    if(status[0] == false){
    	document.getElementById('btmkftpdir').style.display='block';
    	document.getElementById('resultdiv').innerHTML="N&atilde;o existe o diret&oacute;rio";
    }
};
mkftpdir = function (){
    //alert(arguments[0]);
    eval(arguments[0]);
    alert('fams');
    if(ret == true ){
    	document.getElementById('btmkftpdir').style.display='none';
    	document.getElementById('resultdiv').innerHTML="Diret&oacute;rio criado";
    }else{
    alert('fams2');
    	document.getElementById('resultdiv').innerHTML=msg;
    }
    alert('fams3');
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
  document.getElementById('wait').style.backgroundColor = '#F66';
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
&header($user_uid,"images/icon.gif","edit_pureftpduser",1,undef,undef,undef,$prebody);

&printMenu($ldap, $conf, $user, $user_uid, $onglet, $base);
print "<div id='wait'></div>";
print "<table><tr><td><img src=images/user.gif></td>
<td><h1>$user_uid</h1></td><td>$creation</td></tr></table>\n";
print "<hr>\n";

print "<table width='80%'><tr><td><h2>".$text{'edit_pureftp_ftp_account'}."</h2></td><td>\n";
if (!$in{'new'} && !$in{'delete'}) {
    print "<a href=$url&delete=yes>".$text{'edit_pureftp_delete_account'}."</a>\n";
}
print "</td></tr></table><br>\n";
print "<form action=$url method=post>\n";
print "<table width='70%' class='ftptable'>\n";

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
    &webmin_log("deleting FTP account for user [$user_uid]",undef, undef,\%in);
    print "<font color=green>".$text{'edit_pureftp_deleted'}."</font></br>\n";
} elsif ($in{'new'}) {
###
#Form de criacao de conta ftp
#
$pureftp_quotafiles=$conf->{$onglet}->{'FTPQuotaFiles'}->{'default'};
$pureftp_quotambytes=$conf->{$onglet}->{'FTPQuotaMBytes'}->{'default'};
$pureftp_uploadratio=$conf->{$onglet}->{'FTPUploadRatio'}->{'default'};
$pureftp_downloadratio=$conf->{$onglet}->{'FTPDownloadRatio'}->{'default'};
$pureftp_uploadbandwidth=$conf->{$onglet}->{'FTPUploadBandwidth'}->{'default'};
$pureftp_downloadbandwidth=$conf->{$onglet}->{'FTPDownloadBandwidth'}->{'default'};
$pureftp_dir=$conf->{$onglet}->{'FTPdir'}->{'default'};
if($pureftp_dir=~/^\//){
    $pureftp_dir=~s/USERNAME/$user_uid/;
}else{
    my $homedir = &LDAPGetUserAttribute($ldap, $user, 'homedirectory');    
    $pureftp_dir="$homedir/$pureftp_dir";
}

print "<tr><td>".$text{'edit_pureftp_quotafiles'}."</td>
    <td><input type=text name=\"FTPQuotaFiles\" value=\"$pureftp_quotafiles\"></td></tr>";
print "<tr><td>".$text{'edit_pureftp_quotambytes'}."</td>
    <td><input type=text name=\"FTPQuotaMBytes\" value=\"$pureftp_quotambytes\"></td></tr>";
print "<tr><td>".$text{'edit_pureftp_uploadratio'}."</td>
    <td><input type=text name=\"FTPUploadRatio\" value=\"$pureftp_uploadratio\"></td></tr>";
print "<tr><td>".$text{'edit_pureftp_downloadratio'}."</td>
    <td><input type=text name=\"FTPDownloadRatio\" value=\"$pureftp_downloadratio\"></td></tr>";
print "<tr><td>".$text{'edit_pureftp_uploadbandwidth'}."</td>
    <td><input type=text name=\"FTPUploadBandwidth\" value=\"$pureftp_uploadbandwidth\"></td></tr>";
print "<tr><td>".$text{'edit_pureftp_downloadbandwidth'}."</td>
    <td><input type=text name=\"FTPDownloadBandwidth\" value=\"$pureftp_downloadbandwidth\"></td></tr>";
print "<tr><td>".$text{'edit_pureftp_dir'}."</td>
    <td><input type=text name=\"FTPdir\" value=\"$pureftp_dir\"></td></tr>";
print "</table>\n";
    

print $str;
print "<br><br><input type=submit name=create value='".$text{'edit_pureftp_create_account'}."'>\n";
} else {
    my $FTPStatus = &LDAPGetUserAttribute($ldap, $user, 'FTPStatus');
    my $pureftp_quotafiles = &LDAPGetUserAttribute($ldap, $user, 'FTPQuotaFiles');
    my $pureftp_quotambytes = &LDAPGetUserAttribute($ldap, $user, 'FTPQuotaMBytes');
    my $pureftp_uploadratio = &LDAPGetUserAttribute($ldap, $user, 'FTPUploadRatio');
    my $pureftp_downloadratio = &LDAPGetUserAttribute($ldap, $user, 'FTPDownloadRatio');
    my $pureftp_uploadbandwidth = &LDAPGetUserAttribute($ldap, $user, 'FTPUploadBandwidth');
    my $pureftp_downloadbandwidth = &LDAPGetUserAttribute($ldap, $user, 'FTPDownloadBandwidth');
    my $pureftp_dir = &LDAPGetUserAttribute($ldap, $user, 'FTPdir');
    #form de alteracao

    print "<tr><td>".$text{'edit_pureftp_quotafiles'}."</td>
        <td><input type=text name=\"FTPQuotaFiles\" value=\"$pureftp_quotafiles\"></td></tr>";
    print "<tr><td>".$text{'edit_pureftp_quotambytes'}."</td>
        <td><input type=text name=\"FTPQuotaMBytes\" value=\"$pureftp_quotambytes\"></td></tr>";
    print "<tr><td>".$text{'edit_pureftp_uploadratio'}."</td>
        <td><input type=text name=\"FTPUploadRatio\" value=\"$pureftp_uploadratio\"></td></tr>";
    print "<tr><td>".$text{'edit_pureftp_downloadratio'}."</td>
        <td><input type=text name=\"FTPDownloadRatio\" value=\"$pureftp_downloadratio\"></td></tr>";
    print "<tr><td>".$text{'edit_pureftp_uploadbandwidth'}."</td>
        <td><input type=text name=\"FTPUploadBandwidth\" value=\"$pureftp_uploadbandwidth\"></td></tr>";
    print "<tr><td>".$text{'edit_pureftp_downloadbandwidth'}."</td>
        <td><input type=text name=\"FTPDownloadBandwidth\" value=\"$pureftp_downloadbandwidth\"></td></tr>";
    print "<tr><td>".$text{'edit_pureftp_dir'}."</td>
        <td><input type=text name=\"FTPdir\" value=\"$pureftp_dir\"></td></tr>";
    print "</table>\n";
    print <<EOF
<input type="button" value="Verificar diretorio" onclick="pureftpdsub( ['function__vrfyftpdir' , 'ftpuid__$user_uid'] , [ vrfyftpdir ],[ 'POST' ]  );"/>
<input type="button" id="btmkftpdir" value="Criar Diret&oacute;rio" onclick="pureftpdsub( ['function__mkftpdir' , 'ftpuid__$user_uid'] , [ mkftpdir ],[ 'POST' ]  );"/>
<div id="resultdiv"></div>
EOF
;
    print $str;
    if ($FTPStatus =~ /^disabled/ ) {
        print "<input type=checkbox name='FTPStatus'> ".$text{'edit_pureftp_is_enabled'};
    } else {
        print "<input type=checkbox name='FTPStatus' checked> ".$text{'edit_pureftp_is_enabled'};
    }
    print "<br><br><input type=submit name=change value='".$text{'edit_pureftp_apply_changes'}."'>\n";
}
print "</form>\n";
    
&LDAPClose($ldap);
&footer("list_users.cgi?base=".&urlize($base),$text{'list_users_return'});


###########
# functions
###########
sub FtpSanitizer{
    my ($ldap,$base,$ftpuid) = @_;
    my $result = &LDAPSearch($ldap,
                          "(&(objectclass=qmailuser)(uid=$ftpuid))",
                             'ftpDir',
                             $base);
    if ( $result->count > 1 ) {
        &error($text{'err_pureftp_account_invalid'});
    }
    my $diretorio = $result->entry->get_value('ftpDir');
    if(($diretorio=~/\.\./)or($diretorio=~/ /)){
        &error($text{'err_pureftp_invalid_path'});
    }
    my $ftpserver = new lxnclient;     
    if(! $ftpserver->connect('execscript',$config{remoteftp})){
        &error($ftpserver->{MSG});
    }

    if(my $ret=$ftpserver->exec("mkftpdir $ftpuid 1")){
    	if($ret == 2){ &error($ftpserver->{MSG});}
        return 1;
    }else{
        &error($ftpserver->{MSG});
    }
    undef $ftpserver;
}
