#!/bin/bash
WEO_REPO_DIR="/opt/weo"
# Prepare git directory
mkdir -p $WEO_REPO_DIR
chown development:development $WEO_REPO_DIR
echo "export WEO_REPO_DIR=$WEO_REPO_DIR" > /etc/profile.d/weo.sh
# Change to user
sudo -i -u development bash << EOF
# Install ansible
pip install pipx
python3 -m pipx ensurepath
python3 -m pipx install --include-deps ansible
python3 -m pipx inject --include-apps ansible argcomplete
# Get git repository
cd $WEO_REPO_DIR
echo $PWD
git clone https://github.com/Vec7or/WEO.git .
git checkout main
EOF