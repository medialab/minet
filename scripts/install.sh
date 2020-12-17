#!/bin/bash
set -e

# Functions
get_latest_release() {
  curl -S -s -L "https://api.github.com/repos/$1/releases/latest" |
    grep '"tag_name":' |
    sed -E 's/.*"([^"]+)".*/\1/'
}

cleanup() {
  rm -rf /tmp/minet
  rm -f /tmp/minet.zip
  rm -f /tmp/minet-exec
  sudo rm -rf /usr/local/bin/minet-dist
  sudo rm -f /usr/local/bin/minet
}

get_ubuntu_version() {
  (cat /etc/os-release | grep VERSION_ID | grep -Po "[0-9]{2}(?=\.)") || "unknown"
}

fail_install() {
  echo "Installation not supported on this OS, sorry :("
  exit 1
}

# Variables
os="unknown"

if [[ $(uname -s) == "Darwin" ]]; then
  os="macos"
  echo "Installing minet for mac..."
else
  ubuntu_version=$(get_ubuntu_version)

  if [[ $ubuntu_version != "unkown" ]]; then
    echo "Installing minet for ubuntu (or similar)..."

    if [ $ubuntu_version -le "16" ]; then
      os="ubuntu_16"
    elif [[ $ubuntu_version == "18" || $ubuntu_version == "17" ]]; then
      os="ubuntu_18"
    else
      os="ubuntu_20"
    fi
  else
    fail_install
  fi
fi

# Finding latest released version
latest=$(get_latest_release medialab/minet)

# Generic install script
cleanup

echo "Downloading binaries..."
mkdir /tmp/minet
curl -S -s -L  "https://github.com/medialab/minet/releases/download/$latest/$os.zip" > /tmp/minet.zip

echo "Installing..."
unzip -qq /tmp/minet.zip -d /tmp/minet/
rm /tmp/minet.zip
sudo mv /tmp/minet /usr/local/bin/minet-dist
printf '#!/bin/bash\n/usr/local/bin/minet-dist/minet $@' > /tmp/minet-exec
sudo mv /tmp/minet-exec /usr/local/bin/minet
sudo chmod +x /usr/local/bin/minet
sudo chmod +x /usr/local/bin/minet-dist/minet

echo "Installed:"
minet --version
