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

## dvs

## cluster