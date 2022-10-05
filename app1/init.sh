# Update hosts
cat /home/outscale/hosts | sudo tee --append /etc/hosts

# Initialize the volume
## Partitioning the volume
sudo fdisk /dev/sda << EOF
n
p
1
2048
241172479
w
EOF

## format
sudo mkfs.ext4 /dev/sda1

## mount volume to /data
sudo mkdir /data
sudo mount /dev/sda1 /data
echo '/dev/sda1 /data ext4    defaults,nofail        0       2' | sudo tee --append /etc/fstab
sudo chown outscale:outscale /data

# Install Docker (https://docs.docker.com/engine/install/ubuntu/)
sudo apt-get update -y
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y 
sudo apt-get update -y

sudo usermod -aG docker $USER

## Change docker files location
mkdir /data/docker
echo '{"data-root": "/data/docker"}' | sudo tee --append /etc/docker/daemon.json
sudo systemctl daemon-reload
sudo systemctl restart docker


# Install tools
sudo apt-get install unzip -y

# Run containers
# sudo docker compose up -d

# Install Python
sudo apt-get -y install python3
sudo apt-get -y install python3-pip

# Install application
mkdir /data/code
mkdir /data/input
mkdir /data/output
mkdir /data/log


# Run app1 as a service
cat <<EOF > /tmp/app1.service
[Unit]
Description=app1
After=multi-user.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/bin/python3 /home/outscale/app1.py

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/app1.service /etc/systemd/system/app1.service

sudo systemctl daemon-reload
sudo systemctl enable app1.service
sudo systemctl start app1.service

# To stop and restart:
# sudo systemctl stop app1.service
# sudo systemctl restart app1.service

# Run media_load as a service
cat <<EOF > /tmp/media_load.service
[Unit]
Description=media_load
After=multi-user.target

[Service]
Type=simple
Restart=no
ExecStart=/home/outscale/.media_load.sh

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/media_load.service /etc/systemd/system/media_load.service

sudo systemctl enable media_load.service
sudo systemctl start media_load.service

# Install powertop (must be installed on all VMs!)
mkdir /data/logs
mkdir /data/metrics
sudo apt install powertop -y

# Install ifstat (must be installed on all VMs!)
sudo apt install ifstat -y 

