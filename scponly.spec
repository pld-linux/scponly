Summary:	A restricted shell for assigning scp- or sftp-only access
Summary(pl):	Okrojona pow³oka daj±ca dostêp tylko do scp i/lub sftp
Name:		scponly
Version:	4.0
Release:	1
License:	BSD-like
Group:		Applications/Shells
Source0:	http://www.sublimation.org/scponly/%{name}-%{version}.tgz
# Source0-md5:	1706732945996865ed0cccd440b64fc1
Patch0:		%{name}-sftp_path.patch
Patch1:		%{name}-DESTDIR.patch
URL:		http://www.sublimation.org/scponly/
BuildRequires:	autoconf
BuildRequires:	automake
#BuildRequires:	openssh-clients >= 3.5p1
#Conflicts:	openssh-server < 3.5p1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_bindir		/bin

%description
scponly is an alternative 'shell' (of sorts) for system administrators
who would like to provide access to remote users to both read and
write local files without providing any remote execution priviledges.
Functionally, it is best described as a wrapper to the "tried and
true" SSH suite of applications.

A typical usage of scponly is in creating a semi-public account not
unlike the concept of anonymous login for FTP. This allows an
administrator to share files in the same way an anon ftp setup would,
only employing all the protection that SSH provides. This is
especially significant if you consider that FTP authentications
traverse public networks in a plaintext format.

%description -l pl
scponly to alternatywna "pow³oka" dla administratorów systemu, którzy
chcieliby udostêpniæ zdalnym u¿ytkownikom mo¿liwo¶æ odczytu i zapisu
plików lokalnych bez prawa wykonywania poleceñ. Funkcjonalno¶æ mo¿na
najlepiej okre¶liæ jako wrapper dla sprawdzonego zbioru aplikacji SSH.

Typowy sposób u¿ycia scponly to stworzenie prawie publicznego konta
podobnie do idei anonimowego dostêpu do FTP. Pozwala to
administratorowi na wspó³dzielenie plików w ten sam sposób co
anonimowe FTP, ale z u¿yciem ochrony zapewnianej przez SSH. Ma to
szczególne znaczenie w przypadku uwierzytelniania FTP poprzez sieæ
publiczn±.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	 DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post
umask 022
if [ ! -f /etc/shells ]; then
	echo "%{_bindir}/%{name}" > /etc/shells
else
	if ! grep -q '^%{_bindir}/%{name}$' /etc/shells; then
		echo "%{_bindir}/%{name}" >> /etc/shells
	fi
fi

%preun
umask 022
if [ "$1" = "0" ]; then
	grep -v %{_bindir}/%{name} /etc/shells > /etc/shells.new
	mv -f /etc/shells.new /etc/shells
fi

%files
%defattr(644,root,root,755)
%doc AUTHOR CHANGELOG CONTRIB INSTALL README TODO setup_chroot.sh
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/*
%attr(755,root,root) %{_bindir}/%{name}
# There is also similar binary - use proper configure option (maybe separate subpackage?)
#%attr(4755,root,root) %{_sbindir}/scponlyc
%{_mandir}/man?/*
