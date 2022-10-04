### Available keys in cluster configuration file 

These are the keys whose values can be handled by the `create` command in 
cluster-level operation. For the keys that are highlighted, their values can be defined in ranges. 

See the [examples/cluster-scripts](../examples/cluster-scripts) directory for examples.

The keys can de defined in `[_VMS_]` section: 

|        Key         | Definition    |  Type  | Note| 
|:------------------:|:---------------:|:----:| :----:|
|      template      | Name of the template VM to clone from | string  | Must be an existing template  |
|        cpu         | Number of CPUs  |  int | If omitted, it will be the same as the template VM.| 
|       memory       | Amount of memory (in GB) |  float | If omitted, it will be the same as the template VM. | 
|     datacenter     | Name of the destination datacenter  |  string | If specified, it must be an existing datacenter. If omitted, the first datacenter in the vCenter inventory will be used. | 
|     vm_folder      | Name of the destination VM folder      |  string    | If specified, it must be an existing vm folder. If omitted, the first VM folder in the specified/default datacenter will be used.| 
|      cluster       | Name of the destination cluster |  string | If specified, it must be an existing cluster. If omitted, the first cluster in the specified/default datacenter will be used. | 
|      **host**      |   Name of the destination host |  string | If specified, it must be an existing host. If omitted, the first host in the specified/default cluster will be used. Value can be defined in range.  | 
|   **datastore**    |  Name of the destination datastore     | string | If specified, it must be an existing datastore. If omitted, the first datastore in the specified/default host will be used. Value can be defined in range. | 
|   resource_pool    |  Name of the destination resource pool     |  string   | If specified, it must be an existing resource pool. If omitted, the first resource pool in the specified/default cluster will be used. |           
|     port_group     |  Name of the network port group     | string     | If a port group with same name is already configured for the VM (e.g. cloned from template), it will continue to configure network settings. Otherwise, it will add a new port group for the VM. |   
|      is_dhcp       |   whether to use DHCP for the network   | string or int | Available: yes, y, true, t, 1 or no, n, false, f, 0 (not case sensitive)|  
|       **ip**       |  IP address for network     | string | Should in IPv4 address format. Value can be defined in range. |
| **guest_hostname** |  Hostname of Guest OS  | string | Value can be defined in range.  |
|      netmask       |  Netmask for the network     | string | Should in IPv4 address format. | 
|      gateway       |  Gateway for the network      |  string | Should in IPv4 address format. |            
|       domain       |   Domain name for the network    |  string |  |             
|        dns         |   DNS servers for the network    | list of strings   |Format: ['dns1'] or ['dns1', 'dns2'] Each DNS server IP should be quoted. |
|       device       |  Device IDs of PCI devices      | list of strings | Format: ['deviceID1', 'deviceID2', ...] Each deviceID string should be quoted.|       
|      latency       |  Latency sensitivity level     |  string  | Available: high or normal     |
|  cpu_reservation   | Whether to reserve all guest CPUs   | string or int | Available:  yes, y, true, t, 1 or no, n, false, f, 0 (not case sensitive). |  
| memory_reservation | Whether to reserve all guest memory  |  string or int | Available: yes, y, true, t, 1 or no, n, false, f, 0 (not case sensitive).|  
|     cpu_shares     | Shares of CPU for VM  | int |  |  
|   memory_shares    |  Shares of memory for VM |  int | |  
|   guest_username   |  Guest OS username     | string   | Default: root | 
|   guest_password   |  Guest OS password     | string   | If it's not specified, you will be prompted. |
|       script       | The path of local script to be executed in guest OS | string | If you define multiple scripts, it will be appended into a list|
|      sequence      | The execution order of post script  | int | Scripts will be executed as the order specified by barrier key. See cluster-post.conf for example. Without barrier key, by default, scripts wil be executed simultaneously|
|  sriov_port_group  |  Name of port group which enables SR-IOV adapter type | string | The SR-IOV network adapter must be backed up by a Physical Function with SR-IOV enabled. |   
|         pf         |  Name of physical function     | string     | The Physical Function is required for backing up SR-IOV Passthrough. | 
| pvrdma_port_group  |  Name of virtual network adapter which enables PVRDMA adapter type    | string     | The adapter should be from a Distributed Virtual Switch.  |   
|        vgpu        |  Profile of the vGPU     | string     | Profile represents the vGPU type. If multiple VMs sharing a GPU on a ESXi host, all VMs should use same profile. |   
|       power        |  Power status of VMs     | string     | Whether to power on this VM after provision. Default is to power on VMs unless "off" is specified |

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
