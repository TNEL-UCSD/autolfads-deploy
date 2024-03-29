# Scaling AutoLFADS

[![](https://img.shields.io/badge/autolfads--tf2-e6aae8a-informational)](https://github.com/snel-repo/autolfads-tf2/tree/e6aae8aaa7deba2717d0c950c868b32349741258) [![](https://img.shields.io/badge/Docker-ucsdtnel%2Fautolfads-informational)](https://hub.docker.com/r/ucsdtnel/autolfads) [![DOI](https://joss.theoj.org/papers/10.21105/joss.05023/status.svg)](https://doi.org/10.21105/joss.05023)

## Introduction

This repository provides a set of solutions for running [AutoLFADS](https://github.com/snel-repo/autolfads-tf2/tree/main/lfads-tf2) in a wider variety of compute environments. This enables more users to take better advantage of the hardware available to them to perform computationally demanding hyperparameter sweeps.

![](paper/solutions.png)

We provide three options for different cluster configurations and encourage the user to select the one that best suits their needs:
- _Local Compute_: users directly leverage a container image that bundles all the AutoLFADS software dependencies and provides an entrypoint directly to the LFADS package. Interactivity with this workflow is provided via YAML model configuration files and command line arguments.
- _Unmanaged Compute (Ray)_: users configure a Ray cluster and interact with the workflow by updating YAML model configurations, updating hyperparameter sweep scripts, and then running experiment code.
- _Managed Compute (KubeFlow)_: users interact with a KubeFlow service by providing an experiment specification that includes model configuration and hyperparameter sweep specifications either as a YAML file or using a code-less UI-based workflow.

The solution matrix below provides a rough guide for identifying an suitable workflow:

|                                                   | Local Container | Ray       | KubeFlow      |
|---------------------------------------------------|-----------------|-----------|---------------|
| Number of Users                                   | 1               | 1-3       | >1            |
| Number of Jobs                                    | 1               | >1        | >1            |
| Preferred Interaction                             | CLI             | CLI       | CLI / UI      |
| Infrastructure                                    | Local           | Unmanaged | Managed/Cloud |
| Cost                                              | $               | $ - $$    | $ - $$$       |

> Details describing the AutoLFADS solutions and evaluation against the Neural Latents Benchmark datasets can be found in our [paper](paper/paper.pdf).

## Installation & Usage

Follow the appropriate guide below to run AutoLFADS on your target platform. We recommend copying the following files to your team's source control and modifying them as necessary to organize and execute custom experiments.
- Model configuration file (e.g. `examples/lorenz/data/config.yaml`)
- KubeFlow configuration file (e.g. `examples/lorenz/kubeflow_job.yaml`) or Ray run script (e.g. `examples/lorenz/ray_run.py`)

### Container

Running LFADS in a container provides isolation from your host operating system and instead relies on a system installed container runtime. This workflow is suitable for evaluating algorithm operation on _small_ datasets or exploring specific model parameter changes. It is suitable for use on shared compute environments and other platforms where there is limited system package isolation.

**Prerequisites:** Container runtime (e.g. Docker - [Linux / Mac / Windows](https://docs.docker.com/get-docker/), Podman - [Linux / Mac / Windows](https://github.com/containers/podman/releases), containerD - [Linux / Windows](https://github.com/containerd/containerd/releases)) and the [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker) (GPU only).

> Instructions are provided in docker syntax, but can be easily modified for other container runtimes


1. Specify `latest` for CPU operation and `latest-gpu` for GPU compatible operation
    ```bash
    TAG=latest
    ```
1. (OPTIONAL) Pull the docker image to your local machine. This step ensures you have the latest version of the image.
    ```bash
    docker pull ucsdtnel/autolfads:$TAG
    ```
1. Browse to a directory that has access to your data and LFADS configuration file
    ```bash
    #    The general structure should be as follows (names can be changed, just update the paths in the run parameters)
    #    \<my-data-directory>
    #       \data
    #          <data files>
    #          config.yaml (LFADS model parameter file)
    #       \output
    #          <location for generated outputs>
    cd <my-data-directory>
    ```
1. Run LFADS (bash scripts provided in `examples` for convenience)
    ```bash
    # Docker flags
    #   --rm removes container resources on exit
    #   --runtime specifies a non-default container runtime
    #   --gpus specifies which gpus to provide to the container
    #   -it start the container with interactive input and TTY
    #   -v <host location>:<container location> mount a path from host to container
    #       $(pwd): expands the terminal working directory so you don't need to type a fully qualified path
    # AutoLFADS overrides
    #   --data location inside container with data
    #   --checkpoint location inside container that maps to a host location to store model outputs
    #   --config-file location inside container that contains training configuration
    #   KEY VALUE command line overrides for training configuration

    # For CPU
    docker run --rm -it -v $(pwd):/share ucsdtnel/autolfads:$TAG \
        --data /share/data \
        --checkpoint /share/container_output \
        --config-file /share/data/config.yaml
    
    # For GPU (Note: $TAG value should have a `-gpu` suffix`)
    docker run --rm --runtime=nvidia --gpus='"device=0"' -it -v $(pwd):/share ucsdtnel/autolfads:$TAG \
        --data /share/data \
        --checkpoint /share/container_output \
        --config-file /share/data/config.yaml
    ```

### Ray

Running AutoLFADS using Ray enables scaling your processing jobs to many worker nodes in an ad-hoc cluster that you specify. This workflow is suitable for running on unmanaged or loosely managed compute resources (e.g. lab compute machines) where you have direct ssh access to the instances. It is also possible to use this workflow with *VM* based cloud environments as noted [here](https://snel-repo.github.io/autolfads/create_infra).

**Prerequisites:** Conda

#### AutoLFADS Installation

1. Clone the latest version of `autolfads-tf2`
    ```bash
    git clone git@github.com:snel-repo/autolfads-tf2.git
    ```
1. Change the working directory to the newly cloned repository
    ```bash
    cd autolfads-tf2
    ```
1. Create a new conda environment
    ```bash
    conda create --name autolfads-tf2 python=3.7
    ```
1. Activate the environment
    ```bash
    conda activate autolfads-tf2
    ```
1. Install GPU specific packages
    ```bash
    conda install -c conda-forge cudatoolkit=10.0
    conda install -c conda-forge cudnn=7.6
    ```
1. Install LFADS
    ```bash
    python3 -m pip install -e lfads-tf2
    ```
1. Install LFADS Ray Tune component
    ```bash
    python3 -m pip install -e tune-tf2
    ```
1. Modify `ray/ray_cluster_template.yaml` with the appropriate information. Note, you will need to fill in values for all `<...>` stubs.
1. Modify `ray/run_pbt.py` with the desired hyperparameter exploration configuration
1. Modify `ray/run_pbt.py` variable `SINGLE_MACHINE` to be `False`
1. Run AutoLFADS
    ```bash
    python3 ray/run_pbt.py
    ```

### KubeFlow

Running AutoLFADS using KubeFlow enables scaling your experiments across an entire cluster. This workflow allows for isolated multi-user utilization and is ideal for running on managed infrastructure (e.g. University, public or private cloud) or on service-oriented clusters (i.e. no direct access to compute instances). It leverages industry standard tooling and enables scalable compute workflows beyond AutoLFADS for groups looking to adopt a framework for scalable machine learning.

If you are using a cloud provider, KubeFlow provides a series of [tutorials](https://www.kubeflow.org/docs/started/installing-kubeflow/#install-a-packaged-kubeflow-distribution) to get you setup with a completely configured install. We currently require a [feature](https://github.com/kubeflow/katib/pull/1833) that was introduced in Katib 0.14. The below installation provides a pathway for installing KubeFlow on a _vanilla_ Kubernetes cluster integrating the noted changes.

**Prerequisites:** Kubernetes cluster access and Ansible (installed locally; only needed when deploying KubeFlow)

1. Install Istio if your cluster does not yet have it
```bash
ansible-playbook istio.yml --extra-vars "run_option=install"
```
1. Install NFS Storage Controller (if you need an [RWX](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) storage driver)
```bash
ansible-playbook nfs_storage_class.yml --extra-vars "run_option=install"
```
1. Install KubeFlow
```bash
ansible-playbook kubeflow.yml --extra-vars "run_option=install"
```
1. Use `examples/lorenz/kubeflow_job.yaml` as a template to specify a new job with desired hyperparameter exploration configuration and AutoLFADS configuration. Refer to the dataset [README](examples/README.md) for details on how to acquire and prepare the data.
1. Run AutoLFADS
    ```bash
    kubectl create -f kubeflow_job.yaml
    ```
1. (Optional) Start or monitor job using KubeFlow UI
    ```bash
    # Start a tunnel between your computer and the kubernetes network if you did not add an ingress entry
    kubectl port-forward svc/istio-ingressgateway -n istio-system --address 0.0.0.0 8080:80
    # Browse to http://localhost:8080
    ```
1. Results can be downloaded from the KubeFlow [Volumes UI](https://www.arrikto.com/blog/kubeflow/news/democratizing-the-use-of-pvcs-with-the-introduction-of-a-volume-manager-ui/) or directly from the data mount location.

## Contributing

Find a bug? Built new integration for AutoLFADS on your framework of choice? We'd love to hear about it and work with you to integrate your solution to this repository! Drop us an Issue or PR and we'd be happy to collaborate. 


## Citing

If you found this work helpful, please cite the following works:

```
@article{keshtkaran2021large,
    title = {A large-scale neural network training framework for generalized estimation of single-trial population dynamics},
    author = {Keshtkaran, Mohammad Reza and Sedler, Andrew R and Chowdhury, Raeed H and Tandon, Raghav and Basrai, Diya and Nguyen, Sarah L and Sohn, Hansem and Jazayeri, Mehrdad and Miller, Lee E and Pandarinath, Chethan},
    journal = {BioRxiv},
    year = {2021},
    publisher = {Cold Spring Harbor Laboratory}
}
@article{Patel2023, 
    doi = {10.21105/joss.05023},
    url = {https://doi.org/10.21105/joss.05023},
    year = {2023},
    publisher = {The Open Journal},
    volume = {8},
    number = {83},
    pages = {5023},
    author = {Aashish N. Patel and Andrew R. Sedler and Jingya Huang and Chethan Pandarinath and Vikash Gilja},
    title = {High-performance neural population dynamics modeling enabled by scalable computational infrastructure},
    journal = {Journal of Open Source Software}
} 
```
