#!/bin/bash

while getopts "u:p:" option; do
  case $option in
    u) # Username
        username=$OPTARG;;
    p) # Password
        password=$OPTARG;;
    \?) # Invalid option
      echo "Error: Invalid option"
      exit 1;;
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

# Add user to the system
useradd -m -s /bin/bash $username
# Add user to sudoers group
usermod -aG sudo $username
# Change password for user
echo "$username:$password" | chpasswd


## Change default wsl user -> do in real basic
#printf "\n[user]\ndefault=development" >> /etc/wsl.conf
# Update system
apt update && apt dist-upgrade -y
# Generate ssh key for remote connection
su $username -c "ssh-keygen -q -t ed25519 -C \"$username\" -N '' <<< ~/.ssh/id_ed25519"
## Add generated key to authorized_keys
su $username -c "cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys"
## Install openssh server
apt-get install openssh-server -y
# Enable ssh
systemctl enable ssh
# Configure the ssh server to only allow certificate secured connections
printf "ChallengeResponseAuthentication no\nPasswordAuthentication no\nUsePAM no\nPermitRootLogin no\n" \
  > /etc/ssh/sshd_config.d/disable_root_login.conf
# Restart ssh
/etc/init.d/ssh restart
# Install python
apt-get install python3 python3-pip python3-venv git -y