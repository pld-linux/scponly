Summary:	A restricted shell for assigning scp- or sftp-only access
Summary(pl):	Okrojona pow�oka daj�ca dost�p tylko do scp i/lub sftp
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
scponly" is an alternative 'shell' (of sorts) for system
administrators who would like to provide access to remote users to
both read and write local files without providing any remote execution
priviledges. Functionally, it is best described as a wrapper to the
"tried and true" ssh suite of applications.

A typical usage of scponly is in creating a semi-public account not
unlike the concept of anonymous login for ftp. This allows an
administrator to share files in the same way an anon ftp setup would,
only employing all the protection that ssh provides. This is
especially significant if you consider that ftp authentications
traverse public networks in a plaintext format.

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
%attr(644,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/%{name}/*
%dir %{_sysconfdir}/%{name}
%attr(755,root,root) %{_bindir}/%{name}
# There is also similar binary - use proper configure option (maybe separate subpackage?)
#%attr(4755,root,root) %{_sbindir}/scponlyc
%{_mandir}/man?/*
