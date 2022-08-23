# Commands

This is a list of all the commands available to use

| **Command**          	                                     | **What does it do?**                                                                                                	|
|------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------	|
| [view](common-commands.md#view)                 	          | View the vCenter object names                                                                                       	|
| [cluster](common-commands.md#cluster)              	       | Create/Destroy vHPC cluster based on cluster configuration file                                                     	|
| [clone](vm-commands.md#clone)                	             | Clone VM(s) via Full Clone or Linked Clone                                                                          	|
| [destroy](vm-commands.md#destroy)              	           | Destroy VM(s)                                                                                                       	|
| [power](vm-commands.md#power)                	             | Power on/off VM(s)                                                                                                  	|
| [secure_boot](vm-commands.md#secure_boot)          	       | Turn secure boot on/off VM(s)                                                                                       	|
| [migrate_vm](vm-commands.md#migrate_vm)           	        | Migrate VM(s) to a different host                                                                                   	|
| [cpumem](vm-commands.md#cpumem)               	            | Reconfigure CPU/memory for VM(s)                                                                                    	|
| [latency](vm-commands.md#latency)              	           | Configure/Check latency sensitivity                                                                                 	|
| [vm_sched_affinity](vm-commands.md#vm_sched_affinity)    	 | Change VM scheduling affinity                                                                                       	|
| [numa_affinity](vm-commands.md#numa_affinity)        	     | Change NUMA node affinity                                                                                           	|
| [network](vm-commands.md#network)              	           | Add/Remove network adapter(s) for VM(s)                                                                             	|
| [network_cfg](vm-commands.md#network_cfg)          	       | Configure network(s) for VM(s)                                                                                      	|
| [passthru](vm-commands.md#passthru)             	          | Add/Remove (large) PCI device(s) in Passthrough mode                                                                	|
| [sriov](vm-commands.md#sriov)                	             | Add/remove single root I/O virtualization (SR-IOV) device(s)                                                        	|
| [pvrdma](vm-commands.md#pvrdma)               	            | Add/Remove PVRDMA (Paravirtual RDMA) device(s)                                                                      	|
| [vgpu](vm-commands.md#vgpu)                                | Add/Remove vGPU device in SharedPassthru mode                                                                       	|
| [post](vm-commands.md#post)                 	              | Execute post script(s) in guest OS                                                                                  	|
| [get_vm_config](vm-commands.md#get_vm_config)        	     | View the performance metrics of the VM                                                                              	|
| [power_policy](host-commands.md#power_policy)        	     | Change the power policy for the host                                                                                	|
| [sriov_host](host-commands.md#sriov_host)           	      | Modify SR-IOV configuration on host(s). This operation assumes that SR-IOV drivers have been installed on ESXi host 	|
| [svs](common-commands.md#svs)                  	           | Create/destroy a standard virtual switch                                                                            	|
| [dvs](common-commands.md#dvs)                  	           | Create/destroy a distributed virtual switch                                                                         	|

## Instructions to use documentation

- If an argument takes only pre-defined values, all possible values are specified using the `{option1, option2 ..}` notation
- Some of the arguments are flags in themselves. When using these arguments, there is no need to pass any values. Such arguments can be identified by checking their datatypes. It is marked as none for these arguments since they don't take any values.
- A group specifies a collection of flags of which at-most one argument of a given group can be used at once
- For many commands, each flag is not mandatory. But some groups might be mandatory. That means, one argument from mandatory group must be used with the command