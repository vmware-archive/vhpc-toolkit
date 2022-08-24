# Commands not associated with host or VM

## view
Use this command to view all vCenter object names
```bash
./vhpc_toolkit view --networking
```

| **Argument** 	| **What does it do?**                                                                     	| Group 	| Type 	| Required 	|
|--------------	|------------------------------------------------------------------------------------------	|-------	|------	|----------	|
| networking   	| Show all the network objects (virtual switch and network adapters) along with basic view 	|       	| None 	| False    	|

## svs
Create/Destroy Standard Virtual Switch
```bash
./vhpc_toolkit svs --create --host host_name --name switch_name --pnic nic_name --port_group port_group --mtu mtu
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
./vhpc_toolkit dvs --create --host host_name --name dvs_name --pnic pnic1 pnic2 --host host1 host2 host3 --port_group port_group
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