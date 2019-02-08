#!/bin/sh -x

PMP_TAG=$1
PMP_VERSION=$(echo $PMP_TAG | sed -e 's/-.*//g' -e 's/^v//g')
PMP_SHORTCOMMIT=$(echo $PMP_TAG | sed -e 's/.*-//g')

rm -f *tar.gz *tar.xz *tar.xz.sha1 *cmake

wget -c https://github.com/plexinc/plex-media-player/archive/$PMP_TAG.tar.gz \
  -O plex-media-player-$PMP_VERSION-$PMP_SHORTCOMMIT.tar.gz

tar -xzf plex-media-player-$PMP_VERSION-$PMP_SHORTCOMMIT.tar.gz --strip-components=2 \
  plex-media-player-$PMP_VERSION-$PMP_SHORTCOMMIT/CMakeModules/WebClient.cmake

WEB_CLIENT_BUILD_ID=$(grep "set(WEB_CLIENT_BUILD_ID" WebClient.cmake | awk '{print $2}' | tr -d \))

wget -c https://artifacts.plex.tv/web-client-pmp/$WEB_CLIENT_BUILD_ID/buildid.cmake

TV_VERSION=$(grep "set(TV_VERSION" buildid.cmake | awk '{print $2}' | tr -d \))
DESKTOP_VERSION=$(grep "set(DESKTOP_VERSION" buildid.cmake | awk '{print $2}' | tr -d \))

rm -f WebClient.cmake buildid.cmake

sed -i \
    -e "s|%global shortcommit.*|%global shortcommit ${PMP_SHORTCOMMIT}|g" \
    -e "s|Version:.*|Version:        ${PMP_VERSION}|g" \
    -e "s|%global _web_client_build_id.*|%global _web_client_build_id ${WEB_CLIENT_BUILD_ID}|g" \
    -e "s|%global _tv_version.*|%global _tv_version ${TV_VERSION}|g" \
    -e "s|%global _desktop_version.*|%global _desktop_version ${DESKTOP_VERSION}|g" \
    plex-media-player.spec

rpmdev-bumpspec -c "Update to $PMP_TAG." -n $PMP_VERSION plex-media-player.spec

rm -f *xz *sha1 *gz

spectool -g plex-media-player.spec
