#!/bin/bash
#
# Purpose:
#   Configures an Ubuntu SIFT workstation to use the macOS (and iOS)
#   Artifact Parsing Tool (mac_apt), created by Yogesh Khatri
#   (@swiftforensics): https://github.com/ydkhatri/mac_apt
#
# Requirements:
#   Must be run as root. Assumes `pip` resolves to python3-pip and `python`
#   resolves to Python 3.7+.
#
# Usage:
#   ./sift_mac_apt.sh
#
# Warning:
#   This script uses the potentially dangerous --ignore-installed switch on
#   pip3 to avoid an issue with PyYAML. This may leave your system unstable.
#   If this is an issue, consider using a venv instead.

set -euo pipefail

# Check Requirements
if [[ $EUID != 0 ]]; then
    echo "[!] This script must be run with root privileges!"
    echo "[!] Exiting"
    exit 255
else
    echo "[ ] Initial check completed, script is running with correct privileges."
fi

# Update repos.
echo "[ ] Updating repositories. You might get prompted for answers."
apt update && apt install -y python3-pip python3-dev libbz2-dev zlib1g-dev

# Clone gits
echo -e "\n\n\n[*] Seting up mac_apt now."
cd /opt || exit 1
wget https://github.com/libyal/libewf-legacy/releases/download/20140808/libewf-20140808.tar.gz
tar xzf libewf-20140808.tar.gz
rm libewf-20140808.tar.gz
cd /opt/libewf-20140808 || exit 1
python setup.py build
python setup.py install
cd /opt || exit 1
git clone https://github.com/ydkhatri/mac_apt
cd /opt/mac_apt || exit 1
pip3 install ./other_dependencies/pyaff4-0.31-yk.zip --ignore-installed
pip3 install anytree biplist construct==2.9.45 xlsxwriter plistutils kaitaistruct lz4 pytsk3==20170802 libvmdk-python==20181227 pycryptodome cryptography pybindgen==0.21.0 pillow pyliblzfse nska_deserialize
cd 
# Install completed

echo "[ ] Install Completed."
echo "[ ] You can now run mac_apt as follows"
echo "python /opt/mac_apt/mac_apt.py -h"

