# Commands not associated with host or VM

## view
Use this command to view all vCenter object names
```bash
./vhpc_toolkit view [-h] [--networking]
```

| **Argument** 	| **What does it do?**                                                                     	| Group 	| Type 	| Required 	|
|--------------	|------------------------------------------------------------------------------------------	|-------	|------	|----------	|
| networking   	| Show all the network objects (virtual switch and network adapters) along with basic view 	|       	| None 	| False    	|

## svs
Create/Destroy Standard Virtual Switch
```bash
./vhpc_toolkit svs [-h] (--create | --destroy) --host HOST [HOST ...] --name NAME [--pnic PNIC] [--port_group PORT_GROUP] [--mtu MTU]
```
| **Argument** 	| **What does it do?**                                                                 	| Group 	| Type    	| Required    	|
|--------------	|--------------------------------------------------------------------------------------	|-------	|---------	|-------------	|
| create       	| Create a standard virtual switch                                                     	| 1     	| None    	| True(Group) 	|
| destroy      	| Destroy the standard virtual switch                                                  	| 1     	| None    	| True(Group) 	|
| host         	| Name of the ESXi host on which to create standard virtual switch                     	|       	| string  	| True        	|
| name         	| Name of the standard virtual switch to be created or destroyed                       	|       	| string  	| True        	|
| pnic         	| Physical NIC to be added into its standard virtual switch like `vmnic0`              	|       	| string  	| False       	|
| port_group   	| Name of virtual port group to be created within this standard virtual switch         	|       	| string  	| False       	|
| mtu          	| Maximum Transmission Unit. Might fail if it is not valid value for the given network 	|       	| integer 	| False       	|

To destroy the switch, can use only the required arguments

## dvs
Create/Destroy Distributed Virtual Switch
```bash
./vhpc_toolkit dvs [-h] (--create | --destroy) --name NAME [--datacenter DATACENTER] [--host HOST [HOST ...]] [--pnic PNIC [PNIC ...]] [--port_group PORT_GROUP] [--mtu MTU]
```

| **Argument** 	| **What does it do?**                                                                                                    	| Group 	| Type         	| Required    	|
|--------------	|-------------------------------------------------------------------------------------------------------------------------	|-------	|--------------	|-------------	|
| create       	| Create a distributed virtual switch                                                                                     	| 1     	| None         	| True(Group) 	|
| destroy      	| Destroy the distributed virtual switch                                                                                  	| 1     	| None         	| True(Group) 	|
| host         	| Name of the ESXi hosts on which to create distributed virtual switch                                                    	|       	| list[string] 	| True        	|
| name         	| Name of the distributed virtual switch to be created or destroyed                                                       	|       	| string       	| True        	|
| pnic         	| Physical NIC(s) on each host to be added into this distributed virtual switch, e.g. `vmnic0 vmnic1`                     	|       	| list[string] 	| False       	|
| port_group   	| Name of virtual port group to be created within this standard virtual switch                                            	|       	| string       	| False       	|
| datacenter   	| Name of the datacenter to create the distributed virtual switch. Note that all hosts need to be in the same datacenter. 	|       	| string       	| False       	|
| mtu          	| Maximum Transmission Unit. Might fail if it is not valid value for the given network                                    	|       	| integer      	| False       	|

## cluster

The cluster configuration file is the key to defining an HPC virtual cluster. 
It's composed of multiple sections, each of which consists of a set of properties that are represented as key-value pairs. The toolkit
adopts the YAML format (without nested structure) to parse the cluster definition because of its human readability. The cluster definition file
can be divided into three sections: property section, VM section and networking section. 

### Property Section
In the following example, a section called **BASE** has been defined (for
any property section, section name can be arbitrary and section names
should be bracketed). In this section, we can, for example, define clone
properties as:
```
[BASE]
template: vhpc_clone
datacenter: HPC_Datacenter
cluster: COMPUTE_GPU_Cluster
host: vhpc-esx-01.hpc.vmware.com
datastore: COMPUTE_vsanDatastore
linked: no
instant: no
cpu: 4
memory: 16
```
We define another section called **NETWORK**, which contains some
networking properties:

```
[NETWORK]
is_dhcp: true
port_group: vHPC-PG-VMNetwork
domain: hpc.vmware.com
netmask: 255.255.255.0
gateway: 172.1.101.1
dns: ['172.1.110.1', '172.1.110.2']
```

We can also define another section to assign `NVIDIA P100 vGPU` with
`grid_p100-2q` profile, where the profile represents the vGPU type
and `2q` refers to the vGPU's memory size, 2GB.

```
[P100-VGPU]
vgpu: grid_p100-2q
```

### VM Section
The VM definition section should have the section name
`_VMS_`. Each line contains a VM name and some property
definitions. You can set the VM name arbitrarily, but the VM's
definition must be a combination of previously-defined section names
and explicit key-value pairs. Each section name will be replaced inline
with the set of key-value pairs listed in that section’s definition.
Multiple VM property definitions are delimited by whitespace, e.g.:

```
[_VMS_]
new_vm1: BASE NETWORK P100-VGPU
new_vm2: BASE NETWORK P100-VGPU
new_vm3: BASE NETWORK
```

The above example defines three VMs: `new_vm1`, `new_vm2` and
`new_vm3`. All VMs will inherit the properties defined in the
`BASE`, `NETWORK` sections. VMs `new_vm1`, `new_vm2` will
inherit properties defined in the `P100-VGPU` section as well.
To inherit most of the properties in a section for a VM but override one
or two particular properties, you can append the properties after the
section inheritance. For example,

```
[_VMS_]
new_vm1: BASE NETWORK P100-VGPU
new_vm2: BASE NETWORK P100-VGPU
new_vm3: BASE NETWORK host: vhpc-esx-02.hpc.vmware.com
```

In the VM section, certain key values can be defined in ranges, e.g.:
```
new_vm{4:7}: BASE NETWORK host: vhpc-esx-0{2:3}.hpc.vmware.com
```
The above example defines four VMs on two hosts. The rules for this
range definition are:
• The size of the range of the left-hand side (the number of VMs)
must be greater than or equal to each of the ranges of the righthand
side.
• Currently, only the host, datastore, ip, and guest_hostname key
values along with the VM name can include range specifiers.
• Ranges on the property side that are smaller than the VM name
range will be padded to the proper length using one of two
strategies: round-robin or consecutive.
In the round-robin case, the ranges will be expanded as shown in the table below.<br>

| **VM**  	| **Host**                   	|
|----------	|---------------------------|
| new_vm4 	| vhpc-esx-02.hpc.vmware.com 	|
| new_vm5 	| vhpc-esx-03.hpc.vmware.com 	|
| new_vm6 	| vhpc-esx-02.hpc.vmware.com 	|
| new_vm7 	| vhpc-esx-03.hpc.vmware.com 	|

Note that the host range 2-3 has been expanded by repeating the
range to match the number of VMs: 2, 3, 2, 3.<br><br>

The expansion in the consecutive case is shown in table blow.

| **VM**  	| **Host**                   	|
|---------	|----------------------------	|
| new_vm4 	| vhpc-esx-02.hpc.vmware.com 	|
| new_vm5 	| vhpc-esx-02.hpc.vmware.com 	|
| new_vm6 	| vhpc-esx-03.hpc.vmware.com 	|
| new_vm7 	| vhpc-esx-03.hpc.vmware.com 	|

The syntax for defining round-robin ranges is `{x:y}` and the syntax
for defining consecutive ranges is `{{x:y}}`, where x is the beginning
of the range and y is the end of the range. When you perform a cluster-level
operation that includes ranges, the ranges will be expanded and
the user will be prompted to confirm the action.

### Networking Section
Additionally, the user can also define operations to create/destroy SVS
or DVS in the cluster configuration file. The section should have the
section name `_SVS_` or `_DVS_`, e.g.:
```
[HOST-LIST]
host: vhpc-esx-0{5:8}.hpc.vmware.com

[_DVS_]
pvrdma-dvs: pnic: vmnic5 port_group: pvrdma-pg HOSTLIST
```
which creates a DVS named `pvrdma-dvs` with pnic `vmnic5` from
the hosts defined in the `HOST-LIST` property section and also
creates a port group `pvrdma-pg` within this DVS.

### Available keys in cluster configuration file 

These are the keys whose values can be handled by the `create` command in 
cluster-level operation. For the keys that are highlighted, their values can be defined in ranges. 

See the [examples/cluster-scripts](../examples/cluster-scripts) directory for examples.

The keys can de defined in `[_VMS_]` section: 

|        Key         | Definition    |  Type  |                                                                                               Note                                                                                               | 
|:------------------:|:---------------:|:----:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
|      template      | Name of the template VM to clone from | string  |                                                                                   Must be an existing template                                                                                   |
|        cpu         | Number of CPUs  |  int |                                                                       If omitted, it will be the same as the template VM.                                                                        | 
|       memory       | Amount of memory (in GB) |  float |                                                                       If omitted, it will be the same as the template VM.                                                                        | 
|     datacenter     | Name of the destination datacenter  |  string |                                     If specified, it must be an existing datacenter. If omitted, the first datacenter in the vCenter inventory will be used.                                     | 
|     vm_folder      | Name of the destination VM folder      |  string    |                                If specified, it must be an existing vm folder. If omitted, the first VM folder in the specified/default datacenter will be used.                                 | 
|      cluster       | Name of the destination cluster |  string |                                  If specified, it must be an existing cluster. If omitted, the first cluster in the specified/default datacenter will be used.                                   | 
|      **host**      |   Name of the destination host |  string |                       If specified, it must be an existing host. If omitted, the first host in the specified/default cluster will be used. Value can be defined in range.                        | 
|   **datastore**    |  Name of the destination datastore     | string |                    If specified, it must be an existing datastore. If omitted, the first datastore in the specified/default host will be used. Value can be defined in range.                    | 
|   resource_pool    |  Name of the destination resource pool     |  string   |                              If specified, it must be an existing resource pool. If omitted, the first resource pool in the specified/default cluster will be used.                              |           
|     port_group     |  Name of the network port group     | string     | If a port group with same name is already configured for the VM (e.g. cloned from template), it will continue to configure network settings. Otherwise, it will add a new port group for the VM. |   
|      is_dhcp       |   whether to use DHCP for the network   | string or int |                                                             Available: yes, y, true, t, 1 or no, n, false, f, 0 (not case sensitive)                                                             |  
|       **ip**       |  IP address for network     | string |                                                                  Should in IPv4 address format. Value can be defined in range.                                                                   |
| **guest_hostname** |  Hostname of Guest OS  | string |                                                                                  Value can be defined in range.                                                                                  |
|      netmask       |  Netmask for the network     | string |                                                                                  Should in IPv4 address format.                                                                                  | 
|      gateway       |  Gateway for the network      |  string |                                                                                  Should in IPv4 address format.                                                                                  |            
|       domain       |   Domain name for the network    |  string |                                                                                                                                                                                                  |             
|        dns         |   DNS servers for the network    | list of strings   |                                                            Format: ['dns1'] or ['dns1', 'dns2'] Each DNS server IP should be quoted.                                                             |
|       device       |  Device IDs of PCI devices      | list of strings |                                                          Format: ['deviceID1', 'deviceID2', ...] Each deviceID string should be quoted.                                                          |       
|      latency       |  Latency sensitivity level     |  string  |                                                                                    Available: high or normal                                                                                     |
|  cpu_reservation   | Whether to reserve all guest CPUs   | string or int |                                                            Available:  yes, y, true, t, 1 or no, n, false, f, 0 (not case sensitive).                                                            |  
| memory_reservation | Whether to reserve all guest memory  |  string or int |                                                            Available: yes, y, true, t, 1 or no, n, false, f, 0 (not case sensitive).                                                             |  
|     cpu_shares     | Shares of CPU for VM  | int |                                                                                                                                                                                                  |  
|   memory_shares    |  Shares of memory for VM |  int |                                                                                                                                                                                                  |  
|   guest_username   |  Guest OS username     | string   |                                                                                          Default: root                                                                                           | 
|   guest_password   |  Guest OS password     | string   |                                                                           If it's not specified, you will be prompted.                                                                           |
|       script       | The path of local script to be executed in guest OS | string |                                                                 If you define multiple scripts, it will be appended into a list                                                                  |
|      sequence      | The execution order of post script  | int |           Scripts will be executed as the order specified by sequence key. See cluster-post.conf for example. Without cluster key, by default, scripts wil be executed simultaneously            |
|  sriov_port_group  |  Name of port group which enables SR-IOV adapter type | string |                                                     The SR-IOV network adapter must be backed up by a Physical Function with SR-IOV enabled.                                                     |   
|         pf         |  Name of physical function     | string     |                                                               The Physical Function is required for backing up SR-IOV Passthrough.                                                               | 
| pvrdma_port_group  |  Name of virtual network adapter which enables PVRDMA adapter type    | string     |                                                                     The adapter should be from a Distributed Virtual Switch.                                                                     |   
|        vgpu        |  Profile of the vGPU     | string     |                                         Profile represents the vGPU type. If multiple VMs sharing a GPU on a ESXi host, all VMs should use same profile.                                         |   
|       power        |  Power status of VMs     | string     |                                                Whether to power on this VM after provision. Default is to power on VMs unless "off" is specified                                                 |

The keys can de defined in `[_SVS_]` section for creating/destroying Standard Virtual Switch (SVS): 

| Key | Definition    |  Type | 
| :----------:|:---------------:|:----:|
| port_group  |  Name of virtual port group to be created within this SVS| string |  
| **host**  |   Name of ESXi host on which to create a SVS|  string |    
| pnic |  Physical NIC to be added into this SVS  | string |   

The keys can de defined in `[_DVS_]` section for creating/destroying Distributed Virtual Switch (DVS): 

| Key | Definition    |  Type  |
| :----------:|:---------------:|:----:|
| port_group|  Name of virtual port group to be created within this DVS|string |  
| **host**  |   Name of ESXi host to be added into this DVS |  string |   
| pnic |  Physical NIC(s) on each host to be added into this DVS  | string |   
| datacenter   | Name of the destination datacenter for creating DVS  |  string | 
