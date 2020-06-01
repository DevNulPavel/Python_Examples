#! /usr/bin/env bash

SERVICE_NAME=com.gameinsight.distcc
PLIST_FOLDER=/Library/LaunchDaemons

sudo launchctl stop $SERVICE_NAME
sudo launchctl unload $PLIST_FOLDER/com.gameinsight.distcc.plist

echo "Stopped"