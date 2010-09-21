// global flag
/*Suporte a lista de discussao, ajax primário
# author: <fams@linuxplace.com.br>
# Version: $Id$
*/

var isIE = false;

// global request and XML document objects
var reqGet;
var reqSend;
if (window.XMLHttpRequest) {
    isIE = false;    
} else if (window.ActiveXObject) {
    isIE = true;
}
function loadXMLDoc(url,changefunc) {
    // branch for native XMLHttpRequest object
    if (window.XMLHttpRequest) {
        reqGet = new XMLHttpRequest();
        reqGet.onreadystatechange = changefunc;
        reqGet.open("GET", url, true);
        reqGet.send(null)
    // branch for IE/Windows ActiveX version
    } else if (window.ActiveXObject) {
        isIE = true;
        reqGet = new ActiveXObject("Microsoft.XMLHTTP");
        if (reqGet) {
            reqGet.onreadystatechange = changefunc;
            reqGet.open("GET", url, true);
            reqGet.send();
        }
    }
}


//Adicionar/editar
function createXMLFromString (string) {
    var xmlParser, xmlDocument;
    if(isIE){
        try {    
            xmlDocument = new ActiveXObject('Msxml2.DOMDocument');
            xmlDocument.async = false;
            xmlDocument.loadXML(string);
            return xmlDocument;
        }   
        catch (e) {
            alert("Can't create XML document.2");
            return null;
        } 
    }else{
        try {
            xmlParser = new DOMParser();
            xmlDocument = xmlParser.parseFromString(string, 'text/xml');
            return xmlDocument;
        }
        catch (e) {
            alert("Can't create XML document.");
            return null;
        }
    }
}

function serializeXML (xmlDocument) {
    var xmlSerializer;
    if(isIE){
        return xmlDocument.xml;
    }else{
        try {
            xmlSerializer = new XMLSerializer();
            return xmlSerializer.serializeToString(xmlDocument);
        }
        catch (e) {
            alert("Can't serialize XML document.");
            return '';
        }
    }
}

function postXML (url, xmlDocument) {
    if(isIE){
        try {
            httpRequest = new ActiveXObject('Msxml2.XMLHTTP');
            httpRequest.open('POST', url, false);
            httpRequest.send(xmlDocument);
            return httpRequest;
        }
        catch (e) {
            alert("Can't post XML document.");
            return null;
        }
    }else{
        try {
            var httpRequest = new XMLHttpRequest();
            httpRequest.open('POST', url, false);
            httpRequest.send(xmlDocument);
            return httpRequest;
        }
        catch (e) {
            alert("Can't post XML document");
            return null;
        }
    }       
}
//Create Request
function listOperate(select,lista,operation){
    var wait=document.getElementById("wait");
    wait.style.display="block";
    var xmlDocument = createXMLFromString('<request type="'+operation+'"></request>');
        if (xmlDocument) {
            //Criando lista
            var listaElement = xmlDocument.createElement('maillist');
            listaElement.setAttribute('name', lista);
            //Preenchendo
            
            var mail_select = document.getElementById(select);
            if(mail_select.type=='text'){
                var mailElement = xmlDocument.createElement('email');
                mailElement.setAttribute('value', mail_select.value);
                listaElement.appendChild(mailElement);
            }else{               
                for(i=0;i < mail_select.length;i++){
                    if(mail_select.options[i].selected==true){
                        var mailElement = xmlDocument.createElement('email');
                        mailElement.setAttribute('value', mail_select.options[i].value);
                        listaElement.appendChild(mailElement);
                    }
                }
            }
            xmlDocument.documentElement.appendChild(listaElement);
            //alert(serializeXML(xmlDocument));
            var httpRequest = postXML('proc.cgi?action=xmlrequest', xmlDocument);
            if (httpRequest) {
                var req_result = reqGet.responseXML.getElementsByTagName('status');
                /*if (! req_result[0].getAttribute('value')=='ok'){
                    alert('Falha Ao executar operacao');
            }*/
                getListMembers(lista);
            }

        }
    
}


//Retrieve
function getListMembers(lista){
    loadXMLDoc("proc.cgi?action=getListMembers&listuid="+lista,procListMemberResult);
}

function procListMemberResult() {
    // only if reqGet shows "loaded"

    if (reqGet.readyState == 4) {
   // only if "OK"
        if (reqGet.status == 200) {
            clearMemberList();
            buildMemberList();
            var wait=document.getElementById("wait");
            wait.style.display="none";
        } else {
            alert("There was a problem retrieving the XML data:\n" +
                    reqGet.statusText);
        }
    }
}
function clearMemberList() {
    var select = document.getElementById("list_members");
    while (select.length > 0) {
        select.remove(0);
    }
}
function buildMemberList() {
    var select = document.getElementById("list_members");
    var items = reqGet.responseXML.getElementsByTagName("email");
    // loop through <item> elements, and add each nested
    // <title> element to Topics select element
    for (var i = 0; i < items.length; i++) {
    	if(isIE){
            appendToSelect(select, items[i].text,items[i].text);
	    }else{
            appendToSelect(select, items[i].textContent,items[i].textContent);
        }
    }
}


//Search
function searchDisp(){
    var search_pattern=document.getElementById("search_pattern");
    var search_type=document.getElementById("search_type");
    var wait=document.getElementById("wait");
    wait.style.display="block";
    loadXMLDoc("proc.cgi?action=retrieve&search_type="+search_type.value+"&search_pattern="+search_pattern.value,procDispResult);
}

function procDispResult() {
    // only if reqGet shows "loaded"

   if (reqGet.readyState == 4) {
   // only if "OK"
    if (reqGet.status == 200) {
            clearDispList();
            buildDispList();
         } else {
            alert("There was a problem retrieving the XML data:\n" +
            reqGet.statusText);
         }
    }
}
function clearDispList() {
    var select = document.getElementById("mail_result");
    while (select.length > 0) {
        select.remove(0);
    }
}
function buildDispList() {
    var select = document.getElementById("mail_result");
    var items = reqGet.responseXML.getElementsByTagName("email");
    var wait = document.getElementById("wait");
    //alert(reqGet.responseText);
    // loop through <item> elements, and add each nested
    // <title> element to Topics select element
    for (var i = 0; i < items.length; i++) {
    	if(isIE){
            appendToSelect(select, items[i].getAttribute('name'),items[i].text);
	    }else{
            appendToSelect(select, items[i].getAttribute('name'),items[i].textContent);
        }
    }
    wait.style.display= 'none';
}
// add item to select element the less
// elegant, but compatible way.
function appendToSelect(select, value, text) {
    var opt;
    opt = document.createElement("option");
    opt.value = value;
    opt.text=text;
    if(isIE){
        select.add(opt);
    }else{
        select.appendChild(opt);
    }
}
