# Commands

This is a list of all the commands available to use

| **Command**          	 | **What does it do?**                                                                                                	|
|------------------------|---------------------------------------------------------------------------------------------------------------------	|
| view                 	 | View the vCenter object names                                                                                       	|
| cluster              	 | Create/Destroy vHPC cluster based on cluster configuration file                                                     	|
| clone                	 | Clone VM(s) via Full Clone or Linked Clone                                                                          	|
| destroy              	 | Destroy VM(s)                                                                                                       	|
| power                	 | Power on/off VM(s)                                                                                                  	|
| secure_boot          	 | Turn secure boot on/off VM(s)                                                                                       	|
| migrate_vm           	 | Migrate VM(s) to a different host                                                                                   	|
| cpumem               	 | Reconfigure CPU/memory for VM(s)                                                                                    	|
| latency              	 | Configure/Check latency sensitivity                                                                                 	|
| vm_sched_affinity    	 | Change VM scheduling affinity                                                                                       	|
| numa_affinity        	 | Change NUMA node affinity                                                                                           	|
| network              	 | Add/Remove network adapter(s) for VM(s)                                                                             	|
| network_cfg          	 | Configure network(s) for VM(s)                                                                                      	|
| passthru             	 | Add/Remove (large) PCI device(s) in Passthrough mode                                                                	|
| sriov                	 | Add/remove single root I/O virtualization (SR-IOV) device(s)                                                        	|
| pvrdma               	 | Add/Remove PVRDMA (Paravirtual RDMA) device(s)                                                                      	|
| vgpu                 	 | Add/Remove vGPU device in SharedPassthru mode                                                                       	|
| post                 	 | Execute post script(s) in guest OS                                                                                  	|
| get_vm_config        	 | View the performance metrics of the VM                                                                              	|
| power_policy         	 | Change the power policy for the host                                                                                	|
| sriov_host           	 | Modify SR-IOV configuration on host(s). This operation assumes that SR-IOV drivers have been installed on ESXi host 	|
| svs                  	 | Create/destroy a standard virtual switch                                                                            	|
| dvs                  	 | Create/destroy a distributed virtual switch                                                                         	|