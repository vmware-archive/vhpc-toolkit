# <img src="docs/img/hpc-logo400.png" width="64" valign="middle" alt="vhpclogo"/> vHPC Toolkit

## Overview 

Virtualized High Performance Computing Toolkit (vHPC Toolkit) is a flexible, extensible and easy-to-use toolkit, that allows users to deploy and manage virtualized clusters for High Performance Computing (HPC) and machine learning environments.

[comment]: <> (Due to their extreme demand on performance, HPC workloads often have much 
more intensive resource requirements than those workloads found in the 
typical enterprise. For example, HPC commonly leverages hardware 
accelerators, such as GPU and FPGA for compute as well as RDMA 
interconnects, which require special vSphere configurations. )

This toolkit is intended to facilitate managing the lifecycle of these 
special configurations by leveraging vSphere APIs. It also includes features 
that help vSphere administrators perform some common vSphere tasks that are 
related to creating such high-performing environments, such as VM cloning, 
setting Latency Sensitivity, sizing vCPUs and memory, creating SRIOV dirtributed virtual switch (DVS) network, using assignable hardware (AH) accelerators (RDMA interconnects, GPU and FPGA), etc.

## Try It Out

### Prerequisites

OS for using this toolkit: Linux or Mac <br/>
vSphere >=6.5 <br/>
Python >=3.7 <br/> 

### Install 

Package dependencies will be isolated in a Python virtual environment by 
```virtualenv```. This 
allows us to have different versions of dependencies. 

To install ```virtualenv``` if you don't have one, for example, 

- For Mac: 
```pip install --upgrade virtualenv```
- For Ubuntu: 
```sudo apt-get install python3-pip```; ```sudo pip3 install virtualenv```


Setup this toolkit with an virtual env:
 
```bash 
git clone https://github.com/vmware/vhpc-toolkit.git
cd vhpc-toolkit
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
pip install vhpc_toolkit
```

After proper installation and setup, you should be able to execute ```./vhpc_toolkit view``` under `vhpc_toolkit/bin` folder to view the cluster. 

## Documentation
[Full documentation](https://vmware.github.io/vhpc-toolkit/#/) is available, or run `./vhpc_toolkit --help` under `vhpc_toolkit/bin` folder to view all available 
operations


## Contributing

The vhpc-toolkit project team welcomes contributions from the community. Before you start working with vhpc-toolkit, please
read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be
signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on
as an open-source patch. For more detailed information, refer to [CONTRIBUTING.md](https://vmware.github.io/vhpc-toolkit/#/contribute).

## License

This toolkit is available under the [Apache 2 license](https://vmware.github.io/vhpc-toolkit/#/license).
