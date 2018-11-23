%define snapshot 20181123
Summary:	Driver for Corsair gaming keyboards and mice
Name:		ckb
Version:	0.3.2
Release:	0.%{snapshot}.1
Epoch:		1
Group:		Graphical desktop/KDE
License:	GPLv2 LGPLv2 GFDL
Url:		https://github.com/ckb-next/ckb-next
Source0:	https://github.com/ckb-next/ckb-next/archive/master.tar.gz
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5DBus)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	pkgconfig(Qt5Script)
BuildRequires:	pkgconfig(Qt5Test)
BuildRequires:	pkgconfig(quazip)
BuildRequires:	qmake5 cmake ninja
BuildRequires:	imagemagick
# For ckb-mviz
BuildRequires:	pkgconfig(libpulse) pkgconfig(libpulse-simple)

%description
Driver for Corsair gaming keyboards and mice.

This driver allows Linux to access special functionality such as
per-key background lights, and makes some keyboard variants work
despite their extremely broken firmware.

%package ui
Summary:	UI for configuring Corsair gaming keyboards and mice
Group:		Graphical desktop/KDE
Requires:	%{name} = %{EVRD}

%description ui
UI for configuring Corsair gaming keyboards and mice

%files
%{_bindir}/ckb-next-daemon
/lib/systemd/system/*.service
/lib/systemd/system/multi-user.target.wants/*.service
%{_sysconfdir}/udev/rules.d/99-ckb-daemon.rules
%{_bindir}/ckb-next-dev-detect

%files ui
%{_bindir}/ckb-next
%{_prefix}/libexec/ckb-next-animations
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/applications/*.desktop

%prep
%setup -qn %{name}-next-master
%apply_patches
%cmake_qt5 -G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build

mkdir -p %{buildroot}%{_sbindir} %{buildroot}%{_bindir} %{buildroot}%{_prefix}/lib %{buildroot}%{_datadir}/applications %{buildroot}/lib/systemd/system/multi-user.target.wants
for x in 128 64 32 24 22 16; do
	mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${x}x${x}/apps
	convert %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/ckb-next.png -scale ${x}x${x} %{buildroot}%{_datadir}/icons/hicolor/${x}x${x}/apps/ckb-next.png
done
mkdir -p %{buildroot}/lib/systemd/system/multi-user.target.wants
mv %{buildroot}%{_libdir}/systemd/system/* %{buildroot}/lib/systemd/system
rm -rf %{buildroot}%{_libdir}/systemd
ln -s ../ckb-next-daemon.service %{buildroot}/lib/systemd/system/multi-user.target.wants/
# No -devel package, so this is essentially useless
rm -rf %{buildroot}%{_libdir}/cmake
