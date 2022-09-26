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

