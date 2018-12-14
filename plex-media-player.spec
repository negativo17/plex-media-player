%global shortcommit 63fcaa8e
%global username plex-media-player

%global _web_client_build_id 87-ac3c1b07015f76
%global _tv_version 3.80.1-ac3c1b0
%global _desktop_version 3.77.2-7015f76

Name:           plex-media-player
Version:        2.24.0.924
Release:        6%{?dist}
Summary:        Next generation Plex Desktop client
License:        GPLv2
URL:            https://www.plex.tv/apps/computer/plex-media-player/

Source0:        https://github.com/plexinc/%{name}/archive/v%{version}-%{shortcommit}.tar.gz#/%{name}-%{version}-%{shortcommit}.tar.gz
Source1:        https://artifacts.plex.tv/web-client-pmp/%{_web_client_build_id}/buildid.cmake#/buildid-%{_web_client_build_id}.cmake
Source2:        https://artifacts.plex.tv/web-client-pmp/%{_web_client_build_id}/web-client-desktop-%{_desktop_version}.tar.xz
Source3:        https://artifacts.plex.tv/web-client-pmp/%{_web_client_build_id}/web-client-desktop-%{_desktop_version}.tar.xz.sha1
Source4:        https://artifacts.plex.tv/web-client-pmp/%{_web_client_build_id}/web-client-tv-%{_tv_version}.tar.xz
Source5:        https://artifacts.plex.tv/web-client-pmp/%{_web_client_build_id}/web-client-tv-%{_tv_version}.tar.xz.sha1

Source10:        %{name}.appdata.xml
Source11:        %{name}.pkla
Source12:        %{name}.service
Source13:        %{name}.target
Source14:       README.Fedora

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
cp %{SOURCE14} .

mkdir -p build/dependencies
cp  %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} build/dependencies/

%build
# This makes build stop if any download is attempted
export http_proxy=http://127.0.0.1

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

install -p -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/
install -p -m 0644 %{SOURCE12} %{SOURCE13} %{buildroot}%{_unitdir}

%if 0%{?fedora}
# Install Gnome Software metadata
install -p -m 0644 -D %{SOURCE10} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml
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
* Fri Dec 14 2018 Simone Caronni <negativo17@gmail.com> - 2.24.0.924-6
- Update to v2.24.0.924-63fcaa8e.

* Sat Dec 01 2018 Simone Caronni <negativo17@gmail.com> - 2.23.0.920-5
- Update to v2.23.0.920-5bc1a2e5.

* Mon Nov 26 2018 Simone Caronni <negativo17@gmail.com> - 2.22.1.917-4
- Update to v2.22.1.917-2a5a2e01.

* Thu Nov 01 2018 Simone Caronni <negativo17@gmail.com> - 2.21.0.914-3
- Update to v2.21.0.914-4839cbf2.

* Fri Oct 19 2018 Simone Caronni <negativo17@gmail.com> - 2.20.0.909-2
- Do not let rpmbuild download source files.
- Add helper scripts to fill versions in SPEC file.

* Thu Oct 04 2018 Simone Caronni <negativo17@gmail.com> - 2.20.0.909-1
- Update to v2.20.0.909-46413dd1.

* Wed Sep 19 2018 Simone Caronni <negativo17@gmail.com> - 2.19.0.902-1
- Update to v2.19.0.902-42a9f589.

* Mon Sep 10 2018 Simone Caronni <negativo17@gmail.com> - 2.18.0.893-1
- Update to v2.18.0.893-48795f25.

* Sun Aug 19 2018 Simone Caronni <negativo17@gmail.com> - 2.16.0.885-1
- Update to v2.16.0.885-f2338b5e.

* Wed Jul 25 2018 Simone Caronni <negativo17@gmail.com> - 2.15.0.882-1
- Update to v2.15.0.882-8b488458.

* Tue Jul 17 2018 Simone Caronni <negativo17@gmail.com> - 2.14.1.880-1
- Update to v2.14.1.880-301a4b6c.

* Wed Jul 04 2018 Simone Caronni <negativo17@gmail.com> - 2.13.0.877-1
- Update to v2.13.0.877-6e1ea2cb.

* Fri Jun 22 2018 Simone Caronni <negativo17@gmail.com> - 2.12.1.871-1
- Update to v2.12.1.871-6c71195e.

* Wed Jun 13 2018 Simone Caronni <negativo17@gmail.com> - 2.12.0.869-1
- Update to v2.12.0.869-010a1af4.

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
