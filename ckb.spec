%define snapshot %{nil}

Summary:	Driver for Corsair gaming keyboards and mice
Name:		ckb
Version:	0.6.0
Release:	2
Group:		Graphical desktop/KDE
License:	GPLv2 LGPLv2 GFDL
Url:		https://github.com/ckb-next/ckb-next
Source0:	https://github.com/ckb-next/ckb-next/archive/refs/tags/v%{version}/ckb-next-%{version}.tar.gz
Source1:	ckb-next.appdata.xml
Source2:	ckb-next.1
Source3:	99-ckb-next.preset
Patch0:		ckb-next-0.4.2-fix-daemon.patch
#Patch1:		ckb-next-0.4.2--missing-extern-qualifiers.patch
BuildRequires:	cmake(Qt5Core)
BuildRequires:	cmake(Qt5DBus)
BuildRequires:	cmake(Qt5Widgets)
BuildRequires:	cmake(Qt5Script)
BuildRequires:	cmake(Qt5Test)
BuildRequires:	cmake(Qt5X11Extras)
BuildRequires:	cmake(Qt5LinguistTools)
BuildRequires:	cmake(QuaZip-Qt5)
BuildRequires:	qmake5
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(dbusmenu-qt5)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(gudev-1.0)
BuildRequires:	pkgconfig(udev)
BuildRequires:	pkgconfig(appindicator-0.1)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(xcb-ewmh)
BuildRequires:	desktop-file-utils
BuildRequires:	appstream-util
BuildRequires:	imagemagick
# For ckb-mviz
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libpulse-simple)

%description
Driver for Corsair gaming keyboards and mice.

This driver allows Linux to access special functionality such as
per-key background lights, and makes some keyboard variants work
despite their extremely broken firmware.

%package ui
Summary:	UI for configuring Corsair gaming keyboards and mice
Group:		Graphical desktop/KDE
Requires:	%{name} = %{EVRD}
%rename ckb-next

%description ui
UI for configuring Corsair gaming keyboards and mice

%files
%{_libexecdir}/ckb-next-daemon
%{_libexecdir}/ckb-next-sinfo
%{_unitdir}/*.service
%{_systemd_util_dir}/multi-user.target.wants/*.service
%{_bindir}/ckb-next-dev-detect
%{_presetdir}/99-ckb-next.preset
%{_udevrulesdir}/99-ckb-next-daemon.rules
%doc %{_mandir}/man1/ckb-next.1*

%files ui
%{_bindir}/ckb-next
%{_prefix}/libexec/ckb-next-animations
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/applications/*.desktop
%{_datadir}/metainfo/*.appdata.xml

%prep
%autosetup -p0 -n %{name}-next-%{version}
%cmake_qt5 -G Ninja \
	-DFORCE_INIT_SYSTEM=systemd \
	-DSAFE_INSTALL=OFF \
	-DSAFE_UNINSTALL=OFF \
	-DDISABLE_UPDATER=1 \
	-DQuaZip_LIBRARIES="quazip1-qt5" \
	-DQuaZip_INCLUDE_DIR="$(ls -d %{_includedir}/QuaZip-Qt5-*/quazip)" \
	-DUDEV_RULE_DIRECTORY=%{_udevrulesdir}

%build
%ninja_build -C build

%install
%ninja_install -C build

install -Dpm 0644 %{S:1} %{buildroot}%{_datadir}/metainfo/ckb-next.appdata.xml
install -Dpm 0644 %{S:2} %{buildroot}%{_mandir}/man1/ckb-next.1
install -Dpm 0644 %{S:3} %{buildroot}%{_presetdir}/99-ckb-next.preset
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/ckb-next.appdata.xml

for x in 128 64 32 24 22 16; do
    mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${x}x${x}/apps
    convert %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/ckb-next.png -scale ${x}x${x} %{buildroot}%{_datadir}/icons/hicolor/${x}x${x}/apps/ckb-next.png
done

mkdir -p %{buildroot}%{_systemd_util_dir}/multi-user.target.wants/
ln -s ../ckb-next-daemon.service %{buildroot}%{_systemd_util_dir}/multi-user.target.wants/
# No -devel package, so this is essentially useless
rm -rf %{buildroot}%{_libdir}/cmake
