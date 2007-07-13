%define real_name Belgian_Identity_Card_Run-time
%define release %mkrel 1
%define name	beid
%define version 2.5.9
%define	major	2
%define libname %mklibname %name %major
%define libnamedev %mklibname %name %major -d

Name: %{name}
Summary: Application to read out information from the Belgian electronic ID card
Version: %{version}
Release: %{release}
License: GPL
Group: Communications
URL: http://eid.belgium.be/
Packager: Cedric Devillers <brancaleone@altern.org>
Source: http://www.belgium.be/zip/Belgian_Identity_Card_Run-time%{version}.tar.bz2
Source1: beid-scripts.tar.gz
Patch0: eid-belgium-2.5.9-openscreader.patch
Patch1: eid-belgium-2.5.9-reader-pcsc.patch
Patch2: beid-2.5.9-SConstruct.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

#Scons doesn't build when eid-belgium is already installed
BuildConflicts: beid
BuildRequires: scons, openssl-devel >= 0.9.7, pcsc-lite-devel >= 1.2.9
BuildRequires: libqt3-devel >= 3.3.3
BuildRequires: libwxgtk2.6-devel
Requires: pcsc-lite

%description
This application allows the user to read out any information from a
Belgian electronic ID card, by using libbeid and libbeidlibopensc to
read the data from the card and parse it. Both identity information and
information about the stored cryptographic keys can be read in a
user-friendly manner, and can easily be printed out or stored for later
reviewal.

The application verifies the signature of the identity information,
checks whether it was signed by a government-issued key, and optionally
checks the certificate against the government's Certificate Revocation List
(CRL) and/or by using the Online Certificate Status Protocol (OCSP) against
the government's servers.

%package -n %{libname}
Group:          System/Libraries
Summary:        Shared library part of beid

%description -n %{libname}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libnamedev}
Summary: Header files, libraries and development documentation for %{name}.
Group: Development/C
Requires: %{libname} = %{version}

%description -n %{libnamedev}
This package contains the header files, development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{libnamedev}.

%prep
%setup -q
%setup -q -a 1

%patch0 -p0
%patch1 -p0
%patch2 -p0

### Fixing the references to /usr/local in some files
%{__perl} -pi.orig -e 's|/usr/local/etc\b|%{buildroot}%{_sysconfdir}|g' \
	SConstruct
%{__perl} -pi.orig -e 's|/usr/local/lib\b|%{buildroot}%{_libdir}|g' \
	src/newpkcs11/SConscript
%{__perl} -pi.orig -e 's|/etc/init.d\b|%{buildroot}%{_initrddir}|g' \
	src/beidservicecrl/SConscript \
	"src/Belpic PCSC Service/SConscript"

%{__perl} -pi.orig -e 's|/usr/local/etc\b|%{_sysconfdir}|g' \
	src/beidcommon/config.cpp \
	src/newpkcs11/config.h
%{__perl} -pi.orig -e 's|/usr/local/lib\b|%{_libdir}|g' \
	src/newpkcs11/etc/Belgian_eID_PKCS11_java.cfg \
	src/newpkcs11/etc/beid-pkcs11-register.html
%{__perl} -pi.orig -e 's|/usr/local/bin/beidgui.png\b|%{_datadir}/icons/beidgui.png|g' \
	src/eidviewer/beidgui.desktop
%{__perl} -pi.orig -e 's|/usr/local/bin\b|%{_bindir}|g' \
	src/beidservicecrl/belgium.be-beidcrld \
	"src/Belpic PCSC Service/belgium.be-beidpcscd" \
	src/eidviewer/beidgui.desktop
%{__perl} -pi.orig -e 's|/usr/local/share\b|%{_datadir}|g' \
	src/eidviewer/beidgui.conf
sed -i -e /MultipleArgs=false/d \
	src/eidviewer/beidgui.desktop

%build
#export CFLAGS="%{optflags}"
#export JAVA_HOME="$(readlink /etc/alternatives/java_sdk)"
#source "/etc/profile.d/qt.sh"
scons configure prefix="%{_prefix}"
scons prefix="%{_prefix}"

%install
rm -rf %{buildroot}
#install -d -m0755 %{buildroot}%{_bindir}
#%{__install} -d -m0755 %{buildroot}%{_libdir}
#source "/etc/profile.d/qt.sh"
scons install --cache-disable prefix="%{buildroot}%{_prefix}" libdir="%{buildroot}%{_libdir}"

install -Dp -m0755 beidcrld.init %{buildroot}%{_initrddir}/beidcrld
install -Dp -m0755 beidpcscd.init %{buildroot}%{_initrddir}/beidpcscd
install -Dp -m0644 beidcrld.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/beidcrld
install -Dp -m0644 beidpcscd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/beidpcscd

#install -d -m0755 %{buildroot}%{_datadir}/applications/
desktop-file-install \
	--vendor "" \
	--add-category="X-MandrivaLinux-Internet-Other" \
	--dir %{buildroot}%{_datadir}/applications \
	%{buildroot}%{_bindir}/beidgui.desktop

install -d -m0755 %{buildroot}%{_datadir}/icons/
mv -vf %{buildroot}%{_bindir}/beidgui.png %{buildroot}%{_datadir}/icons/beidgui.png
mv -vf %{buildroot}%{_bindir}/beidgui.desktop %{buildroot}%{_datadir}/applications/beidgui.desktop

### Fix library symlinks
#for lib in $(ls %{buildroot}%{_libdir}/libbeid*.so.?.?.?); do
#	%{__ln_s} -f $(basename $lib) ${lib//%\.?\.?}
#done

### Fix locale files
for file in $(ls %{buildroot}%{_datadir}/locale/beidgui_*.mo); do
	lang="${file%.mo}"
	lang="${lang#%{buildroot}%{_datadir}/locale/beidgui_}"
	%{__mkdir} -p %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/
	%{__mv} -f $file %{buildroot}%{_datadir}/locale/$lang/LC_MESSAGES/beidgui.mo
done
%find_lang beidgui

%post
/sbin/service pcscd restart
/sbin/chkconfig --add beidcrld
/sbin/chkconfig --add beidpcscd
/sbin/service beidcrld start
/sbin/service beidpcscd start
%{update_menus}

%post -n %{libname}
/sbin/ldconfig

%preun
/sbin/service beidcrld stop
/sbin/service beidpcscd stop
/sbin/chkconfig --del beidcrld
/sbin/chkconfig --del beidpcscd
/sbin/service pcscd restart

%postun
%{clean_menus}

%postun -n %{libname}
/sbin/ldconfig

%clean
%{__rm} -rf %{buildroot}

%files -f beidgui.lang
%defattr(-, root, root, 0755)
%doc CHANGES INSTALL README VERSION doc/*.rtf doc/*.doc
%doc %{_mandir}/man1/beid-pkcs11-tool.1*
%doc %{_mandir}/man1/beid-tool.1*
%config(noreplace) %{_sysconfdir}/beidbase.conf
%config(noreplace) %{_sysconfdir}/beidgui.conf
%config(noreplace) %{_sysconfdir}/sysconfig/beidcrld
%config(noreplace) %{_sysconfdir}/sysconfig/beidpcscd
%{_initrddir}/beidcrld
%{_initrddir}/beidpcscd
%exclude %{_initrddir}/belgium.be-beidcrld
%exclude %{_initrddir}/belgium.be-beidpcscd
%{_bindir}/beid-pkcs11-tool
%{_bindir}/beid-tool
%{_bindir}/beidcrld
%{_bindir}/beidpcscd
%{_bindir}/beidgui
%{_datadir}/applications/beidgui.desktop
%{_datadir}/beid/
%exclude %{_datadir}/beid/eID-toolkit_licensingtermsconditions*.rtf
%exclude %{_datadir}/beid/DeveloperGuide.doc
%{_datadir}/icons/beidgui.png

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libbeid*.so*
%{_libdir}/pkcs11/

%files -n %{libnamedev}
%defattr(-,root,root)
%{_includedir}/beid
