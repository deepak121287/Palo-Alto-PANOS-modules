import paramiko
import time

def change_firewall_password():
    
    host = '52.73.195.112'
    username = 'admin'
    private_key_path = 'C:/Users/deepa/Downloads/keys/PA-keypair.pem'
    new_password = 'Admin@123!'

    ssh_client = None
    
    try:
        
        with open(private_key_path, 'r') as key_file:
            key_contents = key_file.read()
            if not key_contents.startswith('-----BEGIN RSA PRIVATE KEY-----'):
                raise ValueError("The private key file does not start with '-----BEGIN RSA PRIVATE KEY-----'")
            print("Private key file is valid.")

        
        private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(hostname=host, username=username, pkey=private_key)
        print("SSH connection established.")

        def send_command(command, wait_time=5):
            ssh_shell.send(command + '\n')
            time.sleep(wait_time)
            output = ssh_shell.recv(1000).decode()
            print(output)
            return output
        
        ssh_shell = ssh_client.invoke_shell()
        time.sleep(1)  

        ssh_shell.send("set system setting mgmt-interface-swap enable yes\n")
        time.sleep(5)
        ssh_shell.send("y\n")
        time.sleep(5) 
        
        ssh_shell.send("configure\n")
        time.sleep(2)  
        
        ssh_shell.send("set mgt-config users admin password\n")
        time.sleep(10)  

        
        ssh_shell.send(new_password + '\n')
        time.sleep(5)  
        ssh_shell.send(new_password + '\n')
        time.sleep(5)  

        ssh_shell.send("commit\n")
        time.sleep(10)

        while True:
            output = ssh_shell.recv(1000).decode()
            print(output)
            if "Commit complete" in output or "Configuration committed successfully" in output:
                print("Commit operation completed.")
                break
            time.sleep(5)
        
        output = ssh_shell.recv(10000).decode()
        print(output)

    except FileNotFoundError as e:
        print(f"Private key file not found: {private_key_path}")
        print(f"Error: {e}")
    except paramiko.SSHException as e:
        print("SSH connection failed")
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Invalid private key file: {e}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if ssh_client and ssh_client.get_transport() and ssh_client.get_transport().is_active():
            ssh_client.close()
            print("SSH connection closed.")

if __name__ == "__main__":
    change_firewall_password()
