# How to add a new command?


Most of the commands can be added in 3 simple steps

## 1. Get Input
- Define all the input arguments in the get_args.py file
- Arguments can belong to mutually exclusive groups
- Datatype can be custom class where we mention conditions. Ex: affinity – `4:10:2`, `4.10`, `4:3`, `3a:10` all raise an error
- Custom datatype takes in the name of a function
- For custom datatypes, all the input arguments are passed as strings on which we can make additional checks

## 2. Get Object
- Create Operations object initialized with all the arguments and create connection to vCenter.
- Pass connection object to get_objs.py and get the object to operate on for the function.
- For cluster command, path for cluster config file passed as argument.
- Then call cluster.py from operations.py. cluster.py reads from cluster config file and returns config object as key value pairs.

## 3. Perform Operation
- After getting all the argument values, operations.py does all the preprocessing necessary to perform the operation
- Can combine multiple services which act on the resource - ex: destroying a VM first involves making sure that the VM is turned off. Then call destroy function. This combination can be done in operations.py
- Some operations are async, so collect operation and call wait.
