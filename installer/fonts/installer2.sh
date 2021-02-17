#!/usr/bin/bash

mount -o remount,rw /system
# install font
cp -rf /data/openpilot/installer/fonts/NanumGothic* /system/fonts/
# install font to /data/openpilot/selfdrive/assets/fonts/
cp -rf /data/openpilot/installer/fonts/opensans_* /data/openpilot/selfdrive/assets/fonts/
# install font mapping
cp -rf /data/openpilot/installer/fonts/fonts.xml /system/etc/fonts.xml
# change permissions
chmod 644 /system/etc/fonts.xml
chmod 644 /system/fonts/NanumGothic*
