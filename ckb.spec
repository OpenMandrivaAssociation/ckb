%define snapshot 20171011
Summary:	Driver for Corsair gaming keyboards and mice
Name:		ckb
Version:	0.2.9
Release:	0.%{snapshot}.1
Epoch:		1
Group:		Graphical desktop/KDE
License:	GPLv2 LGPLv2 GFDL
Url:		https://github.com/mattanger/ckb-next
Source0:	https://github.com/mattanger/ckb-next/archive/master.tar.gz
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5DBus)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	pkgconfig(Qt5Script)
BuildRequires:	pkgconfig(Qt5Test)
BuildRequires:	qmake5
BuildRequires:	imagemagick

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
%{_sbindir}/ckb-daemon
/lib/systemd/system/*.service
/lib/systemd/system/multi-user.target.wants/*.service

%files ui
%{_bindir}/ckb
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/applications/*.desktop

%prep
%setup -qn %{name}-next-master
%apply_patches
# Workaround for weirdo (ASCII-ish?) comparison that thinks
# Qt 5.10 is older than 5.2...
sed -i -e 's|QT_VERSION, 5.2|QT_VERSION, 5.10|' ckb.pro
./qmake-auto

%build
%make

%install
mkdir -p %{buildroot}%{_sbindir} %{buildroot}%{_bindir} %{buildroot}%{_datadir}/applications %{buildroot}/lib/systemd/system/multi-user.target.wants
for x in 512 128 64 32 24 22 16; do
	mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${x}x${x}/apps
	convert usr/ckb.png -scale ${x}x${x} %{buildroot}%{_datadir}/icons/hicolor/${x}x${x}/apps/ckb.png
done
cp usr/ckb.desktop %{buildroot}%{_datadir}/applications/
sed -e 's,/usr/bin,%{_sbindir},g' service/systemd/ckb-daemon.service >%{buildroot}/lib/systemd/system/ckb-daemon.service
ln -s ../ckb-daemon.service %{buildroot}/lib/systemd/system/multi-user.target.wants/
cp -a bin/ckb %{buildroot}%{_bindir}/
cp -a bin/ckb-daemon %{buildroot}%{_sbindir}/
