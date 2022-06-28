# NFS Provisioner

[![](https://img.shields.io/badge/nfs--provisioner-v4.0.16-informational)](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/tree/nfs-subdir-external-provisioner-4.0.16)

This playbook provides a static and dynamic NFS storage provisioner for use within the cluster.

## Requirements

- Verify the specified volume mounts have suitable mount permissions from the NFS provider (e.g. Synology control panel)

## Installation

The core playbook runs locally using the `ops` initialized configuration.

```bash
# Cluster should first be initialized using: `ops init <cluster>`
ansible-playbook nfs_storage_class.yml --extra-vars "run_option=install"
```

## Uninstallation

```bash
# Cluster should first be initialized using: `ops init <cluster>`
ansible-playbook nfs_storage_class.yml --extra-vars "run_option=uninstall"
```

## WIP: Deployment
- Test should be run on installation
- Volumes should be reflected in variables specific to initialized deployment (e.g. staging, production)
