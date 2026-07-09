#!/usr/bin/env bash

set -e

echo "Updating packages..."
sudo apt update
sudo apt upgrade -y

echo "Installing required packages..."
sudo apt install -y \
  ca-certificates \
  curl \
  gnupg \
  git \
  ufw

echo "Installing Docker..."
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update

sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

echo "Adding current user to docker group..."
sudo usermod -aG docker "$USER"

echo "Docker installed."
echo "IMPORTANT: log out and SSH back in, then run: docker --version"
