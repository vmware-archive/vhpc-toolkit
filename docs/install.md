# How to Install
## Prerequisites

OS for using this toolkit: Linux, Mac or Windows <br/>
vSphere >=6.5 <br/>
Python >=3.6 <br/> 

## Install 

Package dependencies will be isolated in a Python virtual environment by 
```virtualenv```. This 
allows us to have different versions of dependencies. 

To install ```virtualenv``` if you don't have one, for example, 

- For Mac and Windows: 
```bash
pip install --upgrade virtualenv
```
- For Ubuntu: 
```bash
sudo apt-get install python3-pip
sudo pip3 install virtualenv
```


Setup this toolkit with an virtual env and install it in "develop" mode (allow actively modify the toolkit):
 
```bash 
git clone https://github.com/vmware/vhpc-toolkit.git
cd vhpc-toolkit
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Secure Setup via Vault 

This toolkit leverages vSphere APIs to manage vSphere objects (such as VMs, 
distributed virtual switches). So it needs connection to vCenter. In order 
to enable the possibility of automation (without prompting password every 
operation), as one option, you could put your vCenter information in 
```vCenter.conf``` under ```vhpc_toolkit/config``` or ```~/vhpc_toolkit```, 
such as 

```text  
# vCenter configuration 
server: 192.168.0.1 
username: mySecretUsername
password: mySecretPassword
```
  
However, it's NOT secure to explicitly store your sensitive information in a 
plain text file. So we enable [Vault](https://learn.hashicorp.com/vault) 
integration. With Vault, the setup procedure is like this: 
  
1. Follow [Vault](https://learn.hashicorp.com/tutorials/vault/getting-started-install?in=vault/getting-started) instructions to install 
Vault and setup a Vault server if you don't have one
  
2. Connect to Vault server by `export VAULT_ADDR=xx` and `export 
VAULT_TOKEN=xx` environment variables 

3. Store your vCenter secrets as key value pairs under a secret path into the
 Vault server, e.g. 

```
vault kv put secret/vCenter vcenter-hostname=192.168.0.1 vcenter-username=mySecretUsername vcenter-password=mySecretPassword
```

4. Finally, you can directly put your keys in ```vCenter.conf``` file as:  
  
```text  
# vCenter configuration 
vault: yes
vault_secret_path: vCenter
server: vcenter-hostname
username: vcenter-username
password: vcenter-password
```

For more advanced features of Vault, such as managing token leases, dynamic 
secrets and Web UI, please refer to  [Vault](https://learn.hashicorp.com/vault). 

## Verification 

After proper installation and setup, you should be able to execute `
./vhpc_toolkit --help` under `vhpc_toolkit/bin` folder to view all available 
operations. <br>
For a quick test, run - 
```bash
# For linux/macOS
./vhpc_toolkit view
# For windows
python ./vhpc_toolkit view
```
!> Have to use **python** before running all commands on Windows systems
