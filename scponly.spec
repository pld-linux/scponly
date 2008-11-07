# TODO
#  - make sure we don't provide the libraries
#  - more comments needed on chroot package (write me ;)
#  - store versioned libraries, and ldconfig the symlinks?
#  - hard depend all libraries copied to runtime dep? (so they're urged
#  to get updated scponly-chroot package when the library gets newer
#  package)
#  - separation for -chroot: rsync subpackage?
#  - maybe there already exists generic chroot env provider package?
#
# Conditional build:
%bcond_with	chroot	# build experimental chroot package
#
Summary:	A restricted shell for assigning scp- or sftp-only access
Summary(pl.UTF-8):	Okrojona powłoka dająca dostęp tylko do scp i/lub sftp
Name:		scponly
Version:	4.8
Release:	0.1
License:	BSD-like
Group:		Applications/Shells
Source0:	http://dl.sourceforge.net/sourceforge/scponly/%{name}-%{version}.tgz
# Source0-md5:	139ac9abd7f3b8dbc5c5520745318f8a
Patch0:		%{name}-sftp_path.patch
Patch1:		%{name}-DESTDIR.patch
Patch2:		%{name}-man.patch
Patch3:		%{name}-setup_chroot.patch
URL:		http://sublimation.org/scponly/
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with chroot}
# These are for building chroot jail package
BuildRequires:	coreutils
BuildRequires:	fakeroot
BuildRequires:	openssh-clients
BuildRequires:	openssh-server
%endif
BuildRequires:	rsync
Requires(post,preun):	grep
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if %{with chroot}
# better destination?
%define		_datadir	/usr/lib/%{name}
%define		_noautoprovfiles	%{_datadir}
%define		_noautoreqfiles		%{_datadir}
%endif

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

%description -l pl.UTF-8
scponly to alternatywna "powłoka" dla administratorów systemu, którzy
chcieliby udostępnić zdalnym użytkownikom możliwość odczytu i zapisu
plików lokalnych bez prawa wykonywania poleceń. Funkcjonalność można
najlepiej określić jako wrapper dla sprawdzonego zbioru aplikacji SSH.

Typowy sposób użycia scponly to stworzenie prawie publicznego konta
podobnie do idei anonimowego dostępu do FTP. Pozwala to
administratorowi na współdzielenie plików w ten sam sposób co
anonimowe FTP, ale z użyciem ochrony zapewnianej przez SSH. Ma to
szczególne znaczenie w przypadku uwierzytelniania FTP poprzez sieć
publiczną.

%package chroot
Summary:	Chroot capable scponly
Summary(pl.UTF-8):	scponly wykonujące chroot
Group:		Applications/Shells
License:	BSD-like
# + No idea due packaging system libraries
Requires(post,preun):	grep

%description chroot
This package contains suid binary for scponly. As the scponly is
called after authorized user is logged in, it is needed to have suid
bit to do chroot() system call. You should read INSTALL from the main
package to understand what implications this suid binary installations
could bring.

%description chroot -l pl.UTF-8
Ten pakiet zawiera program scponly z ustawionym bitem suid. Jako że
scponly jest wywoływane po zalogowaniu autoryzowanego użytkownika,
musi mieć ten bit ustawiony w celu wykonania wywołania chroot(). O
konsekwencjach tego można przeczytać w pliku INSTALL z głównego
pakietu.

%prep
%setup -q
%patch0 -p0
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__aclocal}
%{__autoconf}
%configure \
	--bindir=%{_sbindir} \
	--enable-rsync-compat \
	--with-sftp-server=%{_prefix}/%{_lib}/openssh/sftp-server \
	%{?with_chroot:--enable-chrooted-binary} \

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	 DESTDIR=$RPM_BUILD_ROOT

# compat, we can't afford trigger changes in /etc/passwd
install -d $RPM_BUILD_ROOT/bin
ln -s ..%{_sbindir}/scponly $RPM_BUILD_ROOT/bin/scponly

%if %{with chroot}
# TODO: implement the setup_chroot.sh here, to be sure how it works.
DESTDIR=$RPM_BUILD_ROOT ROOTDIR=%{_datadir} fakeroot sh ./setup_chroot.sh

echo 'root:x:0:0:root:/root:/bin/sh' > $RPM_BUILD_ROOT%{_datadir}/etc/passwd
echo '' > $RPM_BUILD_ROOT%{_datadir}/etc/ld.so.conf
install groups $RPM_BUILD_ROOT%{_datadir}/usr/bin
rm -rf $RPM_BUILD_ROOT%{_datadir}/usr/%{_lib}/libfakeroot
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
umask 022
if [ ! -f /etc/shells ]; then
	echo '%{_sbindir}/%{name}' > /etc/shells
else
	if ! grep -q '^%{_sbindir}/%{name}$' /etc/shells; then
		echo '%{_sbindir}/%{name}' >> /etc/shells
	fi
fi

%preun
umask 022
if [ "$1" = "0" ]; then
	grep -v '^%{_sbindir}/%{name}$' /etc/shells > /etc/shells.new
	mv -f /etc/shells.new /etc/shells
fi

%if %{with chroot}
%post chroot
umask 022
if [ ! -f /etc/shells ]; then
	echo '%{_sbindir}/%{name}c' > /etc/shells
else
	if ! grep -q '^%{_sbindir}/%{name}c$' /etc/shells; then
		echo '%{_sbindir}/%{name}c' >> /etc/shells
	fi
fi

# build ld.so.ccache
ldconfig -X -r %{_datadir}

%preun chroot
umask 022
if [ "$1" = "0" ]; then
	grep -v '^%{_sbindir}/%{name}c$' /etc/shells > /etc/shells.new
	mv -f /etc/shells.new /etc/shells
fi
%endif

%triggerpostun -- scponly < 4.0-1.5
umask 022
grep -v '^/bin/scponly$' /etc/shells > /etc/shells.new
mv -f /etc/shells.new /etc/shells

%files
%defattr(644,root,root,755)
%doc AUTHOR CHANGELOG CONTRIB INSTALL README TODO
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/*
%attr(755,root,root) %{_sbindir}/%{name}
%{_mandir}/man?/*
# old compat symlink
%attr(755,root,root) /bin/scponly

%if %{with chroot}
%files chroot
%defattr(644,root,root,755)
%doc setup_chroot.sh
%attr(4755,root,root) %{_sbindir}/scponlyc

%dir %{_datadir}/etc
%ghost %{_datadir}/etc/ld.so.cache
%config(noreplace) %verify(not md5 mtime size) %{_datadir}/etc/ld.so.conf
%config(noreplace) %verify(not md5 mtime size) %{_datadir}/etc/passwd

%dir %{_datadir}
%dir %{_datadir}/bin
%attr(755,root,root) %{_datadir}/bin/chgrp
%attr(755,root,root) %{_datadir}/bin/chmod
%attr(755,root,root) %{_datadir}/bin/chown
%attr(755,root,root) %{_datadir}/bin/echo
%attr(755,root,root) %{_datadir}/bin/id
%attr(755,root,root) %{_datadir}/bin/ln
%attr(755,root,root) %{_datadir}/bin/ls
%attr(755,root,root) %{_datadir}/bin/mkdir
%attr(755,root,root) %{_datadir}/bin/mv
%attr(755,root,root) %{_datadir}/bin/pwd
%attr(755,root,root) %{_datadir}/bin/rm
%attr(755,root,root) %{_datadir}/bin/rmdir

%dir %{_datadir}/%{_lib}
%attr(755,root,root) %{_datadir}/%{_lib}/ld-linux.so.*
%attr(755,root,root) %{_datadir}/%{_lib}/lib*.so.*

%dir %{_datadir}/usr
%dir %{_datadir}/usr/bin
%attr(755,root,root) %{_datadir}/usr/bin/groups
%attr(755,root,root) %{_datadir}/usr/bin/scp
%attr(755,root,root) %{_datadir}/usr/bin/rsync

%dir %{_datadir}/usr/%{_lib}
%attr(755,root,root) %{_datadir}/usr/%{_lib}/lib*.so.*
%attr(755,root,root) %{_datadir}/usr/%{_lib}/lib*.so
%dir %{_datadir}/usr/%{_lib}/openssh
%attr(755,root,root) %{_datadir}/usr/%{_lib}/openssh/sftp-server
%endif
