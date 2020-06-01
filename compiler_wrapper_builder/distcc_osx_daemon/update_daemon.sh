#! /usr/bin/env bash

SERVICE_NAME=com.gameinsight.distcc
PLIST_NAME=com.gameinsight.distcc.plist
PLIST_FOLDER=/Library/LaunchDaemons
PLIST_PATH=$PLIST_FOLDER/$PLIST_NAME

sudo launchctl unload $PLIST_PATH
sudo cp $PLIST_NAME $PLIST_PATH
sudo chmod 644 $PLIST_PATH
sudo chown root:wheel $PLIST_PATH

echo "Updated"