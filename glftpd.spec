#TODO
# - add %config(noreplace) to some files

Summary:	glFtpD is a free FTP Daemon
Summary(pl):	glFtpD jest darmowym serwerem FTP
Name:		glftpd
Version:	1.32
Release:	0.9
License:	Freeware
Group:		Daemons
Source0:	http://glftpd.coding-slaves.com/files/distributions/LNX/%{name}-LNX_%{version}.tgz
# Source0-md5:	45913cf02c0c754f054eba9cfa213987
Source1:	%{name}.conf
Source2:	%{name}.inetd
Source3:	%{name}.cron
URL:		http://www.glftpd.com/
PreReq:		rc-inetd
Requires(post):	openssl-tools
BuildRequires:	awk
BuildRequires:	gzip
BuildRequires:	zip
BuildRequires:	sed
BuildRequires:	bash
BuildRequires:	findutils
BuildRequires:	unzip
BuildRequires:	grep
BuildRequires:	coreutils
BuildRequires:	pdksh
Provides:	ftpserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
glFtpD is a free FTP Daemon for Linux, FreeBSD, Sun Solaris, and many
other platforms. It has numerous features, and is easy to setup and
use.

%description -l pl
glFtpD jest darmowym serwerem FTP dla Linuxa, FreeBSD, Sun Solaris, i
wielu innych platform. Ma wiele opcji, i jest latwy do skonfigurowania
i u¿ywania.

%define         _glroot         /home/services/glftpd
%define		_noautoprovfiles	%{_glroot}/bin/{sh,cat,grep,unzip,wc,find,ls,bash,mkdir,rmdir,rm,mv,cp,awk,ln,basename,dirname,head,tail,cut,tr,wc,sed,date,sleep,touch,gzip,zip}
%define		_noautoprovfiles	%{_glroot}/lib/*

%prep
%setup -q -n %{name}-LNX_%{version}

%build
for cfile in `ls bin/sources/*.c`; do
    base=`basename "${cfile%.c}"`
    [ -f "bin/$base" ] && rm -f "bin/$base"
    %{__cc} %{rpmcflags} %{rpmldflags} -o bin/$base $cfile
done


%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_glroot}/{bin,dev} $RPM_BUILD_ROOT/etc/{sysconfig/rc-inetd,cron.hourly}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}
rm -Rf bin/sources
install bin/* $RPM_BUILD_ROOT%{_glroot}/bin
cp -Rf sitebot site ftp-data etc lib $RPM_BUILD_ROOT%{_glroot}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}.conf
install %{SOURCE3} $RPM_BUILD_ROOT/etc/cron.hourly/%{name}
for i in sh cat grep unzip wc find ls bash mkdir rmdir rm mv cp awk ln basename dirname head tail cut tr wc sed date sleep touch gzip zip; do
	install `which $i` $RPM_BUILD_ROOT%{_glroot}/bin
done
install /sbin/ldconfig $RPM_BUILD_ROOT%{_glroot}/bin

ldd $RPM_BUILD_ROOT%{_glroot}/bin/* | grep "=>" | sed 's:^.* => \(/[^ ]*\).*$:\1:' |
sort | uniq | while read lib; do
    if [ -f "$lib" ]; then
        cp -f "$lib" $RPM_BUILD_ROOT%{_glroot}/lib
    fi
done
echo "/lib" > $RPM_BUILD_ROOT%{_glroot}%{_sysconfdir}/ld.so.conf
cp %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/rc-inetd/ftpd
install create_server_key.sh $RPM_BUILD_ROOT%{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
chroot $RPM_BUILD_ROOT%{_glroot} /bin/ldconfig
if [ ! -f $RPM_BUILD_ROOT%{_glroot}/dev/null ]; then
mknod -m666 $RPM_BUILD_ROOT%{_glroot}/dev/null c 1 3
fi
if [ ! -f $RPM_BUILD_ROOT%{_glroot}/dev/zero ]; then
mknod -m666 $RPM_BUILD_ROOT%{_glroot}/dev/zero c 1 5
fi
if [ ! -f /var/lib/openssl/certs/ftpd-dsa.pem ]; then
	cd /var/lib/openssl/certs/
	%{_datadir}/%{name}/create_server_key.sh `hostname -f`
	cd /
fi
if [ -f /etc/services ] && ! grep -q "glftpd" /etc/services; then
	echo "glftpd	2121/tcp" >> /etc/services
fi
if [ -f /var/lock/subsys/rc-inetd ]; then
	/etc/rc.d/init.d/rc-inetd reload 1>&2
else
	echo "Type \"/etc/rc.d/init.d/rc-inetd start\" to start inet server" 1>&2
fi
echo "If you want change default listen port from 2121 
	do it in /etc/services in line glftpd line"

%postun
if [ "$1" = "0" -a -f /var/lock/subsys/rc-inetd ]; then
	/etc/rc.d/init.d/rc-inetd reload 1>&2
fi


%files
%defattr(644,root,root,755)
%doc changelog README UPGRADING docs/*
%dir %{_datadir}/%{name}
%attr(755,root,root) %{_datadir}/%{name}/create_server_key.sh
%config(noreplace) %verify(not size mtime md5) %attr(640,root,root) %{_sysconfdir}/%{name}.conf
/etc/cron.hourly/%{name}
/etc/sysconfig/rc-inetd/ftpd
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
%{_glroot}%{_sysconfdir}/*
%{_glroot}/ftp-data/*/*
%{_glroot}/sitebot/*
