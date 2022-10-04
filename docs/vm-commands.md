# Commands associated with VM

## clone
To clone a VM

```bash
./vhpc_toolkit clone [-h] (--vm VM | --file FILE) [--linked] --template TEMPLATE [--datacenter DATACENTER] [--vm_folder VM_FOLDER] [--cluster CLUSTER] [--host HOST] [--datastore DATASTORE]
                          [--resource_pool RESOURCE_POOL] [--memory MEMORY] [--cpu CPU]
```

| **Argument**  	| **What does it do?**                                                                                                     	| Group 	| Type    	| Required    	|
|---------------	|-------------------------------------------------------------------------------------------------------------------------	|-------	|---------	|-------------	|
| vm            	| Name of the cloned VM                                                                                                    	| 1     	| string  	| True(Group) 	|
| file          	| Name of the file with one clone destination specification (format: `cloned_VM cluster host datastore`) per line          	| 1     	| string  	| True(Group) 	|
| linked        	| Enable linked clone.If linked clone is enabled, the dest datastore will be same as template's datastore.                 	|       	| None    	| False       	|
| template      	| Name of the template VM to clone from                                                                                    	|       	| string  	| True        	|
| datacenter    	| Name of the destination datacenter.If omitted, the first datacenter in the vCenter inventory will be used.               	|       	| string  	| False       	|
| vm_folder     	| Name of the destination VM folder.If omitted, the first VM folder in the specified/default datacenter will be used.      	|       	| string  	| False       	|
| cluster       	| Name of the destination cluster.If omitted, the first cluster in the specified/default datacenter will be used.          	|       	| string  	| False       	|
| host          	| Name of the destination host.If omitted, the first host in the specified/default cluster will be used.                   	|       	| string  	| False       	|
| datastore     	| Name of the destination datastore.If omitted, the same datastore of the template will be used.                           	|       	| string  	| False       	|
| resource_pool 	| Name of the destination resource pool.If omitted, the first resource pool in the specified/default cluster will be used. 	|       	| string  	| False       	|
| memory        	| Memory (in GB) for the cloned VM(s).If omitted, it will be the same as the template VM.                                  	|       	| float   	| False       	|
| cpu           	| Number of CPUs for the cloned VM(s).If omitted, it will be the same as the template VM.                                  	|       	| integer 	| False       	|

## destroy
To destroy VM(s)

```bash
./vhpc_toolkit destroy [-h] (--vm VM | --file FILE)
```

| **Argument** 	| **What does it do?**                                               	| Group 	| Type   	| Required    	|
|--------------	|--------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM to destroy                                          	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line to destroy 	| 1     	| string 	| True(Group) 	|

## power
To Power on/off VM(s)

```bash
./vhpc_toolkit power [-h] (--vm VM | --file FILE) (--on | --off)
```

| **Argument** 	| **What does it do?**                                               	| Group 	| Type   	| Required    	|
|--------------	|--------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM to destroy                                          	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line to destroy 	| 1     	| string 	| True(Group) 	|

## secure_boot
To enable/disable secure boot for VM(s)

```bash
./vhpc_toolkit secure_boot [-h] (--vm VM | --file FILE) (--on | --off)
```

| **Argument** 	| **What does it do?**                                                            	| Group 	| Type   	| Required    	|
|--------------	|---------------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM which for which we need to enable/disable secure boot            	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, to perform the secure boot operation 	| 1     	| string 	| True(Group) 	|
| on           	| Secure boot on                                                                  	| 2     	| None   	| True(Group) 	|
| off          	| Secure boot off                                                                 	| 2     	| None   	| True(Group  	|

## migrate_vm
To migrate VM(s) to a different host

```bash
./vhpc_toolkit migrate_vm [-h] (--vm VM | --file FILE) --destination DESTINATION
```

| **Argument** 	| **What does it do?**                                                    	| Group 	| Type   	| Required    	|
|--------------	|-------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM which needs to be migrated to a different host           	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, to perform migrate operation 	| 1     	| string 	| True(Group) 	|
| destination  	| The name of the destination host, the VM(s) must be migrated to         	|       	| string 	| True        	|

## cpumem
Reconfigure CPU/memory for VM(s)

```bash
vhpc_toolkit cpumem [-h] (--vm VM | --file FILE) [--memory MEMORY] [--cpu CPU] [--cpu_shares CPU_SHARES] [--cores_per_socket CORES_PER_SOCKET] [--memory_shares MEMORY_SHARES]
                           [--memory_reservation MEMORY_RESERVATION] [--cpu_reservation CPU_RESERVATION]
```

| **Argument**       	| **What does it do?**                                                                                                	| Group 	| Type                                        	| Required    	|
|--------------------	|---------------------------------------------------------------------------------------------------------------------	|-------	|---------------------------------------------	|-------------	|
| vm                 	| Name of the VM on which to reconfigure CPU/memory                                                                   	| 1     	| string                                      	| True(Group) 	|
| file               	| Name of the file containing a list of VMs, one per line, to reconfigure CPU/memory                                  	| 1     	| string                                      	| True(Group) 	|
| memory             	| New memory (in GB) for VM(s)                                                                                        	|       	| float                                       	| False       	|
| cpu                	| New number of CPUs for VM(s)                                                                                        	|       	| integer                                     	| False       	|
| cpu_shares         	| Shares of CPUs for VM(s)                                                                                            	|       	| integer                                     	| False       	|
| cores_per_socket   	| Cores per socket for VM(s)                                                                                          	|       	| integer                                     	| False       	|
| memory_shares      	| Shares of memory for VM(s)                                                                                          	|       	| integer                                     	| False       	|
| memory_reservation 	| Whether to reserve memory.<br>Reserve memory: y, yes, t, true, or 1. <br>Not reserve memory: n, no, f, false, or 0. 	|       	| `{y,yes,t,true,1}`<br>`{n, no, f, false, 0}` 	| False       	|
| cpu_reservation    	| Whether to reserve CPU. <br>Reserve CPU: y, yes, t, true, or 1. <br>Not reserve CPU: n, no, f, false, or 0.         	|       	| `{y,yes,t,true,1}`<br>`{n, no, f, false, 0}` 	| False       	|

## latency
Configure/Check latency sensitivity

```bash
./vhpc_toolkit latency [-h] (--vm VM | --file FILE) [--level LEVEL] [--check]
```
| **Argument** 	| **What does it do?**                                                                      	| Group 	| Type             	| Required    	|
|--------------	|-------------------------------------------------------------------------------------------	|-------	|------------------	|-------------	|
| vm           	| Name of the VM on which to configure latency sensitivity                                  	| 1     	| string           	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line, to configure latency sensitivity 	| 1     	| string           	| True(Group) 	|
| level        	| Set Latency Sensitivity level, available: high or normal                                  	|       	| `{high, normal}` 	| False       	|
| check        	| Check Latency Sensitivity level                                                           	|       	| None             	| False       	|

## vm_sched_affinity
Change VM scheduling affinity

```bash
./vhpc_toolkit vm_sched_affinity [-h] (--vm VM | --file FILE) (--affinity AFFINITY | --clear)
```

| **Argument** 	 | **What does it do?**                                                                                                                                                           	| Group 	| Type   	| Required    	|
|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	 | Name of the VM on which to configure latency sensitivity                                                                                                                       	| 1     	| string 	| True(Group) 	|
| file         	 | Name of the file containing a list of VMs, one per line, to reconfigure vm scheduling affinity                                                                                 	| 1     	| string 	| True(Group) 	|
| affinity     	 | Affinity range. Use `:` for separating ranges and steps, and `,` to separate values.<br>For example - `0, 2, 4:7, 8:12:2`  would indicate processors `0, 2, 4, 5, 6, 7, 8, 10, 12` 	| 2     	| string 	| True(Group) 	|
| clear        	 | Clear the scheduling affinity settings for the VM(s)                                                                                                                           	| 2     	| None   	| True(Group) 	|

!> VM needs to be powered off to change scheduling affinity settings
<br>
Valid affinity range specifications should always be of type `lower_limit:upper_limit:step_length`. Both limits are included in the range

## numa_affinity
Change NUMA node affinity

```bash
./vhpc_toolkit numa_affinity [-h] (--vm VM | --file FILE) (--affinity AFFINITY | --clear)
```

| **Argument** 	| **What does it do?**                                                                                                                                                           	| Group 	| Type   	| Required    	|
|--------------	|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM on which to change NUMA node affinity                                                                                                                           	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line, to reconfigure NUMA node affinity                                                                                     	| 1     	| string 	| True(Group) 	|
| affinity     	| Affinity range. Use `:` for separating ranges and steps, and `,` to separate values.<br>For example - `0, 2, 4:7, 8:12:2`  would indicate processors `0, 2, 4, 5, 6, 7, 8, 10, 12` 	| 2     	| string 	| True(Group) 	|
| clear        	| Clear the NUMA affinity settings for the VM(s)                                                                                                                                 	| 2     	| None   	| True(Group) 	|

!> VM needs to be powered off to change NUMA affinity settings

## network
Add/Remove network adapter(s) for VM(s)

```bash
./vhpc_toolkit network [-h] (--vm VM | --file FILE) (--add | --remove) --port_group PORT_GROUP [PORT_GROUP ...]
```

| **Argument** 	| **What does it do?**                                                     	| Group 	| Type         	| Required    	|
|--------------	|--------------------------------------------------------------------------	|-------	|--------------	|-------------	|
| vm           	| Name of the VM on which to add network adapter                           	| 1     	| string       	| True(Group) 	|
| file         	| Name of the file with one vm name per line to add/remove network adapter 	| 1     	| string       	| True(Group) 	|
| port_group   	| Port group for the network adapter to add/remove                         	|       	| list[string] 	| True        	|
| add          	| Add a network adapter                                                    	| 2     	| None         	| True(Group) 	|
| remove       	| Remove a network adapter                                                 	| 2     	| None         	| True(Group) 	|

## network_cfg
Configure network(s) for VM(s)

```bash
./vhpc_toolkit network_cfg [-h] --vm VM --port_group PORT_GROUP (--is_dhcp | --ip IP) --netmask NETMASK --gateway GATEWAY --dns DNS [DNS ...] --domain DOMAIN [--guest_hostname GUEST_HOSTNAME]
```

| **Argument**   	| **What does it do?**                                                     	| Group 	| Type         	| Required    	|
|----------------	|--------------------------------------------------------------------------	|-------	|--------------	|-------------	|
| vm             	| Name of the VM on which to configure network                             	|       	| string       	| True        	|
| port_group     	| Number of the network adapter on which to configure network              	|       	| string       	| True        	|
| ip             	| Static IP address if not use DHCP                                        	| 1     	| string       	| True(Group) 	|
| is_dhcp        	| Use DHCP for this network                                                	| 1     	| None         	| True(Group) 	|
| netmask        	| Netmask                                                                  	|       	| string       	| True        	|
| gateway        	| Gateway                                                                  	|       	| string       	| True        	|
| dns            	| DNS server(s)                                                            	|       	| list[string] 	| True        	|
| domain         	| Domain name                                                              	|       	| string       	| True        	|
| guest_hostname 	| Hostname of Guest OS. If omitted, VM name will be used as guest hostname 	|       	| string       	| False       	|

## passthru
Add/Remove (large) PCI device(s) in Passthrough mode

```bash
 ./vhpc_toolkit passthru [-h] (--vm VM | --file FILE) [--query] [--remove | --add] [--device DEVICE [DEVICE ...]] [--mmio_size MMIO_SIZE] [--dynamic]
```

| **Argument** 	| **What does it do?**                                                                          	| Group 	| Type         	| Required    	|
|--------------	|-----------------------------------------------------------------------------------------------	|-------	|--------------	|-------------	|
| vm           	| Name of the VM on which to perform the passthrough operation                                  	| 1     	| string       	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line, to perform the passthrough operation 	| 1     	| string       	| True(Group) 	|
| query        	| Print available passthrough device(s) information for the VM(s)                               	|       	| None         	| False       	|
| add          	| Add device(s)                                                                                 	| 2     	| None         	| False       	|
| remove       	| Remove device(s)                                                                              	| 2     	| None         	| False       	|
| device       	| Device ID of the PCI device(s), for example: `0000:05:00.0`                                   	|       	| list[string] 	| False       	|
| mmio_size    	| 64-bit MMIO size in GB for PCI device with large BARs. Default: 256.                          	|       	|              	| False       	|
| dynamic      	| If this flag is added, PCI devices are added in dynamic direct i/o mode                       	|       	| None         	| False       	|


!? mmio_size should be a power of 2. If not, the value is ignored and default value of 256 is used
## pvrdma
Add/Remove PVRDMA (Paravirtual RDMA) device(s)

```bash
./vhpc_toolkit pvrdma [-h] (--vm VM | --file FILE) (--add | --remove) --pvrdma_port_group PVRDMA_PORT_GROUP --dvs_name DVS_NAME
```

| **Argument**      	| **What does it do?**                                                                     	| Group 	| Type   	| Required    	|
|-------------------	|------------------------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm                	| Name of the VM on which to perform the PVRDMA operation                                  	| 1     	| string 	| True(Group) 	|
| file              	| Name of the file containing a list of VMs, one per line, to perform the PVRDMA operation 	| 1     	| string 	| True(Group) 	|
| add               	| Add PVRDMA device to VM(s)                                                               	| 2     	| None   	| True(Group) 	|
| remove            	| Remove PVRDMA device from VM(s)                                                          	| 2     	| None   	| True(Group) 	|
| pvrdma_port_group 	| Name of virtual network adapter which could enable PVRDMA                                	|       	| string 	| True        	|
| dvs_name          	| Name of distributed virtual switch which could enable PVRDMA                             	|       	| string 	| True        	|


## vgpu
Add/Remove vGPU device in SharedPassthru mode

```bash
vhpc_toolkit vgpu [-h] (--vm VM | --file FILE) [--query] [--remove | --add] [--profile PROFILE]
```

| **Argument** 	| **What does it do?**                                                                   	| Group 	| Type   	| Required    	|
|--------------	|----------------------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM on which to perform the vGPU operation                                  	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line, to perform the vGPU operation 	| 1     	| string 	| True(Group) 	|
| query        	| Print available vGPU profiles information for the VM(s)                                	|       	| None   	| False       	|
| remove       	| Remove vGPU profile                                                                    	| 2     	| string 	| False       	|
| add          	| Add vGPU profile                                                                       	| 2     	| string 	| False       	|
| profile      	| Profile of the vGPU, for example: `grid_p100-4q`                                       	|       	| string 	| False       	|

?> When using **add**, **profile** must be specified

## post
Run a shell script(s) on remote VM(s)
```bash
./vhpc_toolkit post [-h] (--vm VM | --file FILE) --script SCRIPT [SCRIPT ...] [--guest_username GUEST_USERNAME] [--guest_password GUEST_PASSWORD] [--wait]
```

| **Argument**   	| **What does it do?**                                                               	| Group 	| Type         	| Required    	  |
|----------------	|------------------------------------------------------------------------------------	|-------	|--------------	|----------------|
| vm             	| Name of the VM on which to execute post script(s)                                  	| 1     	| string       	| True(Group) 	  |
| file           	| Name of the file containing a list of VMs, one per line, to execute post script(s) 	| 1     	| string       	| True(Group) 	  |
| script         	| Local post script(s) to be executed in guest OS                                    	|       	| list[string] 	| True        	  |
| guest_username 	| Guest OS username (default: root)                                                  	|       	| string       	| False        	 |
| guest_password 	| Guest OS password. If omitted, it will be prompted.                                	|       	| string       	| False        	 |
| wait           	| Wait for the script execution finish                                               	|       	| string       	| False       	  |

!> If your password contains any restricted characters, escape those characters using `\`

## get_vm_config
Print performance related settings for VM

```bash
./vhpc_toolkit get_vm_config [-h] (--vm VM | --file FILE)
```

| **Argument** 	| **What does it do?**                                                              	| Group 	| Type   	| Required    	|
|--------------	|-----------------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM whose performance related settings should be fetched               	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line, to perform the operation 	| 1     	| string 	| True(Group) 	|