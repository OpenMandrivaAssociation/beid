%define real_name Belgian_Identity_Card_Run-time
%define release %mkrel 1
%define name	beid
%define version 2.5.9
%define	major	2
%define libname %mklibname %name %major
%define develname %mklibname %name -d
%define libname_opensc %mklibname beidlibopensc 2
%define libname_comm %mklibname beidcomm 0
%define libname_common %mklibname beidcommon 0
%define libname_gui %mklibname beidgui 1
%define libname_jni %mklibname beidlibjni 2
%define libname_pcsclite %mklibname beidpcsclite 2
%define libname_pkcs11 %mklibname beidpkcs11 2

Name: %{name}
Summary: Application to read information from the Belgian e-ID card
Version: %{version}
Release: %{release}
License: GPL
Group: Communications
URL: http://eid.belgium.be/
Source: http://www.belgium.be/zip/Belgian_Identity_Card_Run-time%{version}.tar.bz2
Source1: beid-scripts.tar.gz
Patch0: eid-belgium-2.5.9-openscreader.patch
Patch1: eid-belgium-2.5.9-reader-pcsc.patch
Patch2: beid-2.5.9-SConstruct.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

#Scons doesn't build when eid-belgium is already installed
BuildConflicts: beid
BuildRequires: scons, openssl-devel >= 0.9.7, pcsc-lite-devel >= 1.2.9
BuildRequires: qt3-devel >= 3.3.3
BuildRequires: wxGTK2.6-devel
BuildRequires: ImageMagick
BuildRequires: java-sdk
BuildRequires: openssl-devel
BuildRequires: desktop-file-utils
Requires: pcsc-lite

%description
This application allows the user to read out any information from a
Belgian electronic ID card, by using libbeid and libbeidlibopensc to
read the data from the card and parse it. Both identity information 
and information about the stored cryptographic keys can be read in a
user-friendly manner, and can easily be printed out or stored for 
later review.

The application verifies the signature of the identity information,
checks whether it was signed by a government-issued key, and 
optionally checks the certificate against the government's Certificate
Revocation List (CRL) and/or by using the Online Certificate Status
Protocol (OCSP) against the government's servers.

%package -n %{libname}
Group:          System/Libraries
Summary:        Main shared library for beid

%description -n %{libname}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{develname}
Summary: Development library for %{name}.
Group: Development/C
Requires: %{libname} = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}

%description -n %{develname}
This package contains the header files, development
documentation for %{name}. If you want to develop programs using 
%{name}, you will need to install %{libnamedev}.

%package -n %{libname_opensc}
Group:          System/Libraries
Summary:        OpenSC shared library for beid

%description -n %{libname_opensc}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libname_comm}
Group:          System/Libraries
Summary:        Comm shared library for beid

%description -n %{libname_comm}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libname_common}
Group:          System/Libraries
Summary:        Comm shared library for beid

%description -n %{libname_common}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libname_gui}
Group:          System/Libraries
Summary:        GUI shared library for beid

%description -n %{libname_gui}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libname_jni}
Group:          System/Libraries
Summary:        JNI shared library for beid

%description -n %{libname_jni}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libname_pcsclite}
Group:          System/Libraries
Summary:        pcsclite shared library for beid

%description -n %{libname_pcsclite}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

%package -n %{libname_pkcs11}
Group:          System/Libraries
Summary:        pcsclite shared library for beid

%description -n %{libname_pkcs11}
This package provides shared libraries to use with the Belgian
Identity Card runtime and tools.

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
%{__perl} -pi.orig -e 's|/usr/local/lib/libbeidpkcs11.so\b|%{_libdir}/libbeidpkcs11.so.2|g' \
	src/newpkcs11/etc/Belgian_eID_PKCS11_java.cfg \
	src/newpkcs11/etc/beid-pkcs11-register.html
%{__perl} -pi.orig -e 's|/usr/local/bin/beidgui.png\b|beidgui|g' \
	src/eidviewer/beidgui.desktop
%{__perl} -pi.orig -e 's|/usr/local/bin\b|%{_bindir}|g' \
	src/beidservicecrl/belgium.be-beidcrld \
	"src/Belpic PCSC Service/belgium.be-beidpcscd" \
	src/eidviewer/beidgui.desktop
%{__perl} -pi.orig -e 's|/usr/local/share\b|%{_datadir}|g' \
	src/eidviewer/beidgui.conf
%{__perl} -pi.orig -e 's|MultipleArgs=false||g' \
	src/eidviewer/beidgui.desktop

%build
export CFLAGS="%{optflags}"
export CXXFLAGS="%{optflags}"
export JAVA_HOME="$(readlink /etc/alternatives/java_sdk)"
#source "/etc/profile.d/qt.sh"
scons configure prefix="%{_prefix}"
scons prefix="%{_prefix}"

%install
rm -rf %{buildroot}
scons install --cache-disable prefix="%{buildroot}%{_prefix}" libdir="%{buildroot}%{_libdir}"

install -Dp -m0755 beidcrld.init %{buildroot}%{_initrddir}/beidcrld
install -Dp -m0755 beidpcscd.init %{buildroot}%{_initrddir}/beidpcscd
install -Dp -m0644 beidcrld.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/beidcrld
install -Dp -m0644 beidpcscd.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/beidpcscd

install -d -m0755 %{buildroot}%{_iconsdir}/hicolor/{48x48,32x32,16x16}/apps
install -d -m0755 %{buildroot}%{_datadir}/applications/
mv -vf %{buildroot}%{_bindir}/beidgui.png %{buildroot}%{_iconsdir}/hicolor/48x48/apps/beidgui.png
convert -scale 32 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/beidgui.png %{buildroot}%{_iconsdir}/hicolor/32x32/apps/beidgui.png
convert -scale 16 %{buildroot}%{_iconsdir}/hicolor/48x48/apps/beidgui.png %{buildroot}%{_iconsdir}/hicolor/16x16/apps/beidgui.png
mv -vf %{buildroot}%{_bindir}/beidgui.desktop %{buildroot}%{_datadir}/applications/beidgui.desktop

# fix menu entry

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="Qt" \
  --add-category="Utility" \
  --add-category="Security" \
  --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

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
/sbin/service pcscd condrestart > /dev/null 2>/dev/null || :
%_post_service beidcrld
%_post_service beidpcscd
%update_menus
%update_icon_cache hicolor

%post -n %{libname}
/sbin/ldconfig

%preun
%_preun_service beidcrld
%_preun_service beidpcscd

%postun
/sbin/service pcscd condrestart > /dev/null 2>/dev/null || :
%clean_menus
%clean_icon_cache hicolor

%postun -n %{libname}
/sbin/ldconfig

%clean
%{__rm} -rf %{buildroot}

%files -f beidgui.lang
%defattr(-, root, root, 0755)
%doc CHANGES INSTALL README VERSION doc/*.rtf doc/*.doc
%{_mandir}/man1/beid-pkcs11-tool.1*
%{_mandir}/man1/beid-tool.1*
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
%{_libdir}/pkcs11
%{_datadir}/applications/beidgui.desktop
%{_datadir}/beid/
%exclude %{_datadir}/beid/eID-toolkit_licensingtermsconditions*.rtf
%exclude %{_datadir}/beid/DeveloperGuide.doc
%{_iconsdir}/hicolor/48x48/apps/beidgui.png
%{_iconsdir}/hicolor/32x32/apps/beidgui.png
%{_iconsdir}/hicolor/16x16/apps/beidgui.png

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*beid.so.*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/*.so
%{_includedir}/%{name}

%files -n %{libname_opensc}
%defattr(-,root,root)
%{_libdir}/*beidlibopensc.so.*

%files -n %{libname_comm}
%defattr(-,root,root)
%{_libdir}/*beidcomm.so.*

%files -n %{libname_common}
%defattr(-,root,root)
%{_libdir}/*beidcommon.so.*

%files -n %{libname_gui}
%defattr(-,root,root)
%{_libdir}/*beidgui.so.*

%files -n %{libname_jni}
%defattr(-,root,root)
%{_libdir}/*beidlibjni.so.*

%files -n %{libname_pcsclite}
%defattr(-,root,root)
%{_libdir}/*beidpcsclite.so.*

%files -n %{libname_pkcs11}
%defattr(-,root,root)
%{_libdir}/*beidpkcs11.so.*
