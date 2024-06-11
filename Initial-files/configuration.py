import paramiko
import boto3
import time
import base64
import json

def get_secret(secret_name, region_name):
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name= region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"Error fetching secret {secret_name}: {e}")
        return None
    
    secret = get_secret_value_response['SecretString']
    return secret

def change_firewall_password(hostname,username,private_key,new_password):

    ssh_client = None
    
    try:
        
        # with open(private_key_path, 'r') as key_file:
        #     key_contents = key_file.read()
        #     if not key_contents.startswith('-----BEGIN RSA PRIVATE KEY-----'):
        #         raise ValueError("The private key file does not start with '-----BEGIN RSA PRIVATE KEY-----'")
        #     print("Private key file is valid.")

        
        # private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(hostname=hostname, username=username, pkey=private_key)
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

def main():
    
    secret_name = "ec2secret"
    region_name = "us-east-1"
    hostname = input("Enter the hostname/IP: ")
    username = input("Enter the Palo Alto firewall username: ")
    new_password = input("Enter the new password: ") 

    private_key_str = get_secret(secret_name, region_name)
    if private_key_str is None:
        print("Could not fetch the private key from Secrets Manager")
        return

    private_key = paramiko.RSAKey.from_private_key(private_key_str)
    
    change_firewall_password(hostname,username,private_key,new_password)

if __name__ == "__main__":
    main()