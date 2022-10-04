#!/bin/bash
# Example of vHPC-Toolkit Cluster post provision script file to create a SLURM ready cluster
# Author: Yuankun Fu <vhpc-toolkit@vmware.com>
# 1. Change FrontEnd VM's hostname
# 2. Install xCAT and Configure FrontEnd and Compute VMs.
# 3. Install OpenHPC repo
# 4. Install Slurm from OpenHPC repo on FrontEnd and Compute VMs.
# 5. Modify slurm.conf on Frontend
# 6. Install slurm client on all compute nodes
# 7. Start slurm services
# 8. Check nodes's information

# Environment variables
frontend_name="rhel-hpc-demo-frontend"
compute_prefix="rhel-hpc-demo-compute"
first_node=1
last_node=4
compute_group_name="compute"
ip_vlan="192.168.1."
compute_ip_start=160
num_computes=4
num_sockets=2
cores_per_socket=22
threads_per_core=1
 
# [FRONTEND]
# Check FRONTEND's Network
echo "$(date +%T) 1. Change FrontEnd name"
hostnamectl set-hostname ${frontend_name}
 
echo "$(date +%T) 2. install xCAT"
# [FRONTEND]
# Disable SELINUX
setenforce Permissive
echo "Disable SELINUX?"
## Enable xCat's Public repo
dnf install -y wget
wget -P /etc/yum.repos.d https://xcat.org/files/xcat/repos/yum/latest/xcat-core/xcat-core.repo
## Enable the repo of xCat's dependent package for local use
wget -P /etc/yum.repos.d https://xcat.org/files/xcat/repos/yum/xcat-dep/rh8/x86_64/xcat-dep.repo
dnf -y install xCAT >> test.log
## enable xCAT tools for use in current shell
. /etc/profile.d/xcat.sh
# Add provisioned compute nodes to xCat's database
for ((i=$first_node; i <= $last_node; i++)); do mkdef -t node $compute_prefix$i groups=$compute_group_name,all ip=$ip_vlan$(( i + compute_ip_start)) arch=x86_64; done
# Add compute nodes to /etc/hosts
for ((i=$first_node; i <= $last_node; i++)); do echo "$ip_vlan$(( i + compute_ip_start)) $compute_prefix$i" >> /etc/hosts; done

echo "$(date +%T) 2.1 Change Compute nodes name"
for ((i=$first_node; i <= $last_node; i++)); do xdsh $compute_prefix$i hostnamectl set-hostname $compute_prefix$i; done
# Sync DNS files to all compute nodes
xdcp $compute_group_name /etc/resolv.conf /etc/resolv.conf
xdsh $compute_group_name systemctl restart network-online.target
xdsh $compute_group_name hostname | sort
# Sync hosts file to all compute nodes
xdcp $compute_group_name /etc/hosts /etc/

echo "$(date +%T) 2.2 Disable the Firewall for FrontEnd and Compute nodes"
systemctl disable firewalld.service
xdsh $compute_group_name systemctl disable firewalld.service

# [FRONTEND]
echo "$(date +%T) 3. Install OpenHPC repo on FrontEnd and Compute nodes"
dnf -y install http://repos.openhpc.community/OpenHPC/2/CentOS_8/x86_64/ohpc-release-2-1.el8.x86_64.rpm
# Install OpenHPC repo on all compute nodes
xdsh $compute_group_name dnf -y install http://repos.openhpc.community/OpenHPC/2/CentOS_8/x86_64/ohpc-release-2-1.el8.x86_64.rpm

# [FRONTEND]
echo "$(date +%T) 4. Install Slurm server on Frontend"
dnf -y install ohpc-slurm-server >> test.log

echo "$(date +%T) 5. Modify slurm.conf on Frontend"
cp /etc/slurm/slurm.conf.ohpc /etc/slurm/slurm.conf
cd /etc/slurm
sed -i "s/^\(NodeName.*\)/#\1/" /etc/slurm/slurm.conf
echo "NodeName=${compute_prefix}[${first_node}-${last_node}] Sockets=${num_sockets} CoresPerSocket=${cores_per_socket} ThreadsPerCore=${threads_per_core} State=UNKNOWN" >> /etc/slurm/slurm.conf
sed -i "s/ControlMachine=.*/ControlMachine=${frontend_name}/" /etc/slurm/slurm.conf
sed -i "s/^\(PartitionName.*\)/#\1/" /etc/slurm/slurm.conf
sed -i "s/^\(ReturnToService.*\)/#\1\nReturnToService=2/" /etc/slurm/slurm.conf
sed -i "s/^\(SelectType=.*\)/#\1\nSelectType=select\/linear/" /etc/slurm/slurm.conf
sed -i "s/^\(SelectTypeParameters=.*\)/#\1/" /etc/slurm/slurm.conf
sed -i "s/^\(JobCompType=jobcomp\/none\)/#\1/" /etc/slurm/slurm.conf
cat >> /etc/slurm/slurm.conf << EOFslurm
PartitionName=demo Nodes=${compute_prefix}[${first_node}-${last_node}] Default=YES MaxTime=24:00:00 State=UP
EOFslurm

# [FRONTEND]
echo "$(date +%T) 6. Install slurm client on all compute nodes"
xdsh $compute_group_name dnf -y install ohpc-slurm-client
xdcp $compute_group_name /etc/slurm/slurm.conf /etc/slurm/slurm.conf
xdcp $compute_group_name /etc/munge/munge.key /etc/munge/munge.key

# [FRONTEND]:
echo "$(date +%T) 7. Start slurm services"
# Start munge and slurm controller on master host
systemctl enable munge
systemctl enable slurmctld
systemctl restart munge
systemctl restart slurmctld
# Start slurm clients on compute hosts
xdsh $compute_group_name systemctl enable munge
xdsh $compute_group_name systemctl enable slurmd
xdsh $compute_group_name systemctl restart munge
xdsh $compute_group_name systemctl restart slurmd
# Update compute node's state as Idle
scontrol update NodeName=${compute_prefix}[${first_node}-${last_node}] State=Idle

echo "$(date +%T) 8. Check nodes's information"
sinfo
sinfo -N --long