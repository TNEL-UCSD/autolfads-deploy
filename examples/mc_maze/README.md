# MC Maze

As part of the NeuralLatents competition, a set of reference datasets can be used to evaluate AutoLFADS. The core (NWB) data and tools can be downloaded from the [nlb_tools repository](https://github.com/neurallatents/nlb_tools#other-resources). To prepare the NWB formatted data, a convenient conversion utility is provided [here](https://github.com/neurallatents/nlb_tools/blob/main/examples/baselines/autolfads/lfads_data_prep.py).

## Usage

Container Runtime:

```bash
# 1. Run the bash script that starts the Docker container
bash container_run.sh
```

Ray:

```bash
# 1. Follow the instructions in the repository root README.md for setting up your AutoLFADS cluster
# 2. Review the search parameters in ray_run.py
# 3. Start the experiment:
python3 ray_run.py
```

KubeFlow:

```bash
# 1. MC Maze data should be accessible in the cluster
# 2. Review namespace, paths, parameters, etc. in kubeflow_job.yml
# 3. Start the experiment:
kubectl apply -f kubeflow_job.yml
```
