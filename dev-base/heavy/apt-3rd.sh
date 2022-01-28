#!/bin/bash
set -e


sudo apt -y update

####### fish
sudo sudo apt-add-repository ppa:fish-shell/release-3
sudo apt-get update
sudo apt-get install -y fish

###### VSCODE

if [ ! -f /tmp/apt3-cache/code.deb ]
then
	wget "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -O /tmp/apt3-cache/code.deb --progress=dot:mega
fi
sudo apt-get install -y /tmp/apt3-cache/code.deb


########## DBEAVER
if [ ! -f /tmp/apt3-cache/dbeaver.deb ]
then
	wget https://dbeaver.io/files/dbeaver-ce_latest_amd64.deb -O /tmp/apt3-cache/dbeaver.deb --progress=dot:mega
fi
sudo apt-get -y install /tmp/apt3-cache/dbeaver.deb


# ########## keybase
# curl -s https://keybase.io/docs/server_security/code_signing_key.asc | sudo apt-key add -
# echo "deb http://prerelease.keybase.io/deb stable main" | sudo tee -a /etc/apt/sources.list.d/jp.list




# chromium
sudo tee - a /etc/apt/sources.list.d/debian.list > /dev/null <<EOL
deb http://deb.debian.org/debian buster main
deb http://deb.debian.org/debian buster-updates main
deb http://deb.debian.org/debian-security buster/updates main
EOL

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 648ACFD622F3D138
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys AA8E81B4331F7F50
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 112695A0E562B32A



sudo tee - a /etc/apt/preferences.d/chromium.pref > /dev/null <<EOL
# Note: 2 blank lines are required between entries
Package: *
Pin: release a=eoan
Pin-Priority: 500


Package: *
Pin: origin "ftp.debian.org"
Pin-Priority: 300


# Pattern includes 'chromium', 'chromium-browser' and similarly
# named dependencies:
Package: chromium*
Pin: origin "ftp.debian.org"
Pin-Priority: 700
EOL

apt update
apt install -y chromium

curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && sudo apt-get install -y nodejs


cd /tmp/apt3-cache
if [ ! -f rclone-current-linux-amd64.zip ]
then
	curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip
fi
unzip -o rclone-current-linux-amd64.zip
cd rclone-*-linux-amd64

sudo cp rclone /usr/bin/
sudo chown root:root /usr/bin/rclone
sudo chmod 755 /usr/bin/rclone

sudo mkdir -p /usr/local/share/man/man1
sudo cp rclone.1 /usr/local/share/man/man1/
sudo mandb
