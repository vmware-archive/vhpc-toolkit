# Commands associated with host

## power_policy
Select the power policy for the host(s) mentioned
```bash
./vhpc_toolkit power_policy [-h] (--host HOST | --file FILE) --policy {1,2,3,4}
```

| **Argument**          	 | **What does it do?**                       | Group | Type              |
|-----------------------|--------------------------------------------|-------|-------------------|
| host                 	 | Name of the host whose power policy must be changed | 1     | string            |
| file            	     | Name of the file containing a list of host(s), one per line, to perform the change power policy operation| 1     | string            |
| policy                	 | The power policy to change it to. Specify the corresponding index for the power policy  |       | integer [1,2,3,4] |

Each policy number corresponds to different policy

| **Policy Number**   | **Coressponding policy** |
|---------------------|-------------------------|
| 1                 	 | High Performance        |
| 2              	    | Balanced                | 
| 3                	  | Low Power               |
| 4                	  | Custom                  |


!> This command assumes that there are 4 standard power policies avaialable for the host

## sriov_host
Modify SR-IOV configuration on host(s). 

!> This command assumes that SR-IOV drivers are already installed on ESXi host 

```bash
./vhpc_toolkit sriov_host [-h] (--host HOST | --file FILE) --device DEVICE (--on | --off) [--num_func NUM_FUNC]
```


| **Argument**          	   | **What does it do?**                                                                                                                       | Group | Type    | Required    |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|------|---------|-------------|
| host                 	    | Name of the host on which to perform the modify SR-IOV operation                                                                           | 1    | string  | Yes (Group) |
| file            	         | Name of the file containing a list of host(s), one per line, to perform the modify SR-IOV operation                                        | 1    | string  | Yes (Group) |
| device                	   | PCIe address of the Virtual Function (VF) of the SR-IOV device in format `xxxx:xx:xx.x`                                                      |      | string  | Yes         |
| on                	       | Turn on SR-IOV mode for device on host(s)                                                                                                  | 2    | None    | Yes (Group) |
| off                	      | Turn off SR-IOV mode for device on host(s)                                                                                                 | 2    | None    | Yes (Group) |
| num_func                	 | Number of virtual functions. This argument is ignored if used with --off flag. num_func must be equal or smaller than the VF enabled in firmware |      | integer | No          |

!> The **num_func** argument is ignored if used with --off flag. **num_func** must be equal to or smaller than the virtual functions enabled in firmware
