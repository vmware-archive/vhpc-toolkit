#!/usr/bin/env bash

yum -y install wget
wget https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda_8.0.61_375.26_linux-run
sh cuda_8.0.61_375.26_linux-run --silent

echo "LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc
echo "PATH=/usr/local/cuda/bin:$PATH" >> ~/.bashrc
echo "export PATH LD_LIBRARY_PATH" >> ~/.bashrc

