#!/usr/bin/perl
sub multiremote{
	my($field,$value) = @_;
	"<input type=hidden name=$field  id=$field value='$value'>
	<input type=button value=\"Select Hosts\" onClick=\"var $field=document.getElementById(\'$field\');window.open('idxldapaccounts/multiselect.cgi?field=$field&remotes='+$field.value,'page','toolbar=no,location=no,status=no,menubar=no,scrollbars=no,resizable=no,width=320,height=300');\">";
}
sub show_multisamba{
	my ($value) =@_;
	&multiremote('remotesmb',$value);
}
sub parse_multisamba{
	return $in{remotesmb};
}
1;
