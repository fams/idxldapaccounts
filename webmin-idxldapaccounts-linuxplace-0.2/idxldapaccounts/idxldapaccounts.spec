# $Id$
%define name idxldapaccounts-samba-v3
%define version 0.2
%define release 5

Summary: A webmin module for LDAP accounts administration.
Name: %{name}
Vendor: IDEALX S.A.S.
URL: http://IDEALX.org/
Packager: Gerald Macinenti <gerald.macinenti@IDEALX.com>
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}-%{release}.tar
Copyright: GPL
Group: System/Tools
BuildRoot: %{_tmppath}/%{name}-buildroot
Prefix: %{_prefix}
PreReq: tar
PreReq: webmin
PreReq: perl-perl-ldap
BuildArch: noarch

%description 

idxldapaccounts is a Webmin module for managing LDAP users and groups accounts. 

%prep 

%setup

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/libexec/webmin/idxldapaccounts
cp -a * $RPM_BUILD_ROOT/usr/libexec/webmin/idxldapaccounts

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/libexec/webmin/idxldapaccounts/

%post
if [ "$1" = "1" ] ; then  # first install
	cd /usr/libexec/webmin
	tar  -cf /tmp/idxldapaccounts.wbm idxldapaccounts
	./install-module.pl /tmp/idxldapaccounts.wbm
	rm /tmp/idxldapaccounts.wbm
fi

# end of file
