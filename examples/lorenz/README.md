# Lorenz

The Lorenz dataset provides a toy example for evaluating AutoLFADS. The data can be downloaded from the [autolfads-tf2 repository](https://github.com/snel-repo/autolfads-tf2/blob/bdace0690cd016fd2ee1290c7ee5edbd9aec96bc/datasets/lorenz_dataset.h5).

## Usage

Container Runtime:

```bash
# 1. Replace $TAG with latest or the specific AutoLFADS image version you want to run
# 2. Start the experiment:
docker run --rm -it -v $(pwd):/share ucsdtnel/autolfads:$TAG \
        --data /share/data \
        --checkpoint /share/output \
        --config-file /share/data/config.yaml
```

> `container_run.sh` is provided as a convenience for Mac/Linux users

Ray:

```bash
# 1. Follow the instructions in the repository root README.md for setting up your AutoLFADS cluster
# 2. Review the search parameters in ray_run.py
# 3. Start the experiment:
python3 ray_run.py
```

KubeFlow:

```bash
# 1. Lorenz data should be accessible in the cluster
# 2. Review namespace, paths, parameters, etc. in kubeflow_job.yml
# 3. Start the experiment:
kubectl apply -f kubeflow_job.yml
```
