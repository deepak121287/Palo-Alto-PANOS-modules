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


