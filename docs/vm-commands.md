# Commands associated with VM

## clone
To clone a VM


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
## post
## get_vm_config