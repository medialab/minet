#!/bin/bash
set -e

# Checking for necessary commands
fail_deps() {
  echo
  echo "Missing required dependencies for this script to work."
  echo "Please install \"curl\" and \"unzip\" before running the script again."
  echo ""
  echo "On ubuntu, debian etc. you can do so by running:"
  echo "  $ sudo apt install curl unzip"
  echo
  exit 1
}

if ! command -v unzip &> /dev/null; then
  fail_deps
elif ! command -v curl &> /dev/null; then
  fail_deps
fi

# Asking for sudo right away
echo
echo "This install script will ask you for your password so it can move/copy"
echo "things to '/usr/local/bin'. If you are not comfortable with this you can"
echo "read the install script here:"
echo "https://github.com/medialab/minet/blob/master/scripts/install.sh"
echo

sudo echo "test" > /dev/null

# Functions
get_latest_release() {
  curl -sSL "https://api.github.com/repos/$1/releases/latest" |
    grep '"tag_name":' |
    sed -E 's/.*"([^"]+)".*/\1/'
}

cleanup() {
  rm -rf /tmp/minet
  rm -f /tmp/minet.zip
  sudo rm -rf /usr/local/bin/minet-dist
  sudo rm -f /usr/local/bin/minet
}

get_ubuntu_version() {
  (cat /etc/os-release | grep VERSION_ID | grep -Po '[0-9]{2}(?=[\."])' | head -n 1) || echo "unknown"
}

fail_install() {
  echo "Installation not supported on this OS, sorry :("
  echo
  echo "You can still install minet through python:"
  echo "  $ pip install minet"
  echo
  exit 1
}

fail_download() {
  echo
  echo "The zipped file was not able to be downladed. This might be because the rate limit of GitHub's API was reached. Please wait a few moments and launch the command again."
  echo
  exit 1
}

# Variables
os="unknown"

if [[ $(uname -s) == "Darwin" ]]; then
  os="macos"
  echo "Installing minet for mac..."
elif cat /etc/os-release | grep -q "Debian GNU/Linux"; then
  os="ubuntu_18"
  echo "Installing minet for debian..."
else
  ubuntu_version=$(get_ubuntu_version)

  if [[ $ubuntu_version != "unkown" ]]; then
    echo "Installing minet for ubuntu $ubuntu_version (or similar)..."

    if [[ $ubuntu_version -le "18" ]]; then
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

# Verify that the GitHub API returned the latest released version
if [ -z "$latest" ]; then
  fail_download
fi

# Generic install script
cleanup

echo "Downloading $os binaries for $latest release..."
mkdir /tmp/minet
curl -sSL  "https://github.com/medialab/minet/releases/download/$latest/$os.zip" > /tmp/minet.zip

echo "Installing..."
unzip -qq /tmp/minet.zip -d /tmp/minet/
rm /tmp/minet.zip
sudo mv /tmp/minet /usr/local/bin/minet-dist
sudo chmod +x /usr/local/bin/minet-dist/minet
sudo ln -s /usr/local/bin/minet-dist/minet /usr/local/bin/minet

echo "Installed:"
minet --version
