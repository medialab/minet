#!/bin/bash
echo
echo "This uninstall script will ask you for your password so it can remove"
echo "things from '/usr/local/bin'. If you are not comfortable with this you can"
echo "read the uninstall script here:"
echo "https://github.com/medialab/minet/blob/master/scripts/uninstall.sh"
echo

sudo rm -rf /usr/local/bin/minet-dist
sudo rm -f /usr/local/bin/minet
echo "minet successfully uninstalled!"
