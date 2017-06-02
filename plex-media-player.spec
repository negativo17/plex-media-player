%global shortcommit 21cb31b8

Name:           plex-media-player
Version:        1.3.2.657
Release:        1%{?dist}
Summary:        Next generation Plex Desktop/Embedded Client
License:        GPLv2
URL:            https://www.plex.tv/apps/computer/plex-media-player/

Source0:        https://github.com/plexinc/%{name}/archive/v%{version}-%{shortcommit}.tar.gz#/%{name}-%{version}-%{shortcommit}.tar.gz
Patch0:         %{name}-1.3.2-webengine.patch

BuildRequires:  alsa-lib-devel
BuildRequires:  cmake >= 3.1.0
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  fribidi-devel
BuildRequires:  gnutls-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  harfbuzz-devel
BuildRequires:  libcec-devel >= 4.0.0
BuildRequires:  libva-devel
BuildRequires:  libvdpau-devel
BuildRequires:  libX11-devel
BuildRequires:  libXrandr-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mpv-libs-devel
BuildRequires:  pulseaudio-libs-devel
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

%files
%license LICENSE
%{_bindir}/plexmediaplayer
%{_bindir}/pmphelper
%{_datadir}/plexmediaplayer

%changelog
* Thu Jun 01 2017 Simone Caronni <negativo17@gmail.com> - 1.3.2.657-1
- First build for version 1.3.2.657-21cb31b8.
