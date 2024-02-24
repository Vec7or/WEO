#!/bin/bash

while getopts "u:p:" option; do
  case $option in
    u) # Username
        username=$OPTARG;;
    p) # Password
        password=$OPTARG;;
    \?) # Invalid option
      echo "Error: Invalid option"
      exit;;
  esac
done

if [ -z ${username+x} ]; 
then 
  echo "username is required";
  exit 1;
fi

if [ -z ${password+x} ]; 
then 
  echo "password is required";
  exit 1;
fi

WEO_REPO_DIR="/opt/weo"
# Prepare git directory
mkdir -p $WEO_REPO_DIR
chown $username:$username $WEO_REPO_DIR
echo "export WEO_REPO_DIR=$WEO_REPO_DIR" > /etc/profile.d/weo.sh
# Change to user
sudo -i -u $username bash << EOF
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
sudo printf "[user]\nusername=$username\npassword=$password\n" > /etc/weo.conf
sudo chown $username:$username /etc/weo.conf
sudo chmod 600 /etc/weo.conf