%global shortcommit 4af5a622
%global username plex-media-player

Name:           plex-media-player
Version:        2.11.1.870
Release:        1%{?dist}
Summary:        Next generation Plex Desktop client
License:        GPLv2
URL:            https://www.plex.tv/apps/computer/plex-media-player/

Source0:        https://github.com/plexinc/%{name}/archive/v%{version}-%{shortcommit}.tar.gz#/%{name}-%{version}-%{shortcommit}.tar.gz
Source2:        %{name}.appdata.xml
Source3:        %{name}.pkla
Source4:        %{name}.service
Source5:        %{name}.target
Source10:       README.Fedora

%if 0%{?rhel} == 7
BuildRequires:  cmake3 >= 3.1.0
%else
BuildRequires:  cmake >= 3.1.0
%endif

BuildRequires:  alsa-lib-devel
BuildRequires:  desktop-file-utils
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  fribidi-devel
BuildRequires:  gnutls-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
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
BuildRequires:  qt5-qtbase-devel >= 5.6
BuildRequires:  qt5-qtdeclarative-devel >= 5.6
BuildRequires:  qt5-qtwebchannel-devel >= 5.6
BuildRequires:  qt5-qtwebengine-devel >= 5.6
BuildRequires:  qt5-qtx11extras-devel >= 5.6
BuildRequires:  SDL2-devel
BuildRequires:  uchardet-devel
BuildRequires:  yasm
BuildRequires:  zlib-devel

Requires:       qt5-qtquickcontrols >= 5.6

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
%autosetup -n %{name}-%{version}-%{shortcommit}
cp %{SOURCE10} .
mkdir build

%build
pushd build
%if 0%{?rhel} == 7
%cmake3 \
%else
%cmake \
%endif
    -DQTROOT="%{_qt5_prefix}" \
    ..
popd

%install
pushd build
%make_install
popd

# Desktop icon
install -p -m 0644 -D resources/images/icon.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

# Install session files
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/

install -p -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/
install -p -m 0644 %{SOURCE4} %{SOURCE5} %{buildroot}%{_unitdir}

%if 0%{?fedora}
# Install Gnome Software metadata
install -p -m 0644 -D %{SOURCE2} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml
%endif

%check
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/appdata/%{name}.appdata.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/plexmediaplayer.desktop

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
%if 0%{?fedora}
%systemd_post %{name}.service

%preun session
%systemd_preun %{name}.service

%postun session
%systemd_postun %{name}.service
%endif

%post
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif

%postun
%if 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif

%files
%license LICENSE
%doc README.Fedora release-notes
%{_bindir}/plexmediaplayer
%{_bindir}/pmphelper
%if 0%{?fedora}
%{_datadir}/appdata/%{name}.appdata.xml
%endif
%{_datadir}/applications/plexmediaplayer.desktop
%{_datadir}/icons/hicolor/scalable/apps/plexmediaplayer.svg
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/plexmediaplayer

%files session
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.target
%{_sysconfdir}/polkit-1/localauthority/50-local.d/%{name}.pkla
%attr(750,%{username},%{username}) %{_sharedstatedir}/%{name}

%changelog
* Mon Jun 11 2018 Simone Caronni <negativo17@gmail.com> - 2.11.1.870-1
- Update to v2.11.1.870-4af5a622.

* Thu May 31 2018 Simone Caronni <negativo17@gmail.com> - 2.11.0.867-1
- Update to 2.11.0.867-f27f8d2a.
- Remove conan/pip part.

* Mon Jan 08 2018 Simone Caronni <negativo17@gmail.com> - 2.2.1.758-1
- Update to 2.2.1.758-5dad2d62.

* Tue Dec 19 2017 Simone Caronni <negativo17@gmail.com> - 1.3.12.755-1
- Update to version 1.3.12.755-fed6185a.

* Mon Oct 30 2017 Simone Caronni <negativo17@gmail.com> - 1.3.10.720-1
- Update to 1.3.10.720-dfcd90a6.

* Thu Sep 21 2017 Simone Caronni <negativo17@gmail.com> - 1.3.5.689-1
- Update to 1.3.5.689-a36fa532.

* Thu Jun 22 2017 Simone Caronni <negativo17@gmail.com> - 1.3.4.670-1
- Update to 1.3.4.670-1d4f6da1.

* Thu Jun 01 2017 Simone Caronni <negativo17@gmail.com> - 1.3.2.657-1
- First build for version 1.3.2.657-21cb31b8.
