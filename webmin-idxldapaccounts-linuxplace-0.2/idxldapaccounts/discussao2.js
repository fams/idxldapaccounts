var isIE = false;
// global request and XML document objects
var reqGet;
var reqSend;

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

function listReq(){
	this.tipo= "add";
	this.elementos= new Array();
	this.encoding="iso-8859-1";
	this.header="<\?xml version='1.0' encoding='"+this.encoding+"'\?>\n"
	this.add = listReqAdd;
	this.getXml=listReqGetXml;
}
function listReqAdd(value){
	this.elementos.push(value);
}
function listReqGetXml(){
	var i=0;
	var xmlDoc=this.header;
	xmlDoc+="<request>\n";
	switch(this.tipo){
		case "add":
			xmlDoc+="<adicionar>\n";				
			break;
		case "delete":
			xmlDoc+="<deletar>\n";				
			break;
	}
	while(email=this.elementos.pop()){
			xmlDoc +="<email>" + email + "</email>\n";
	}
	switch(this.tipo){
		case "add":
			xmlDoc+="</adicionar>\n";				
			break;
		case "delete":
			xmlDoc+="</deletar>\n";				
			break;
	}
	xmlDoc+="</request>";
	return xmlDoc;
}
	

function getDisponivel(){
	var select = document.getElementById("mail_result");
	var i=0;	
	request=new listReq();
	for(i=0;i < select.length;i++){
		if(select.options[i].selected==true){
			request.add(select.options[i].value);
		}
	}
loadXMLDoc("/proc.php",request.getXml());
}
function buildCadastrados() {
    var select = document.getElementById("cadastrados");
    var items = reqDisp.responseXML.getElementsByTagName("email");
    // loop through <item> elements, and add each nested
    // <title> element to Topics select element
    for (var i = 0; i < items.length; i++) {
        appendToSelect(select, i,
            document.createTextNode(getElementTextNS("", "title", items[i], 0)));
    }
}	
function searchDisp(){
	var lista=document.getElementById("search");
	loadXMLDoc("/retrieve.php?lista="+lista.value,procDispResult);
}

function procDispResult() {
	// only if reqGet shows "loaded"

   if (reqGet.readyState == 4) {
   // only if "OK"
   	if (reqGet.status == 200) {
  			clearDispList();
			buildDisponivel();
         } else {
            alert("There was a problem retrieving the XML data:\n" +
            reqGet.statusText);
         }
    }
}
function clearDispList() {
    var select = document.getElementById("disponivel");
    while (select.length > 0) {
        select.remove(0);
    }
}
function buildDisponivel() {
    var select = document.getElementById("disponivel");
    var items = reqGet.responseXML.getElementsByTagName("email");
    alert(reqGet.responseText);
    // loop through <item> elements, and add each nested
    // <title> element to Topics select element
    for (var i = 0; i < items.length; i++) {
        appendToSelect(select, i,items[i].textContent);
    }
}
// add item to select element the less
// elegant, but compatible way.
function appendToSelect(select, value, text) {
    var opt;
    opt = document.createElement("option");
    opt.value = value;
    opt.text=text;
    select.appendChild(opt);
}
