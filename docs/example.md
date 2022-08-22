# Example Use Cases
## Create cluster 
```bash 
./vhpc_toolkit cluster --create --file cluster.conf
```
This will connect to the vCenter server and create a cluster using the 
cluster definition given in the cluster 
configuration file, whose format is described in the 
[Cluster configuration file](####Cluster-configuration-file) 
section. Once the cluster has been created successfully, IP addresses of VMs 
will be displayed (if power on is successful and VM guest agent is working 
properly after powering on)

## Destroy cluster
```bash 
./vhpc_toolkit cluster --destroy --file cluster.conf
```

This will destroy the cluster defined in the cluster.conf file, 
if the cluster exists. Before destroying, 
you will be prompted to confirm the destroy operation. 

## Cluster configuration file

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

## Prepare the VM template 

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

