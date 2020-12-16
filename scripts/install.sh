#!/bin/bash

# Functions
get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" |
    grep '"tag_name":' |
    sed -E 's/.*"([^"]+)".*/\1/'
}

cleanup() {
  rm -rf /tmp/minet
  rm -f /tmp/minet.zip
  rm -rf /usr/local/bin/minet-dist
  rm /usr/local/bin/minet
}

# Variables
name=$(uname -s)
latest=$(get_latest_release medialab/minet)

# Generic install script
if [[ $name == "Darwin" ]]; then
  cleanup
  echo "Downloading binaries..."
  mkdir /tmp/minet
  curl -L "https://github.com/medialab/minet/releases/download/$latest/macos.zip" > /tmp/minet.zip
  echo "Installing..."
  unzip -qq /tmp/minet.zip -d /tmp/minet/
  rm /tmp/minet.zip
  mv /tmp/minet /usr/local/bin/minet-dist
  printf "#!/bin/bash\\n/usr/local/bin/minet-dist/minet \$@" > /usr/local/bin/minet
  chmod +x /usr/local/bin/minet
  chmod +x /usr/local/bin/minet-dist/minet
  echo "Now correctly installed for version:"
  minet --version
else
  echo "Installation not supported on $name yet."
fi
