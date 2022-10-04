# Overview
High Performance Computing (HPC) is the use of parallel-processing techniques
 to solve complex computational problems. HPC systems have the ability to deliver sustained 
performance through the concurrent use of distributed computing resources, 
and they are typically used for solving advanced scientific and engineering problems, 
such as computational fluid dynamics, bioinformatics, 
molecular dynamics, weather modeling and deep learning with neural networks. 
 
Due to their extreme demand on performance, HPC workloads often have much 
more intensive resource requirements than those workloads found in the 
typical enterprise. For example, HPC commonly leverages hardware 
accelerators, such as GPU and FPGA for compute as well as RDMA 
interconnects, which require special vSphere configurations. 

This toolkit is intended to facilitate managing the lifecycle of these 
special configurations by leveraging vSphere APIs. It also includes features 
that help vSphere administrators perform some common vSphere tasks that are 
related to creating such high-performing environments, such as VM cloning, 
setting Latency Sensitivity, and sizing vCPUs, memory, etc.

Feature Highlights:
 
- Configure PCIe devices in DirectPath I/O mode, such as GPGPU, FPGA and RDMA
 interconnects
- Configure NVIDIA vGPU
- Configure RDMA SR-IOV (Single Root I/O Virtualization)
- Configure  PVRDMA (Paravirtualized RDMA)
- Easy creation and  destruction of virtual HPC clusters using cluster 
configuration files
- Perform common vSphere tasks, such as cloning VMs, configuring vCPUs, memory, 
reservations, shares, Latency Sensitivity, Distributed Virtual 
Switch/Standard Virtual Switch, network adapters and network configurations
