# Virtualized High Performance Computing Toolkit (vHPC Toolkit) 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
- [Try It Out](#try-it-out)
  - [Prerequisites](#prerequisites)
  - [Install](#install)
  - [Secure Setup via Vault](#secure-setup-via-vault)
  - [Verification](#verification)
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


!["vhpclogo"](/img/hpc-logo400.png)

## Overview 

High Performance Computing (HPC) is the use of parallel-processing techniques
 to solve complex computational problems. HPC systems have the ability to deliver sustained 
performance through the concurrent use of distributed computing resources, 
and they are typically used for solving advanced scientific and engineering problems, 
such as computational fluid dynamics, bioinformatics, 
molecular dynamics, weather modeling and deep learning with neural networks. 
 
Due to their extreme demand on performance, HPC workloads often have much 
more intensive resource requirements than those workloads found in the 
typical enterprise. For example, HPC commonly leverages hardware 
accelerators, such as GPU and FPGA for compute as well as RDMA 
interconnects, which require special vSphere configurations. 

This toolkit is intended to facilitate managing the lifecycle of these 
special configurations by leveraging vSphere APIs. It also includes features 
that help vSphere administrators perform some common vSphere tasks that are 
related to creating such high-performing environments, such as VM cloning, 
setting Latency Sensitivity, and sizing vCPUs, memory, etc.

Feature Highlights:
 
- Configure PCIe devices in DirectPath I/O mode, such as GPGPU, FPGA and RDMA
 interconnects
- Configure NVIDIA vGPU
- Configure RDMA SR-IOV (Single Root I/O Virtualization)
- Configure  PVRDMA (Paravirtualized RDMA)
- Easy creation and  destruction of virtual HPC clusters using cluster 
configuration files
- Perform common vSphere tasks, such as cloning VMs, configuring vCPUs, memory, 
reservations, shares, Latency Sensitivity, Distributed Virtual 
Switch/Standard Virtual Switch, network adapters and network configurations


## Try It Out



## Documentation  

### Overview

The functions of the available vhpc_toolkit major commands are:

```
    view                View the vCenter object names
    clone               Clone VM(s) via Full Clone or Linked Clone
    destroy             Destroy VM(s)
    power               Power on/off VM(s)
    cpumem              Reconfigure CPU/memory for VM(s)
    network             Add/Remove network adapter(s) for VM(s)
    network_cfg         Configure network(s) for VM(s)
    post                Execute post script(s) in guest OS
    passthru            Add/Remove (large) PCI device(s) in Passthrough mode
    sriov               Add/remove single root I/O virtualization (SR-IOV)
                        device(s)
    pvrdma              Add/Remove PVRDMA (Paravirtual RDMA) device(s)
    vgpu                Add/Remove vGPU device in SharedPassthru mode
    svs                 Create/destroy a standard virtual switch
    dvs                 Create/destroy a distributed virtual switch
    latency             Configure/Check latency sensitivity
    cluster             Create/Destroy vHPC cluster based on cluster
                        configuration file
```

### Command syntax 

Each command has help information (-h or --help), for example, 
```
./vhpc_toolkit passthru --help
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
                        64-bit MMIO size in GB for PCI device with large BARs. Default: 256.
```

The following conventions are used when describing command syntax:

```bash 
./vhpc_toolkit {command} (--cmd1 cmd1_arg | --cmd2 cmd2_arg) [--cmd3 cmd3_arg [cmd3_arg ...]]
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
./vhpc_toolkit cluster --help
usage: vhpc_toolkit cluster [-h] (--create | --destroy) --file FILE

optional arguments:
  -h, --help   show this help message and exit
  --create     Create a cluster
  --destroy    Destroy a cluster
  --file FILE  Name of the cluster configuration file
```
