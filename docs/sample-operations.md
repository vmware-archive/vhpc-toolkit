## Per-VM Operations

While performing cluster-level operations is the most important use case,
it is also possible to perform a variety of individual operations on a VM
or a set of VMs with the toolkit. This section describes some of those additional commands.

### Clone a VM or a set of VMs
`clone` operation supports cloning a VM or a set of VMs: 

Using linked clone to clone a VM `vhpc_vm_01` based on template 
`vhpc_clone` and customize its CPU and memory configurations: 

```
./vhpc_toolkit clone --template vhpc_clone --datacenter HPC_Datacenter --cluster 
COMPUTE_GPU_Cluster --datastore COMPUTE01_vsanDatastore --memory 8 --cpu 8 
--vm vhpc_vm_01 --linked 
```

### Configure Passthrough for a VM or a set of VMs

The operation supports adding and removing PCI devices for a VM or a set of 
VMs:

As described in [How to enable compute accelerators on vSphere 6.5](https://tinyurl.com/y9qfozcj), 
there are some steps that must be done in order to configure PCI devices that have large memory map regions, 
like commonly seen compute accelerators - NVIDIA Tesla K80, P100 and V100, 
Intel Xeon Phi, and FPGA. The `passthru` 
function takes care of some of those steps,
   like adding `pciPassthru.use64bitMMIO`, `pciPassthru.64bitMMIOSizeGB` 
   vmx entries, so you don't need to manually add them, 
   but you still need to make sure the hardware requirements and 
   guest OS EFI installation are met.
<br />

By default, `pciPassthru.64bitMMIOSizeGB` value is set to 256GB, 
which can handle more than eight large PCIe 
devices, e.g. eight nVidia P100 cards. 
If you have more demand than that, you can use `--mmio_size` to override the 
default. <br />

Add GPU device `0000:84:00.0` to VM `hpc-gpu-vm-01` in Passthrough mode: 

```  
./vhpc_toolkit passthru --add --device 0000:84:00.0 --vm hpc-gpu-vm-01
```

### Configure NVIDIA vGPU (GPU Shared Passthrough)

NVIDIA Virtual GPU enables multiple VMs to share a single 
physical GPU. This operation helps you automate [Add an NVIDIA GRID vGPU 
to a Virtual Machine](https://tinyurl.com/yboullgw). 
It supports add/remove NVIDIA GRID vGPU for a VM or a set of VMs. 

For example, adding a `grid_p100-4q` vGPU profile into VM `hpc-vgpu-vm-01`: 
 
```bash
./vhpc_toolkit vgpu --add --profile grid_p100-4q --vm hpc-vgpu-vm-01
```

### Configure PVRDMA 
VMware vSphere 6.5 and later supports remote direct memory access (RDMA) 
between virtual machines with Paravirtual RDMA (PVRDMA) network adapters. 

The configuration of PVRDMA requires: 

(1) The host on which the virtual machine is running is configured for RoCE 
(RDMA over Ethernet) <br />
(2) The host is connected to a vSphere Distributed Switch. <br />
(3) Assign a PVRDMA Adapter to a Virtual Machine

For more configuration details, please refer to 
[PVRDMA Support](https://tinyurl.com/y8j3car4)

This toolkit can help you create a DVS with uplinks mapped from host RDMA 
NICs and assign a PVRDMA adapter for a VM or a set of VMs.

For example, create a DVS (`pvrdma-dvs`) and connect the hosts (`RoCE-host-01`, 
`RoCE-host-02`) with RDMA 
NICs (`vmnic5`), then create a port group (`pvrdma-pg `) within 
this DVS and assign the port group as PVRDMA adapter type to a VM: 

```
./vhpc_toolkit dvs --create --name pvrdma-dvs --pnic vmnic5 --host RoCE-host-01 
RoCE-host-02 --port_group pvrdma-pg

./vhpc_toolkit pvrdma --add --pvrdma_port_group pvrdma-pg --vm hpc-pvrdma-vm-01
--dvs_name pvrdma-dvs
```

### Configure RDMA SR-IOV  
[Single-root I/O virtualization (SR-IOV)](https://tinyurl.com/y76l898x) 
is a specification that allows a 
single PCIe physical device, such as RDMA device, under a single root port to 
appear to the hypervisor or guest OS as multiple separate physical devices.<br/>
 
The prerequisite is 
[Enable SR-IOV on a Host Physical Adapter](https://tinyurl.com/y95yrkys) <br/>

After SR-IOV is enabled on a Host Physical Adapter, the virtual functions appear
 in the PCI devices list in the VM Settings tab in vSphere: 
 
```
0000:af:00.0 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4] [vmnic4]
0000:af:00.2 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_0]
0000:af:00.3 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_1]
0000:af:00.4 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_2]
0000:af:00.5 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_3]
0000:af:00.6 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_4]
0000:af:00.7 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_5]
0000:af:01.0 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_6]
0000:af:01.1 Network controller: Mellanox Technologies MT27700 Family [ConnectX-4 Virtual Function] [PF_0.175.0_VF_7]
```

This operation helps you automate [Assign a Virtual Function as SR-IOV 
Passthrough Adapter to a Virtual Machine](https://tinyurl.com/y7kevbyv)


For example, create a SVS (`sriov-svs`) and create a Port Group (`sriov-pg `) within the
SVS, then assign the port group as SR-IOV Passthrough adapter type to VM 
`hpc-sriov-vm-01` with specified Physical Function (`0000:af:00.0`) backing 
the Passthrough network adapter: 

```
./vhpc_toolkit svs --create --host RoCE-host-01 --name sriov-svs --pnic vmnic4 
--port_group sriov-pg
 
./vhpc_toolkit sriov --add --vm hpc-sriov-vm-01 --sriov_port_group sriov-pg 
  --pf 0000:af:00.0
```
                    
### Execute post scripts in guest OS for a VM or a set of VMs
This operation supports executing post script(s) in the guest OS for quickly 
preparing an HPC environment. Typical tasks might include installing an MPI 
library, or CUDA toolkit; or mounting 
an NFS file system. VMware Tools must be running in the guest OS to use 
this toolkit operation.


e.g. post execute `install_cuda.sh` script in `hpc-gpu-vm-01` VM: 

```
./vhpc_toolkit post --vm hpc-gpu-vm-01 --guest_username vmware --script ../examples/post-scripts/install_cuda.sh 
```

It will prompt you guest OS password for executing the script. 

### Configure Latency Sensitivity for a VM or a set of VMs
In some cases, enabling the ESXi Latency Sensitivity feature 
can help achieve good performance for HPC workloads 
running on vSphere. Setting Latency Sensitivity to “high" will apply several 
optimizations, including network tunings. These optimizations generally reduce 
overhead related to scheduling and contention, resulting in lower latency and 
jitter. For more latency tuning best 
practices, please refer to
 [Best Practices for Performance Tuning of 
 Latency-Sensitive Workloads in vSphere VMs](https://tinyurl.com/yaojgneh). 
This operation supports configuring Latency Sensitivity for a VM or a set of
 VMs.

e.g. configure latency sensitivity `high` for VMs defined a file (`vms`): 

```
./vhpc_toolkit latency --level high --file vms 
```
where file `vms` has a list of VMs  
```
$ cat vms
hpc-mpi-vm-01
hpc-pvrdma-vm-01
hpc-gpu-vm-01
hpc-vgpu-vm-01
hpc-sriov-vm-01
```
