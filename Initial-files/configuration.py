import paramiko
import boto3
import time
import base64
import json
import os
import tempfile
import platform

def get_secret(secret_name, region_name):
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name= region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        return secret
    except client.exceptions.ResourceNotFoundException:
        print(f"Error: The requested secret {secret_name} was not found")
    except client.exceptions.InvalidRequestException:
        print(f"Error: The request was invalid due to: {e}")
    except client.exceptions.InvalidParameterException:
        print(f"Error: The request had invalid params: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

def format_key(private_key_str):

    private_key_str = private_key_str.strip()
    
    if not private_key_str.startswith("-----BEGIN RSA PRIVATE KEY-----"):
        private_key_str = "-----BEGIN RSA PRIVATE KEY-----\n" + private_key_str
    if not private_key_str.endswith("-----END RSA PRIVATE KEY-----"):
        private_key_str = private_key_str + "\n-----END RSA PRIVATE KEY-----"
    
    private_key_lines = private_key_str.splitlines()
    private_key_str = "\n".join(line.strip() for line in private_key_lines if line.strip())
    
    return private_key_str


def change_firewall_password(hostname,username,private_key_str,new_password):

    ssh_client = None
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    private_key_str = format_key(private_key_str)
    #print("Formatted Private Key:\n", private_key_str)

    with tempfile.NamedTemporaryFile(delete=False,mode='w') as temp_key_file:
        temp_key_file.write(private_key_str)
        temp_key_file_path = temp_key_file.name
        
    if platform.system() != 'Windows':
        os.chmod(temp_key_file_path, 0o400)

    # print(f"Temporary key file path: {temp_key_file_path}")
    # with open(temp_key_file_path, 'r') as f:
    #     print("Content of temp key file:")
    #     print(f.read())
    
    try:
        private_key = paramiko.RSAKey.from_private_key_file(temp_key_file_path)
    except paramiko.SSHException as e:
        print(f"Failed to load private key: {e}")
        os.remove(temp_key_file_path)
        return        
        
    try:
        
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
            os.remove(temp_key_file_path)
            print("SSH connection closed.")

def main():
    
    secret_name = "ec2key"
    region_name = "us-east-1"
    hostname = input("Enter the hostname/IP: ")
    username = input("Enter the Palo Alto firewall username: ")
    new_password = input("Enter the new password: ") 

    secret_str = get_secret(secret_name, region_name)
    if secret_str is None:
        print("Could not fetch the private key from Secrets Manager")
        return
    
    try:
        secret_dict = json.loads(secret_str, strict=False)
        private_key_str = secret_dict.get('ssh-key')
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    if private_key_str is None:
        print("No ssh-key found in the secret")
        return
    
    change_firewall_password(hostname,username,private_key_str,new_password)

if __name__ == "__main__":
    main()