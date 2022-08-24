# Commands associated with VM

## clone
To clone a VM

```bash
./vhpc_toolkit clone --vm vm_name --template template_name
```

| **Argument**  	| **What does it do?**                                                                                                     	| Group 	| Type    	| Required    	|
|---------------	|--------------------------------------------------------------------------------------------------------------------------	|-------	|---------	|-------------	|
| vm            	| Name of the cloned VM                                                                                                    	| 1     	| string  	| True(Group) 	|
| file          	| Name of the file with one clone destination specification (format: `cloned_VM cluster host datastore)` per line          	| 1     	| string  	| True(Group) 	|
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
./vhpc_toolkit destroy --vm vm_name
```

| **Argument** 	| **What does it do?**                                               	| Group 	| Type   	| Required    	|
|--------------	|--------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM to destroy                                          	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line to destroy 	| 1     	| string 	| True(Group) 	|

## power
To Power on/off VM(s)

```bash
./vhpc_toolkit power --vm vm_name --off
```

| **Argument** 	| **What does it do?**                                               	| Group 	| Type   	| Required    	|
|--------------	|--------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM to destroy                                          	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, one per line to destroy 	| 1     	| string 	| True(Group) 	|

## secure_boot
To enable/disable secure boot for VM(s)

```bash
./vhpc_toolkit secure_boot --vm vm_name --on
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
./vhpc_toolkit migrate_vm --vm vm_name --destination host_name
```

| **Argument** 	| **What does it do?**                                                    	| Group 	| Type   	| Required    	|
|--------------	|-------------------------------------------------------------------------	|-------	|--------	|-------------	|
| vm           	| Name of the VM which needs to be migrated to a different host           	| 1     	| string 	| True(Group) 	|
| file         	| Name of the file containing a list of VMs, to perform migrate operation 	| 1     	| string 	| True(Group) 	|
| destination  	| The name of the destination host, the VM(s) must be migrated to         	|       	| string 	| True        	|

## cpumem
## latency
## vm_sched_affinity
## numa_affinity
## network
## network_cfg
## passthru
## pvrdma
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