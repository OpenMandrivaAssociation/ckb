%define snapshot %{nil}

Summary:	Driver for Corsair gaming keyboards and mice
Name:		ckb
Version:	0.6.2
Release:	1
Group:		Graphical desktop/KDE
License:	GPL-2.0-only
Url:		https://github.com/ckb-next/ckb-next
Source0:	https://github.com/ckb-next/ckb-next/archive/refs/tags/v%{version}/ckb-next-%{version}.tar.gz
Source1:	ckb-next.appdata.xml
Source2:	ckb-next.1
Source3:	99-ckb-next.preset
# Patch CMakeLists.txt to enable Qt6 if -DPREFER_QT6=ON
# Patch submitted to upstream as: https://github.com/ckb-next/ckb-next/pull/1155
Patch0:		ckb-next-0.6.2-cmakelist-qt6.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	git
BuildRequires:	cmake(Qt6Core)
BuildRequires:	cmake(Qt6Core5Compat)
BuildRequires:	cmake(Qt6DBus)
BuildRequires:	cmake(Qt6Gui)
BuildRequires:	cmake(Qt6LinguistTools)
BuildRequires:	cmake(Qt6Network)
BuildRequires:	cmake(Qt6OpenGLWidgets)
BuildRequires:	cmake(Qt6Widgets)
BuildRequires:	cmake(QuaZip-Qt6)
BuildRequires:	cmake(VulkanHeaders)
BuildRequires:	appstream-util
BuildRequires:	desktop-file-utils
BuildRequires:	imagemagick
BuildRequires:	pkgconfig(appindicator3-0.1)
BuildRequires:	pkgconfig(dbusmenu-qt6)
BuildRequires:	pkgconfig(default-icon-theme)
BuildRequires:	pkgconfig(gudev-1.0)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libpulse-simple)
BuildRequires:	pkgconfig(libudev)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	pkgconfig(xcb)
BuildRequires:	pkgconfig(xcb-ewmh)
BuildRequires:	pkgconfig(xcb-screensaver)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	qt6-qtbase-theme-gtk3
BuildRequires:	systemd-rpm-macros

# In prior packaged versions the ui component was a separate package.
Obsoletes: %{name}-ui < 0.6.2

%description
ckb-next is an open-source driver for Corsair keyboards and mice.

It aims to bring the features of Corsair's proprietary CUE software
to Linux operating systems. This project is currently a work in
progress, but it already supports much of the same functionality,
including full RGB animations.

%rename ckb-next

%prep
%autosetup -n %{name}-next-%{version} -p1
# Remove remote image/badge URLs from README
sed -i -e '3d;9d;' README.md

%cmake \
	-DPREFER_QT6=ON \
	-DSAFE_INSTALL=OFF \
	-DSAFE_UNINSTALL=OFF \
	-DDISABLE_UPDATER=1 \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCMAKE_INSTALL_LIBEXECDIR=libexec \
	-DFORCE_INIT_SYSTEM=systemd \
	-DUDEV_RULE_DIRECTORY=%{_udevrulesdir} \
	-DQuaZip_LIBRARIES="quazip1-qt6" \
	-DQuaZip_INCLUDE_DIR="$(ls -d %{_includedir}/QuaZip-Qt6-*/quazip)" \
	-G Ninja

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
# Build generates cmake target definition files from src/animations/mviz/CMakeLists.txt
# from behind the USE_PORTAUDIO parameter, their purpose is undocumented by
# upstream and not used by the package itself.
# Unless that situation changes and they create a devel package we dont need them.
# No -devel package, so this is essentially useless
rm -rf %{buildroot}%{_libdir}/cmake

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ckb-next.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/ckb-next.appdata.xml

%post
%systemd_post ckb-next-daemon.service
if [ $1 -eq 1 ]; then
    # start daemon after installing
    systemctl start ckb-next-daemon.service >/dev/null 2>&1 || :
fi
# reload udev rules
udevadm control --reload-rules 2>&1 > /dev/null || :

%preun
%systemd_preun ckb-next-daemon.service

%postun
%systemd_postun_with_restart ckb-next-daemon.service
# reload udev rules
udevadm control --reload-rules 2>&1 > /dev/null || :


%files
%{_bindir}/ckb-next
%{_bindir}/ckb-next-daemon
%{_bindir}/ckb-next-dev-detect
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/metainfo/*.appdata.xml
%{_libexecdir}/ckb-next-sinfo
%{_libexecdir}/ckb-next-animations
%{_presetdir}/99-ckb-next.preset
%{_systemd_util_dir}/multi-user.target.wants/*.service
%{_udevrulesdir}/99-ckb-next-daemon.rules
%{_unitdir}/*.service
%doc %{_mandir}/man1/ckb-next.1*
%doc README.md
%doc FIRMWARE
%license LICENSE
