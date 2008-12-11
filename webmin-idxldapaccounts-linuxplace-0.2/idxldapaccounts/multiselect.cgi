#!/usr/bin/perl


#  This code was developped by Linuxplace (http://www.linuxplace.com.br/) and
#  contributors (their names can be found in the CONTRIBUTORS file).
#
#                 Copyright (C) 2008 Linuxplace
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
# Version: $Id:$

require './idxldapaccounts-lib.pl';

&ReadParse();
my $field=$in{field};
my @remotes=split(/,/,$in{remotes});
popup_header();
print <<EOF
<script type=text/Javascript>
var hosts=0;
function addfield(name,addr){
 var hostname = document.createElement('input');
    var serverframe = document.getElementById('serverframe');
    var hostname=document.createElement('input');
    var hostaddr=document.createElement('input');
    hostname.id='hostname_'+hosts;
    hostaddr.id='hostaddr_'+hosts;
    hostname.size=15;
    hostaddr.size=15;
    hostname.value=name;
    hostaddr.value=addr;
    var br=document.createElement('br');
    serverframe.appendChild(hostname);
    serverframe.appendChild(hostaddr);
    serverframe.appendChild(br);
    hosts++;
}
function send(){
    var campos = '';
    for(x=0;x<hosts;x++){
        var hostname=document.getElementById('hostname_'+x);
        var hostaddr=document.getElementById('hostaddr_'+x);
		if(hostname.value != ''){
			campos = campos + hostname.value + ':' + hostaddr.value + ',';
		}
    }
    parentField=window.opener.document.getElementById('$field');
    parentField.value=campos;
    window.close();
}
</script>
<body>
<div name="serverframe" id="serverframe" >
<label style="float:left;width:150px">Nome</label>
<label style="float:left">Ip</label>
</br>

</div></br>
<script>

EOF
;
foreach(@remotes){
	my($host,$addr) = split(/:/);
	print "addfield('$host','$addr');";
}
print <<EOF
	addfield('','');</script>
<input type=button name=add value=add onClick="addfield('','')">
<input type=button name=send value=send onClick="send()">
EOF
;
popup_footer();
