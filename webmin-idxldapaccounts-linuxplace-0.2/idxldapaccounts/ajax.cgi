#!/usr/bin/perl
require './idxldapaccounts-lib.pl';
my $base = $config{'ldap_users_base'};
use CGI;

# initialize some variables
my $ldap = &LDAPInit();
my $q = new CGI;

print $q->header();
my %subs = (
                "vrfyftpdir"      => \&vrfyftpdir,
                "mkftpdir"      => \&mkftpdir,
                "vrfymaildir"      => \&vrfymaildir,
                "mkmaildir"      => \&mkmaildir,
            );

if( defined( $subs{$q->param('function')} ) ) {
    my $function = $q->param('function');
    my ( $ret , $msg ) = $subs{$function}( $q );
    if ( $ret == 0 ) {
        print "alert(\"ERROR: $msg\");";
    }else{
        print $msg;
    }
}else{
    print "alert('"."ERROR: $q->param('function') not defined"."');";
}

sub mkftpdir  {
    my $q = shift;
    my $ftpuid = $q->param("ftpuid");
    my $ftpserver=new lxnclient;
    if(! $ftpserver->connect('execscript', $config{remoteftp})){
        return  0 , $ftpserver->{MSG} ;
    }
    my $ret=$ftpserver->exec("mkftpdir $ftpuid");
    chomp $ftpserver->{MSG};
    my $html = qq(var msg = "$ftpserver->{MSG}" ;var ret=$ret;);
    return  $ret, $html ;
    undef $ftpserver;
}
sub vrfyftpdir  {
    my $q = shift;
    my $ftpuid = $q->param("ftpuid");
    my $ftpserver=new lxnclient;
    if(! $ftpserver->connect('execscript', $config{remoteftp})){
        return  0 , $ftpserver->{MSG} ;
    }
    if(my $ret=$ftpserver->exec("vrfyftpdir $ftpuid")){
    	split (/:/,$ftpserver->{MSG});
	shift;
	my $status = shift;
	my $html = "var status = new Array();";
	$html .= ( $status & 1 )?"status[0] = true;":"status[0]=false;";
	$html .= ( $status & 2 )?"status[1] = true;":"status[1]=false;";
	$html .= ( $status & 4 )?"status[2] = true;":"status[2]=false;";
	$html .= ( $status & 8 )?"status[3] = true;":"status[3]=false;";
        return  $ret, $html ;
    }else{
        return  0 , $ftpserver->{MSG} ;
    }
    undef $ftpserver;
}
sub mkmaildir  {
    my $q = shift;
    my $mailuid = $q->param("mailuid");
    #perform a nscd restart to be sure the user is known from the system
    my $nscd = $config{"nscd_path"};
    system("$nscd restart");
    my $mailserver=new lxnclient;
    if(! $mailserver->connect('execscript', $config{remotemail})){
        return  0 , $mailserver->{MSG} ;
    }
    my $ret=$mailserver->exec("mkmaildir $mailuid");
    chomp $mailserver->{MSG};
    my $html = qq(var msg = "$mailserver->{MSG}" ; var ret=$ret;);
    return  $ret, $html ;
    undef $mailserver;
}
sub vrfymaildir  {
    my $q = shift;
    my $mailuid = $q->param("mailuid");
    my $mailserver=new lxnclient;
    if(! $mailserver->connect('execscript', $config{remotemail})){
        return  0 , $mailserver->{MSG} ;
    }
    if(my $ret=$mailserver->exec("vrfymaildir $mailuid")){
    	split (/:/,$mailserver->{MSG});
	shift;
	my $status = shift;
	my $html = "var status = new Array();";
	$html .= ( $status & 1 )?"status[0] = true;":"status[0]=false;";
	$html .= ( $status & 2 )?"status[1] = true;":"status[1]=false;";
	$html .= ( $status & 4 )?"status[2] = true;":"status[2]=false;";
	$html .= ( $status & 8 )?"status[3] = true;":"status[3]=false;";
        return  $ret, $html ;
    }else{
        return  0 , $mailserver->{MSG} ;
    }
    undef $mailserver;
}
