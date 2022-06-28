# Kubeflow

[![](https://img.shields.io/badge/Kubeflow-v1.5.0--rc.0-informational)](https://github.com/kubeflow/manifests/releases/tag/v1.5.0-rc.0)

This playbook provides a core kubeflow installation. Specific components are removed (Notebooks, KNative, KFServing) as they are unused in our lab, but can be added back in by modifying the `files/kubeflow/kustomization.yaml`.

## Requirements

- Istio must be installed prior to running these playbooks
- Dex is currently installed with this playbook, take care to ensure no OIDC conflicts until Dex can be separated as a service
- `files/kubeflow/manifests` should contain files; run `git submodule update --init --recursive --remote` if they are missing.

## Installation

The core playbook runs locally using the `ops` initialized configuration.

```bash
# Cluster should first be initialized using: `ops init <cluster>`
ansible-playbook kubeflow.yml --extra-vars "run_option=install"
```

## Uninstallation

```bash
# Cluster should first be initialized using: `ops init <cluster>`
ansible-playbook kubeflow.yml --extra-vars "run_option=uninstall"
```

## Notes

- Individual configurations can be inspected with kubctl using `kubectl kustomize <path>`
- Individual targets can be directly applied using `kubectl apply -k <path>`
- Quick inspection can be done using port forwarding: `kubectl port-forward svc/istio-ingressgateway -n istio-system --address 0.0.0.0 5901:80`


## WIP: Deployment
- Dex IDP (HAS CHANGES)
- OIDC AuthService (HAS CHANGE FOR FUTURE DEPRECATION)
- Pipelines (HAS CHANGE; BUT THIS SEEMS TO BE A BUG OR INCOMPLETE 1.22 SUPPORT)
	NOTE: upstream/base/installs/multi-user/istio-authorization-config.yaml: ml-pipeline security is disabled...should be fixed
- Central dashboard (Modified for deployment)
- Admission webhook (HAS CHANGES)
- Tensorboard controller (HAS CHANGES)
- MPI Operator (README section should be deleted upstream...)
- Default User Namespace (ns: `kubeflow-user-example-com`, un: `user@example.com`, pw: `12341234` )

TODO: expose endpoint
- staging files need to be manually deleted from nuc-03:/tmp
