%global shortcommit 38e019da
%global username plex-media-player

%global _web_client_build_id 183-045db5be50e175
%global _tv_version 4.29.6-045db5b
%global _desktop_version 4.29.2-e50e175

Name:           plex-media-player
Version:        2.58.0.1076
Release:        2%{?dist}
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
Requires(pre):  shadow-utils
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description session
This add-on to the %{name} package allows you to start the Plex Media
Player in TV mode at boot for HTPC installations.

%prep
%autosetup -p1 -n %{name}-%{version}-%{shortcommit}
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
install -p -m 0644 -D %{SOURCE10} %{buildroot}%{_metainfodir}/%{name}.appdata.xml
%endif

%check
appstream-util validate-relax --nonet %{buildroot}/%{_metainfodir}/%{name}.appdata.xml
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
%systemd_post %{name}.service

%preun session
%systemd_preun %{name}.service

%postun session
%systemd_postun %{name}.service

%if 0%{?rhel} == 7

%post
/usr/bin/update-desktop-database &> /dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :

%endif

%files
%license LICENSE
%doc README.Fedora release-notes
%{_bindir}/plexmediaplayer
%{_bindir}/pmphelper
%if 0%{?fedora}
%{_metainfodir}/%{name}.appdata.xml
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
* Sun Nov 01 2020 Simone Caronni <negativo17@gmail.com> - 2.58.0.1076-2
- Rebuild for updated dependencies.

* Fri May 29 2020 Simone Caronni <negativo17@gmail.com> - 2.58.0.1076-1
- Update to v2.58.0.1076-38e019da.

* Thu May 14 2020 Simone Caronni <negativo17@gmail.com> - 2.57.0.1074-1
- Update to v2.57.0.1074-f7d709d1.

* Sat May 09 2020 Simone Caronni <negativo17@gmail.com> - 2.56.0.1071-1
- Update to v2.56.0.1071-85947843.

* Wed Apr 15 2020 Simone Caronni <negativo17@gmail.com> - 2.55.0.1069-1
- Update to v2.55.0.1069-2369bed9.

* Fri Mar 27 2020 Simone Caronni <negativo17@gmail.com> - 2.53.0.1063-1
- Update to v2.53.0.1063-4c40422c.

* Mon Mar 16 2020 Simone Caronni <negativo17@gmail.com> - 2.52.2.1056-1
- Update to v2.52.2.1056-29c49026.

* Thu Mar 05 2020 Simone Caronni <negativo17@gmail.com> - 2.52.1.1054-1
- Update to v2.52.1.1054-86a2dc81.

* Thu Feb 20 2020 Simone Caronni <negativo17@gmail.com> - 2.51.0.1048-1
- Update to v2.51.0.1048-dda6b0b1.

* Fri Feb 07 2020 Simone Caronni <negativo17@gmail.com> - 2.50.0.1045-1
- Update to v2.50.0.1045-37e9e857.

* Sun Jan 26 2020 Simone Caronni <negativo17@gmail.com> - 2.49.0.1041-1
- Update to v2.49.0.1041-bf8608f7.

* Sat Jan 11 2020 Simone Caronni <negativo17@gmail.com> - 2.48.0.1038-1
- Update to v2.48.0.1038-11b21f57.

* Thu Dec 19 2019 Simone Caronni <negativo17@gmail.com> - 2.47.0.1035-1
- Update to v2.47.0.1035-e74d341b.

* Fri Dec 06 2019 Simone Caronni <negativo17@gmail.com> - 2.46.0.1031-1
- Update to v2.46.0.1031-6dc7c723.

* Mon Oct 21 2019 Simone Caronni <negativo17@gmail.com> - 2.44.0.1018-1
- Update to v2.44.0.1018-8f77cbb9.

* Wed Oct 09 2019 Simone Caronni <negativo17@gmail.com> - 2.43.0.1015-1
- Update to v2.43.0.1015-c1291c39.

* Thu Sep 12 2019 Simone Caronni <negativo17@gmail.com> - 2.41.0.1010-1
- Update to v2.41.0.1010-286e05db.

* Tue Sep 03 2019 Simone Caronni <negativo17@gmail.com> - 2.40.0.1007-1
- Update to v2.40.0.1007-5482132c.

* Sun Aug 18 2019 Simone Caronni <negativo17@gmail.com> - 2.39.0.1005-1
- Update to v2.39.0.1005-1b0839a8.

* Sat Jul 27 2019 Simone Caronni <negativo17@gmail.com> - 2.38.0.999-1
- Update to v2.38.0.999-e14e4d74.

* Mon Jul 22 2019 Simone Caronni <negativo17@gmail.com> - 2.37.2.996-2
- Add patches to disable screensaver with dbus and have a dark titlebar.

* Fri Jul 19 2019 Simone Caronni <negativo17@gmail.com> - 2.37.2.996-1
- Update to v2.37.2.996-bea4f9ca.

* Sun Jul 07 2019 Simone Caronni <negativo17@gmail.com> - 2.36.0.988-1
- Update to v2.36.0.988-0150ae52.

* Sun Jun 16 2019 Simone Caronni <negativo17@gmail.com> - 2.35.1.986-1
- Update to v2.35.1.986-29666b14.

* Fri Jun 07 2019 Simone Caronni <negativo17@gmail.com> - 2.34.0.983-1
- Update to v2.34.0.983-edb7fbf7.

* Sun May 12 2019 Simone Caronni <negativo17@gmail.com> - 2.33.1.979-1
- Update to v2.33.1.979-c4087ea7.

* Tue Apr 30 2019 Simone Caronni <negativo17@gmail.com> - 2.32.0.973-1
- Update to v2.32.0.973-62b2e27f.

* Thu Apr 04 2019 Simone Caronni <negativo17@gmail.com> - 2.31.0.967-1
- Update to v2.31.0.967-a95b6d76.

* Fri Mar 15 2019 Simone Caronni <negativo17@gmail.com> - 2.29.1.961-1
- Update to v2.29.1.961-bb236059.

* Fri Mar 08 2019 Simone Caronni <negativo17@gmail.com> - 2.29.0.956-1
- Update to v2.29.0.956-c81d7bae.

* Fri Feb 22 2019 Simone Caronni <negativo17@gmail.com> - 2.28.0.952-1
- Update to v2.28.0.952-5408ca22.

* Fri Feb 08 2019 Simone Caronni <negativo17@gmail.com> - 2.27.0.949-1
- Update to v2.27.0.949-542ba3ed.

* Sun Jan 27 2019 Simone Caronni <negativo17@gmail.com> - 2.26.0.947-9
- Update session systemd configuration.
- Update SPEC file.

* Thu Jan 24 2019 Simone Caronni <negativo17@gmail.com> - 2.26.0.947-8
- Update to v2.26.0.947-1e21fa2b.

* Sat Jan 12 2019 Simone Caronni <negativo17@gmail.com> - 2.25.0.940-7
- Update to v2.25.0.940-485e2ea4.

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
