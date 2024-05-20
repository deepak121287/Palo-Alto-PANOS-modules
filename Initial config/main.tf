provider "panos" {
  hostname   = var.firewall_ip
  ssh_key    = file(var.ssh_private_key)
  ssh_user   = var.ssh_username
  insecure   = true
}

resource "panos_administrator" "admin" {
  name     = var.ssh_username
  password = var.new_password
}
resource "panos_op" "interface_swap" {
  content = "set deviceconfig system swap-management-interface from management to ethernet1/1"
}

resource "panos_commit" "config" {
  depends_on = [panos_op.interface_swap]
}


