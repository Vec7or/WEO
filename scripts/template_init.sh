#!/bin/bash
# Add user to the system
useradd -m -s /bin/bash development
# Add user to sudoers group
usermod -aG sudo development
# Change password for user
echo "development:development" | chpasswd
# Change default wsl user
echo "\n[user]\ndefault=development" >> /etc/wsl.conf
# Update system
sudo apt update && sudo apt dist-upgrade -y
echo "############### 1 ##############"
# Generate ssh key for remote connection
sudo -u development -c "ssh-keygen -q -t ed25519 -C \"development\" -N '' <<< ~/.ssh/id_ed25519"
## Add generated key to authorized_keys
sudo -u development -c "cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys"
## Install openssh server
apt-get install openssh-server -y
# Enable ssh
systemctl enable ssh
# Configure the ssh server to only allow certificate secured connections
echo "ChallengeResponseAuthentication no\nPasswordAuthentication no\nUsePAM no\nPermitRootLogin no\n" \
  >> /etc/ssh/sshd_config.d/disable_root_login.conf
# Install python
apt-get install python3 -y