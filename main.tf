terraform {
  required_providers {
    outscale = {
      source = "outscale-dev/outscale"
      version = "0.5.4"
    }
  }
  required_version = ">= 1.2.0"
}

provider "outscale" {}

resource "outscale_keypair" "keypair01" {
    keypair_name = "hackathon"
}

# SG common for all VMs
resource "outscale_security_group" "hackathon_common" {
    security_group_name = "hackathon-common"
}

resource "outscale_security_group_rule" "hackathon_ssh" {
  flow              = "Inbound"
  security_group_id = outscale_security_group.hackathon_common.id
  rules {
    from_port_range = "22"
    to_port_range   = "22"
    ip_protocol     = "tcp"
    ip_ranges       = ["0.0.0.0/0"]
  }
}

resource "outscale_security_group_rule" "hackathon_vscode" {
  flow              = "Inbound"
  security_group_id = outscale_security_group.hackathon_common.id
  rules {
    from_port_range = "3000"
    to_port_range   = "3000"
    ip_protocol     = "tcp"
    ip_ranges       = ["0.0.0.0/0"]
  }
}

# SG Postgres
resource "outscale_security_group" "hackathon_postgre" {
    security_group_name = "hackathon-postgres"
}

# SG Postgres rule
resource "outscale_security_group_rule" "hackathon_postgre" {
  flow              = "Inbound"
  security_group_id = outscale_security_group.hackathon_postgre.id
  rules {
    from_port_range = "5432"
    to_port_range   = "5432"
    ip_protocol     = "tcp"
    ip_ranges       = ["0.0.0.0/0"]
  }
}

# SG Postgres rule
resource "outscale_security_group_rule" "hackathon_adminer" {
  flow              = "Inbound"
  security_group_id = outscale_security_group.hackathon_postgre.id
  rules {
    from_port_range = "8080"
    to_port_range   = "8080"
    ip_protocol     = "tcp"
    ip_ranges       = ["0.0.0.0/0"]
  }
}

########### VM with Database 1 ###########

resource "outscale_vm" "hackathon_db1" {
  image_id      = "ami-bb490c7e"
  vm_type       = "tinav5.c8r16p1"
  keypair_name  = "${outscale_keypair.keypair01.keypair_name}"
  security_group_ids = [outscale_security_group.hackathon_common.security_group_id, outscale_security_group.hackathon_postgre.security_group_id]
  tags {
    key   = "name"
    value = "hackathon_db1"
  }
  block_device_mappings {
    device_name = "/dev/sdb"
    bsu {
        volume_size           = 115
        volume_type           = "io1"
        iops                  = 150
        delete_on_vm_deletion = true
    }
  }

  # Create SSH connection script
  provisioner "local-exec" {
    command = "echo 'ssh -o StrictHostKeyChecking=no -i ~/.ssh/hackathon.rsa outscale@${outscale_vm.hackathon_db1.public_ip}' > db1_connect.sh"
  }

  # Save IP to local script file 
  provisioner "local-exec" {
    command = "echo '${outscale_vm.hackathon_db1.public_ip} db1' >> hosts"
  }

  # Change script attributes 
  provisioner "local-exec" {
    command = "chmod +x db1_connect.sh"
  }

  # Copy init script to VM
  provisioner "file" {
    source      = "db1/init.sh"
    destination = "/home/outscale/init.sh"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }
  
  # Copy docker-compose.yml to vm
  provisioner "file" {
    source      = "db1/docker-compose.yml"
    destination = "/home/outscale/docker-compose.yml"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Copy DB init script to VM
  provisioner "file" {
    source      = "db1/db_init.sql"
    destination = "/home/outscale/db_init.sql"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Run init script in VM
  provisioner "remote-exec" {  
    inline = [
      "chmod +x /home/outscale/init.sh",
      "/home/outscale/init.sh",
    ]
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Clean on destroy
  provisioner "local-exec" {
    when    = destroy
    command = "rm -f db1_connect.sh"
  }
}

########### VM with Microservice1 ###########

resource "outscale_vm" "hackathon_ms1" {
  image_id      = "ami-bb490c7e"
  vm_type       = "tinav5.c8r16p1"
  keypair_name  = "${outscale_keypair.keypair01.keypair_name}"
  security_group_ids = [outscale_security_group.hackathon_common.security_group_id]
  tags {
    key   = "name"
    value = "hackathon_ms1"
  }
  block_device_mappings {
    device_name = "/dev/sdb"
    bsu {
        volume_size           = 115
        volume_type           = "io1"
        iops                  = 150
        delete_on_vm_deletion = true
    }
  }

  # Create SSH connection script
  provisioner "local-exec" {
    command = "echo 'ssh -o StrictHostKeyChecking=no -i ~/.ssh/hackathon.rsa outscale@${outscale_vm.hackathon_ms1.public_ip}' > ms1_connect.sh"
  }

  # Save IP to file
  provisioner "local-exec" {
    command = "echo '${outscale_vm.hackathon_ms1.public_ip} ms1' >> hosts"
  }  

  # Change script attributes 
  provisioner "local-exec" {
    command = "chmod +x ms1_connect.sh"
  }

  # Pack VSCode
  provisioner "local-exec" {
    command = "zip ms1/vscode.zip ms1/vscode/*"
  }

  # Copy VSCode file to VM
  provisioner "file" {
    source      = "ms1/vscode.zip"
    destination = "/home/outscale/vscode.zip"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }
  
  # Copy init script to VM
  provisioner "file" {
    source      = "ms1/init.sh"
    destination = "/home/outscale/init.sh"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Copy hosts to VM
  provisioner "file" {
    source      = "hosts"
    destination = "/home/outscale/hosts"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Run init script in VM
  provisioner "remote-exec" {  
    inline = [
      "chmod +x /home/outscale/init.sh",
      "/home/outscale/init.sh",
    ]
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }
  
  # Clean on destroy
  provisioner "local-exec" {
    when    = destroy
    command = "rm -f ms1_connect.sh"
  }
}

########### VM with App1 ###########

resource "outscale_vm" "hackathon_app1" {
  image_id      = "ami-bb490c7e"
  vm_type       = "tinav5.c8r16p1"
  keypair_name  = "${outscale_keypair.keypair01.keypair_name}"
  security_group_ids = [outscale_security_group.hackathon_common.security_group_id]
  tags {
    key   = "name"
    value = "hackathon_app1"
  }
  block_device_mappings {
    device_name = "/dev/sdb"
    bsu {
        volume_size           = 115
        volume_type           = "io1"
        iops                  = 150
        delete_on_vm_deletion = true
    }
  }

  # Extract  ssh key to local file in ~/.ssh
  provisioner "local-exec" {
    command = <<EOT
cat <<EOF > ~/.ssh/hackathon.rsa
${outscale_keypair.keypair01.private_key}
EOF
EOT
  }

  # Change ssh key file attributes 
  provisioner "local-exec" {
    command = "chmod 600 ~/.ssh/hackathon.rsa"
  }

  # Create SSH connection script
  provisioner "local-exec" {
    command = "echo 'ssh -o StrictHostKeyChecking=no -i ~/.ssh/hackathon.rsa outscale@${outscale_vm.hackathon_app1.public_ip}' > app1_connect.sh"
  }

  # Save IP to file
  provisioner "local-exec" {
    command = "echo '${outscale_vm.hackathon_app1.public_ip} app1' >> hosts"
  }

  # Change script attributes 
  provisioner "local-exec" {
    command = "chmod +x app1_connect.sh"
  }

  # Pack VSCode
  provisioner "local-exec" {
    command = "zip app1/vscode.zip app1/vscode/*"
  }

  # Copy VSCode file to VM
  provisioner "file" {
    source      = "app1/vscode.zip"
    destination = "/home/outscale/vscode.zip"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Copy init script to VM
  provisioner "file" {
    source      = "app1/init.sh"
    destination = "/home/outscale/init.sh"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Copy hosts to VM
  provisioner "file" {
    source      = "hosts"
    destination = "/home/outscale/hosts"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Copy app1.py to VM
  provisioner "file" {
    source      = "app1/src/app1.py"
    destination = "/home/outscale/app1.py"
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }

  # Run init script in VM
  provisioner "remote-exec" {  
    inline = [
      "chmod +x /home/outscale/init.sh",
      "/home/outscale/init.sh",
    ]
    connection {
      type = "ssh"
      user = "outscale"
      private_key = "${outscale_keypair.keypair01.private_key}"
      host = self.public_ip
    }
  }


  
  # Clean on destroy
  provisioner "local-exec" {
    when    = destroy
    command = "rm -f ~/.ssh/hackathon.rsa"
  }
  provisioner "local-exec" {
    when    = destroy
    command = "rm -f app1_connect.sh"
  }
}


