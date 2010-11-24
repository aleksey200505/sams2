%define webuser apache
%define webgroup apache
%define squidgroup squid
%define apache_confdir /httpd/conf.d

%bcond_without web
%bcond_without doc
%bcond_without devel

Summary:	SAMS2 (Squid Account Management System)
Name:		sams
Version:	2.0.0
Release:	rc1%{dist}
Source0:	http://sams.perm.ru/download/%{name}-%{version}-rc1.tar.bz2
Patch0:		sams2.shebang.patch
License:	GPLv2+
Group:		Applications/Internet
URL:		http://sams.perm.ru/
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Requires:	mysql-server
Requires:	postgresql-server
Requires:	unixODBC
Requires:	pcre
Requires:	squid

BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
BuildRequires:	unixODBC-devel
BuildRequires:	gcc-c++
BuildRequires:	pcre-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	zlib-devel
BuildRequires:	chrpath
BuildRequires:	sed
BuildRequires:	httpd

%description
This program basically used for administrative purposes of squid proxy.
There are access control for users by NTLM, LDAP, NCSA, BASIC or IP
authorization mode.

%post
/sbin/ldconfig
/sbin/chkconfig --add sams2

%postun -p /sbin/ldconfig

%preun
if [ $1 = 0 ]; then
 /sbin/service sams2 stop > /dev/null 2>&1
 /sbin/chkconfig --del sams2
fi

#######################################################################
%if 0%{?with_devel}
%package devel
Summary:SAMS2 devel package
Group:Applications/System
%description devel
The sams2-devel package.
%endif

#######################################################################
%if 0%{?with_web}
%package web
Summary:SAMS2 web administration tool
Group:Applications/System
Requires:	httpd
Requires:	php
Requires:	php-mysql
Requires:	php-gd
Requires:	php-ldap
Requires:	php-pgsql
Requires:	php-odbc
Requires:	squid
Requires:	/usr/bin/wbinfo
%description web
The sams2-web package provides web administration tool
for remotely managing sams2 using your favorite
Web browser.
%endif

#######################################################################
%if 0%{?with_doc}
%package doc
Summary:SAMS2 Documentation
Group:Documentation
%description doc
The sams2-doc package includes the HTML versions of the "Using SAMS2".
%endif

#######################################################################

%prep
%setup -q -n %{name}-%{version}-rc1
%patch0 -p1

%build
make -f Makefile.cvs
%configure --disable-static

%install
%{__rm} -rf %{buildroot}
make DESTDIR=%{buildroot} install

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}%{apache_confdir}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/%{name}2

install -d %{buildroot}%{_docdir}/sams2-%{version}
install -m 644 ChangeLog AUTHORS COPYING NEWS INSTALL %{buildroot}%{_docdir}/sams2-%{version}
install -d -m 755 %{buildroot}%{_docdir}/sams2-%{version}/images

install -m 755 redhat/init.d %{buildroot}%{_initrddir}/samsd

%{__sed} -i -e 's,__PREFIX,%{_prefix}/bin,g' -e 's,__CONFDIR,%{_sysconfdir}/%{name}2,g' %{buildroot}%{_initrddir}/samsd
%{__sed} -i 's|/var/lock/subsys/sams2daemon|/var/lock/subsys/samsd|' %{buildroot}%{_initrddir}/samsd
%{__sed} -i 's|/var/run/sams2daemon.pid|/var/run/samsd.pid|' %{buildroot}%{_initrddir}/samsd

install -m 644 redhat/sysconfig %{buildroot}%{_sysconfdir}/sysconfig/sams
install -m 644 redhat/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/sams

%__mv -f %{buildroot}%{_libdir}/sams2/* %{buildroot}%{_libdir}/
%__mv -f %{buildroot}%{_sysconfdir}/sams2.conf %{buildroot}%{_sysconfdir}/%{name}2/

%__chmod 0644 %{buildroot}%{_docdir}/sams2-%{version}/images/freebsd-logo.png
%__chmod 0755 %{buildroot}/usr/share/sams2/data
%__chmod 0755 %{buildroot}/usr/share/sams2/lang/koi8r*

%{__sed} -i 's|^SQUIDCACHEDIR=.*|SQUIDCACHEDIR=/var/spool/squid|' %{buildroot}%{_sysconfdir}/%{name}2/sams2.conf
%{__sed} -i 's|^SAMSPATH=.*|SAMSPATH=/usr|' %{buildroot}%{_sysconfdir}/%{name}2/sams2.conf
%{__sed} -i 's|^WBINFOPATH=.*|WBINFOPATH=%{_prefix}/bin|' %{buildroot}%{_sysconfdir}/%{name}2/sams2.conf

# let's try to get rid of rpath
chrpath --delete %{buildroot}%{_bindir}/{sams2daemon,samsparser,samsredir}

%clean
%{__rm} -rf %{buildroot}

#######################################################################
## Files section
#######################################################################
%files
%defattr(-,root,root)
%{_prefix}/bin/samsparser
%{_prefix}/bin/sams2daemon
%{_prefix}/bin/samsredir
%{_prefix}/bin/sams_send_email
%{_initrddir}/samsd
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/sams
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/sams
%attr(644,%{webuser},%{squidgroup}) %config(noreplace) %{_sysconfdir}/%{name}2/sams2.conf
%exclude %{_libdir}/*

##########
%if 0%{?with_doc}
%files doc
%defattr(-,root,root)
%attr(644,root,root) %config(noreplace) %{_sysconfdir}%{apache_confdir}/doc4sams2.conf
%doc %{_docdir}/%{name}2-%{version}
%endif

##########
%if 0%{?with_web}
%files web
%defattr(-,%{webuser},%{webgroup})
%attr(644,root,root) %config(noreplace) %{_sysconfdir}%{apache_confdir}/sams2.conf
%{_datadir}/%{name}2
%endif

##########
%if 0%{?with_devel}
%files devel
%defattr(-,root,root)
%{_libdir}/*.so.*
%endif

%changelog
* Wed Nov 24 2010 Aleksey Popkov <aleksey@psniip.ru> - 2.0.0-rc1
- Moved sams2.conf to /_sysconfdir/sams/.

* Tue Nov 23 2010 Aleksey Popkov <aleksey@psniip.ru> - 2.0.0-rc1
- Fixed some errors.
- Adding self package of devel.
- Renamed sysconfig and logrotate config files.
- Moved lib files from /sams2/* to _libdir macros

* Mon Nov 22 2010 Aleksey Popkov <aleksey@psniip.ru> - 2.0.0-rc1
- The begin RPM-build speck file for Fedora and CentOs distributives.
