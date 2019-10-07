# Virtualized High Performance Computing Toolkit (vHPC Toolkit) 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
- [Try It Out](#try-it-out)
  - [Prerequisites](#prerequisites)
  - [Install and setup](#install-and-setup)
- [Documentation](#documentation)
  - [Overview](#overview-1)
  - [Command syntax](#command-syntax)
  - [Per-VM operations](#per-vm-operations)
  - [Cluster-level operations](#cluster-level-operations)
    - [Create cluster](#create-cluster)
    - [Destroy cluster](#destroy-cluster)
    - [Cluster configuration file](#cluster-configuration-file)
  - [Prepare the VM template](#prepare-the-vm-template)
  - [Additional functions](#additional-functions)
- [Contributing](#contributing)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

!["vhpclogo"](docs/img/hpc-logo400.png)

## Overview 
This toolkit is intended to help vSphere administrators easily configure and 
manage virtual high performance computing (HPC) clusters by leveraging vSphere APIs.
 
HPC is the use of parallel-processing techniques to solve complex computational problems. 
HPC systems have the ability to deliver sustained performance through the concurrent use of computing resources, 
and they are typically used for solving advanced scientific and engineering problems, 
such as computational fluid dynamics, bioinformatics, 
molecular dynamics, weather modeling and deep learning with neural networks. 
 
Due to extreme demand on performance, HPC commonly leverages hardware accelerators, 
such as __GPGPU__, __FPGA__ and __RDMA__ interconnects, which require special 
vSphere 
configurations. 
This toolkit is intended to facilitate these special configurations. 
It can also help vSphere administrators perform some common vSphere tasks that are related to creating such environments, 
such as VM cloning, setting Latency Sensitivity, and configuring vCPUs, memory, etc.

Feature Highlights:
 
- Configuring PCIe devices in DirectPath I/O mode, such as GPGPU, FPGA and RDMA interconnects
- Configuring NVIDIA vGPU
- Configuring RDMA SR-IOV (Single Root I/O Virtualization)
- Configuring  PVRDMA (Paravirtualized RDMA)
- Easy creation and  deletion of a virtual HPC clusters using cluster configuration files
- Support of common vSphere tasks, such as cloning VMs, configuring vCPUs, memory, reservations, shares, Latency Sensitivity, Distributed Virtual Switch/Standard Virtual Switch, network adapters and network configurations

## Try It Out

### Prerequisites

OS for using this toolkit: Linux or Mac <br/>
vSphere >=6.5 <br/>
Python >=3 <br/> 

### Install and setup

Package dependencies will be isolated in a Python virtual environment by 
```virtualenv```. This 
allows us to have different versions of dependencies. 

To install ```virtualenv``` if you don't have one, for example, 

- For Mac: 
```pip install --upgrade virtualenv```
- For Ubuntu: 
```sudo apt-get install python3-pip```; ```sudo pip3 install virtualenv```


Setup this toolkit with an virtual env:
 
```bash 
git clone xx
cd vhpc_toolkit
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py install
```

Fill in the ```vCenter.conf``` file from ```vhpc_toolkit/config``` with your 
vCenter server name and username. The file should look like: 
    
```bash   
# vCenter configuration 
server: vcenter-fqdn-or-ip   
port: 443
username: administrator@vsphere.local  
```

After properly setting the config file, you should be able to execute 
`./vhpc_toolkit` under `bin` folder to enter interactive shell and perform all 
available operations, e.g.: 

```bash
./vhpc_toolkit
vCenter password: (enter your vCenter passoword)
Welcome to the vHPC Toolkit Shell. Type help or ? to list commands. Type exit to exit the shell.

vhpc_toolkit> help

Documented commands (type help <topic>):
========================================
clone    cpumem   dvs   help     network      passthru  power   sriov  vgpu
cluster  destroy  exit  latency  network_cfg  post      pvrdma  svs    view

``` 
  
## Documentation  

### Overview

The functions of the available vhpc_toolkit major commands are:

```
    clone               Clone VM(s) via Full Clone or Linked Clone
    cluster             Create/Destroy vHPC cluster based on cluster configuration file
    cpumem              Reconfigure CPU/memory for VM(s)
    destroy             Destroy VM(s)
    dvs                 Create/destroy a distributed virtual switch
    exit                Exit the interactive shell 
    help                Show overview help information 
    latency             Configure/Check latency sensitivity
    network             Add/Remove network adapter(s) for VM(s)
    network_config      Configure network(s) for VM(s)
    passthru            Add/Remove (large) PCI device(s) in Passthrough mode
    post                Execute post script(s) in guest OS
    power               Power on/off VM(s)
    pvrdma              Add/Remove PVRDMA (paravirtual RDMA) device(s)
    sriov               Add/remove single root I/O virtualization (SR-IOV)
                        device(s)
    svs                 Create/destroy a standard virtual switch
    vgpu                Add/Remove vGPU device in SharedPassthru mode
    view                View the vCenter object names
```

### Command syntax 

Each command has help information (-h or --help), for example, 
```
vhpc_toolkit> help passthru
usage: vhpc_toolkit passthru [-h] (--vm VM | --file FILE) [--query]
                             [--remove | --add] [--device DEVICE [DEVICE ...]]
                             [--mmio_size MMIO_SIZE]

optional arguments:
  -h, --help            show this help message and exit
  --vm VM               Name of the VM on which to perform the passthrough operation
  --file FILE           Name of the file containing a list of VMs, one per line, to perform the passthrough operation
  --query               Print available passthrough device(s) information for the VM(s)
  --remove              Remove device(s)
  --add                 Add device(s)
  --device DEVICE [DEVICE ...]
                        Device ID of the PCI device(s), for example: 0000:05:00.0
  --mmio_size MMIO_SIZE
                        64-bit MMIO size in GB for PCI device with large BARs. Default: 256
```

The following conventions are used when describing command syntax:

```bash 
vhpc_toolkit> {command} (--cmd1 cmd1_arg | --cmd2 cmd2_arg) [--cmd3 cmd3_arg [cmd3_arg ...]]
```

* ```{}``` means this is a major command and will be followed by a list of 
sub-commands.  

* ```()``` means this is a mandatory subcommand.  

* ```[]``` means this is an optional subcommand. 

* ```{command}``` could be any command listed in the overview help above.

* ```(--cmd1 cmd1_arg | --cmd2 cmd2_arg)``` means one of these two 
must be specified. 

* ```[--cmd3 cmd3_arg [cmd3_arg ...]]``` means this is an optional command and 
you can optionally append multiple arguments to this command. 


### Per-VM operations

Please see [operation examples](docs/sample-operations.md) for what you can do 
with each operation. 

### Cluster-level operations

The most common usage of this tool is to help administrators create and 
manage virtual HPC clusters on vSphere. This section provides details for the
 cluster-level operations. Available cluster sub-commands are:
 
```bash 
vhpc_toolkit> cluster -h
usage: vhpc_toolkit cluster [-h] (--create | --destroy) --file FILE

optional arguments:
  -h, --help   show this help message and exit
  --create     Create a cluster
  --destroy    Destroy a cluster
  --file FILE  Name of the cluster configuration file
```

#### Create cluster 
```bash 
vhpc_toolkit> cluster --create --file cluster.conf
```
This will connect to the vCenter server and create a cluster using the 
cluster definition given in the cluster 
configuration file, whose format is described in the 
[Cluster configuration file](####Cluster-configuration-file) 
section. Once the cluster has been created successfully, IP addresses of VMs 
will be displayed (if power on is successful and VM guest agent is working 
properly after powering on)

#### Destroy cluster
```bash 
vhpc_toolkit> cluster --destroy --file cluster.conf
```

This will destroy the cluster defined in the cluster.conf file, 
if the cluster exists. Before destroying, 
you will be prompted to confirm the destroy operation. 

#### Cluster configuration file

The cluster configuration file is the key to defining your HPC virtual cluster. 
It's composed of multiple sections, 
each of which consists a set of properties, that are represented 
as key-value pairs. You can define section 
names arbitrarily, but the key names are not arbitrary. For a list of valid 
key names, please see [available keys](docs/availble-keys.md).

See the [examples/cluster-scripts](examples/cluster-scripts) directory for 
different examples.

In the following example, a section called BASE has been defined
 (section names should be bracketed). In this section, we can define clone
 properties as:

```bash
[BASE]
template: vhpc_clone
cpu: 4
memory: 16
datacenter: HPC Datacenter
cluster: COMPUTE GPU Cluster
host: vhpc-esx-01.hpc.vmware.com
vm_folder:
resource_pool:
datastore: COMPUTE01_vsanDatastore
linked: no
```

We define another section called NETWORK, which contains some
networking properties:

```bash
[NETWORK]
is_dhcp: true
port_group: vHPC-PG-VMNetwork
domain: hpc.vmware.com
netmask: 255.255.255.0
gateway: 172.1.101.1
dns: ['172.1.110.1', '172.1.110.2']
```

We can also define another section to assign NVIDIA V100 vGPU with
`grid_p100-2q` profile, where the profile represents vGPU type and “2q”
refers to the vGPU's memory size.

```bash
[P100-VGPU]
vgpu: grid_p100-2q
```

The VM definition section should have the section name ```_VMS_```.
Each line defines a VM name and some
property definitions. You can define VM name arbitrarily,
but the VM's definition must be a combination of previously-defined section
names and explicit key-value pairs ([available keys](docs/availble-keys.md)). 
Each section name will be replaced inline with the set of key-value pairs
listed in section’s definition.
Once the VM definition has been resolved to a list of key-value pairs, the
pairs are processed from left to right with the rightmost occurrence of
a key taking precedence over any earlier occurrence.
Multiple VM property definitions are delimited by whitespace, e.g.:

```bash
[_VMS_]
new_vm1:  BASE NETWORK P100-VGPU
new_vm2:  BASE NETWORK P100-VGPU
new_vm3:  BASE NETWORK
```

In the above example, it defines three VMs: `new_vm1`, `new_vm2` and `new_vm3`.
All VMs will inherit the properties defined in the `BASE`, `NETWORK` sections.
VMs `new_vm1`, `new_vm2` will inherit properties defined in the `P100-VGPU`
section, additionally.

To inherit most of the properties in a section for a VM but override
one or two particular properties,
you can append the properties after the section inheritance:

```bash
new_vm1:  BASE NETWORK P100-VGPU
new_vm2:  BASE NETWORK P100-VGPU
new_vm3:  BASE NETWORK host: vhpc-esx-02.hpc.vmware.com
```

In the VM section, certain key values can be defined in ranges, e.g.:

```bash
new_vm{4:7}: BASE NETWORK host: vhpc-esx-0{2:3}.hpc.vmware.com
```

The above example defines four VMs on two hosts.
The rules for this range definition are:

1. The size of the range of the left-hand side (the number of VMs) must
be greater than or equal to each of the ranges of the righ-thand side.

2. Currently, only the host, datastore, ip, and guest_hostname key values
along with the VM name can include range specifiers.

3. Ranges on the property side that are smaller than the VM name
range will be padded to the proper length using one of two strategies:
round-robin or consecutive.

In the round-robin case, the ranges will be expanded as shown below.
Note that the host range 2-3 has been expanded by repeating the
range to match the number of VMs: 2,3,2,3.

| VM  | host   |
| :------:|:-----:|
| new_vm4      | **vhpc-esx-02.hpc.vmware.com** |
| new_vm5      | **vhpc-esx-03.hpc.vmware.com** |
| new_vm6      | **vhpc-esx-02.hpc.vmware.com** |
| new_vm7      | **vhpc-esx-03.hpc.vmware.com** |

The expansion in the consecutive case is shown below.
Note that the host range 2-3 has been expanded by
repeating each element consecutively: 2, 2, 3, 3.

| VM  | host   |
| :------:|:-----:|
| new_vm4      | **vhpc-esx-02.hpc.vmware.com** |
| new_vm5      | **vhpc-esx-02.hpc.vmware.com** |
| new_vm6      | **vhpc-esx-03.hpc.vmware.com** |
| new_vm7      | **vhpc-esx-03.hpc.vmware.com** |

The syntax for defining round-robin ranges is `{x:y}` and
the syntax for defining consecutive ranges is `{{x:y}}`,
where x is the beginning of the range and y is the end of the range.

When you perform a cluster-level operation that includes ranges,
the ranges will be expanded and you will be prompted to confirm the action.

Additionally, you can also define operations to create/destroy Standard Virtual
Switch (SVS) and Distributed Virtual Switch (DVS) in the cluster
configuration file. The section should have the section name `_SVS_`
or `_DVS_`, e.g.:

Create a DVS named `pvrdma-dvs` with pnic `vmnic5` from the hosts
defined in the following `HOST-LIST` section and also
create a port group `pvrdma-pg` within this DVS:

```
[HOST-LIST]
host: vhpc-esx-0{{5:8}}.hpc.vmware.com
```

```
[_DVS_]
pvrdma-dvs: pnic: vmnic5 HOST-LIST port_group: pvrdma-pg
```

Or create a SVS named `sriov-svs` with pnic `vmnic4` on each host in
`HOST-LIST` and also create a port group `sriov-pg` within each SVS:

```
[_SVS_]
sriov-svs: pnic: vmnic4 HOST-LIST port_group: sriov-pg
```

### Prepare the VM template 

For cloning operation and cluster creation operation, a VM template is 
required. Use the standard procedure for creating vSphere templates, 
include installing Guest Agents, modifying network scripts to remove hardware 
rules and UUID. A good example: [Creating a CentOS 7.2 VMware Gold 
Template](https://tinyurl.com/y9nhlv2k)

If you intend to configure large-BAR PCIe devices (such as NVIDIA 
P100, V100 GPU accelerators) or to execute  post scripts, there are two 
additional requirements:
 
1. To use VM Direct Path I/O (Passthrough), your VM must be configured to 
boot with EFI and your guest OS must have been created with an EFI 
installation of that operating system. 
More details: [VMware KB article 2142307](https://tinyurl.com/ycpgxj2h)
 
2. Linux guests are the only supported guest operating systems 
for executing post scripts. 

### Additional functions 
Please share your ideas

## Contributing

The vhpc-toolkit project team welcomes contributions from the community. Before you start working with vhpc-toolkit, please
read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be
signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on
as an open-source patch. For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This toolkit is available under the [Apache 2 license](LICENSE.txt).






