%global shortcommit 21cb31b8
%global username plex-media-player

Name:           plex-media-player
Version:        1.3.2.657
Release:        1%{?dist}
Summary:        Next generation Plex Desktop client
License:        GPLv2
URL:            https://www.plex.tv/apps/computer/plex-media-player/

Source0:        https://github.com/plexinc/%{name}/archive/v%{version}-%{shortcommit}.tar.gz#/%{name}-%{version}-%{shortcommit}.tar.gz
Source1:        %{name}.desktop
Source2:        %{name}.appdata.xml
Source3:        %{name}.pkla.disabled
Source4:        %{name}.service
Source5:        95-%{name}.preset

Patch0:         %{name}-1.3.2-webengine.patch

BuildRequires:  alsa-lib-devel
BuildRequires:  cmake >= 3.1.0
BuildRequires:  desktop-file-utils
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  fribidi-devel
BuildRequires:  gnutls-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  harfbuzz-devel
BuildRequires:  libappstream-glib
BuildRequires:  libcec-devel >= 4.0.0
BuildRequires:  libva-devel
BuildRequires:  libvdpau-devel
BuildRequires:  libX11-devel
BuildRequires:  libXrandr-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mpv-libs-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  systemd
BuildRequires:  qt5-devel >= 5.7
BuildRequires:  qt5-qtwebengine-devel >= 5.7
BuildRequires:  SDL2-devel
BuildRequires:  uchardet-devel
BuildRequires:  yasm
BuildRequires:  zlib-devel

Requires:       qt5-qtquickcontrols >= 5.7

%description
Plex Media Player is the go-to app for Home Theater PCs (HTPCs) connected to big
screen TVs. Your collection of videos, music, and photos never looked so good!

%package session
Summary:        Plex Embedded Client
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description session
This add-on to the %{name} package allows you to start the Plex Media
Player in TV mode at boot for HTPC installations.

%prep
%autosetup -p1 -n %{name}-%{version}-%{shortcommit}
mkdir build

# Dirty hack to avoid having a system conan
pip3 install --user conan
~/.local/bin/conan remote add plex https://conan.plex.tv

%build
pushd build
~/.local/bin/conan install ..
%cmake \
    -DQTROOT="%{_qt5_prefix}" \
    ..
popd

%install
pushd build
%make_install
popd

# Desktop icon
desktop-file-install --dir %{buildroot}%{_datadir}/applications/ %{SOURCE1}
install -p -m 0644 -D resources/images/icon.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

# Install session files
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_presetdir}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/

install -p -m 0644 -D %{SOURCE3} %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/
install -p -m 0644 -D %{SOURCE4} %{buildroot}%{_unitdir}
install -p -m 0644 -D %{SOURCE5} %{buildroot}%{_presetdir}

%if 0%{?fedora} >= 25
# Install Gnome Software metadata
install -p -m 0644 -D %{SOURCE2} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml
%endif

%check
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

# Apply the systemd preset for plex-media-player.service when upgrading from
# a version without plex-media-player.service, as %%systemd_post only does this
# on fresh installs
%if 0%{?fedora} >= 25
%triggerun -- %{name} < 1.3.2.657-1
systemctl --no-reload preset plex-media-player.service >/dev/null 2>&1 || :
%endif

%pre session
getent group %username >/dev/null || groupadd -r %username &>/dev/null || :
getent passwd %username >/dev/null || useradd -r -M \
    -s /sbin/nologin \
    -d %{_sharedstatedir}/%{name} \
    -c 'Plex Media Player' \
    -G dialout,video,lock,audio \
    -g %username %username &>/dev/null || :
exit 0

%post session
%if 0%{?fedora} >= 25
%systemd_post %{name}.service

%preun session
%systemd_preun %{name}.service

%postun session
%systemd_postun %{name}.service
%endif

%post
%if 0%{?fedora} == 24 || 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif

%postun
%if 0%{?fedora} == 24 || 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif

%files
%license LICENSE
%{_bindir}/plexmediaplayer
%{_bindir}/pmphelper
%if 0%{?fedora} >= 25
%{_datadir}/appdata/%{name}.appdata.xml
%endif
%{_datadir}/applications/%{name}.desktop
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/plexmediaplayer

%files session
%{_unitdir}/%{name}.service
%{_presetdir}/95-%{name}.preset
%{_sysconfdir}/polkit-1/localauthority/50-local.d/%{name}.pkla.disabled
%attr(750,%{username},%{username}) %{_sharedstatedir}/%{name}

%changelog
* Thu Jun 01 2017 Simone Caronni <negativo17@gmail.com> - 1.3.2.657-1
- First build for version 1.3.2.657-21cb31b8.
