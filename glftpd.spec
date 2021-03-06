# NOTE
# - the "source" contains partial source code, daemon is still 32bit ELF
#   altho there's 64bit binary available from homepage
Summary:	glFtpD is a free FTP Daemon
Summary(pl.UTF-8):	glFtpD jest darmowym serwerem FTP
Name:		glftpd
Version:	2.01
Release:	0.2
License:	Freeware
Group:		Daemons
Source0:	http://www.glftpd.dk/files/%{name}-LNX_%{version}.tgz
# Source0-md5:	f15628798b1f6cfe71a781f035cfaa28
Source1:	%{name}.conf
Source2:	%{name}.inetd
Source3:	%{name}.cron
URL:		http://www.glftpd.dk/
BuildRequires:	bash
BuildRequires:	coreutils
BuildRequires:	rpmbuild(macros) >= 1.583
BuildRequires:	unzip
BuildRequires:	zip
Requires(post):	openssl-tools
Requires:	rc-inetd
Provides:	ftpserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_glroot			/home/services/glftpd
%define		_noautoprovfiles	%{_glroot}/lib/*

# copied libraries have symbols missing: errno, h_errno, __resp
%define		skip_post_check_so	libpthread.so.0 librt.so.1 libm.so.6 libcrypt.so.1

%description
glFtpD is a free FTP Daemon for Linux, FreeBSD, Sun Solaris, and many
other platforms. It has numerous features, and is easy to setup and
use.

%description -l pl.UTF-8
glFtpD jest darmowym serwerem FTP dla Linuksa, FreeBSD, Sun Solaris, i
wielu innych platform. Ma wiele opcji, i jest łatwy do skonfigurowania
i używania.

%prep
%setup -q -n %{name}-LNX_%{version}

mv bin/sources .

%build
for cfile in $(ls sources/*.c); do
	ldflags=
	base=$(basename "${cfile%.c}")
	[ -f "bin/$base" ] && rm -f "bin/$base"
	%{__cc} %{rpmcflags} %{rpmldflags} -o bin/$base $cfile
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_glroot}/{bin,dev} $RPM_BUILD_ROOT/etc/{sysconfig/rc-inetd,cron.daily}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
install -p bin/* $RPM_BUILD_ROOT%{_glroot}/bin
cp -Rf sitebot site ftp-data etc lib $RPM_BUILD_ROOT%{_glroot}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/rc-inetd/%{name}
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/cron.daily/%{name}
install -p create_server_key.sh $RPM_BUILD_ROOT%{_datadir}/%{name}
for i in sh cat grep unzip wc find ls bash mkdir rmdir rm mv cp awk ln basename dirname head tail cut tr wc sed date sleep touch gzip zip; do
	install -p `which $i` $RPM_BUILD_ROOT%{_glroot}/bin
done
install -p /sbin/ldconfig $RPM_BUILD_ROOT%{_glroot}/bin

ldd $RPM_BUILD_ROOT%{_glroot}/bin/* | grep "=>" | sed 's:^.* => \(/[^ ]*\).*$:\1:' |
sort | uniq | while read lib; do
	if [ -f "$lib" ]; then
		cp -f "$lib" $RPM_BUILD_ROOT%{_glroot}/lib
	fi
done
echo "/lib" > $RPM_BUILD_ROOT%{_glroot}%{_sysconfdir}/ld.so.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
chroot %{_glroot} /bin/ldconfig
if [ ! -f %{_glroot}/dev/null ]; then
	mknod -m666 %{_glroot}/dev/null c 1 3
fi
if [ ! -f %{_glroot}/dev/zero ]; then
	mknod -m666 %{_glroot}/dev/zero c 1 5
fi
if [ ! -f /var/lib/openssl/certs/ftpd-dsa.pem ]; then
	cd /var/lib/openssl/certs/
	%{_datadir}/%{name}/create_server_key.sh `hostname -f`
	cd /
fi
if [ -f /etc/services ] && ! grep -q "glftpd" /etc/services; then
	echo "glftpd	2121/tcp" >> /etc/services
fi
echo "If you want change default listen port from 2121
  do it in /etc/services in line glftpd line and /etc/sysconfig/rc-inetd/glftpd"

%service -q rc-inetd reload

%postun
if [ "$1" = "0" ]; then
	%service -q rc-inetd reload
fi

%files
%defattr(644,root,root,755)
%doc changelog README UPGRADING docs/*
%dir %{_datadir}/%{name}
%attr(755,root,root) %{_datadir}/%{name}/create_server_key.sh
%config(noreplace) %verify(not md5 mtime size) %attr(640,root,root) %{_sysconfdir}/%{name}.conf
%attr(750,root,root) /etc/cron.daily/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/rc-inetd/glftpd
%dir %{_glroot}
%dir %{_glroot}/bin
%dir %{_glroot}%{_sysconfdir}
%dir %{_glroot}/dev
%dir %{_glroot}/ftp-data
%dir %{_glroot}/ftp-data/*
%dir %{_glroot}/lib
%dir %{_glroot}/site
%attr(777,root,root) %dir %{_glroot}/site/incoming
%dir %{_glroot}/sitebot
%attr(755,root,root) %{_glroot}/bin/*
%attr(755,root,root) %{_glroot}/lib/*
%config(noreplace) %verify(not md5 mtime size) %{_glroot}%{_sysconfdir}/*
%config(noreplace) %verify(not md5 mtime size) %{_glroot}/ftp-data/*/*
%config(noreplace) %verify(not md5 mtime size) %{_glroot}/sitebot/*
