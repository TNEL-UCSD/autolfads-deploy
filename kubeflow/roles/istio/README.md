# Istio

[![](https://img.shields.io/badge/Istio-v1.18.6-informational)](https://istio.io/v1.18/docs/)

The service mesh for within-cluster networking and ingress/egress operations.

## Installation

_Prerequisites:_ The `istioctl` tool corresponding to the above version should be installed to `/usr/local/bin/`

Currently the provided roles install the [default profile](https://istio.io/latest/docs/setup/additional-setup/config-profiles/) using the `istioctl` tool. The following addons are also installed:

- Prometheus (TODO: this should be separated out with only the exporters present in this playbook)
- Jaeger
- Kiali

The core playbook runs locally using the `ops` initialized configuration.

```bash
# Cluster should first be initialized using: `ops init <cluster>`
ansible-playbook istio.yml --extra-vars "run_option=install"
```

## Uninstallation

> [Istio reference](https://istio.io/latest/docs/setup/getting-started/#uninstall)

```bash
# Cluster should first be initialized using: `ops init <cluster>`
ansible-playbook istio.yml --extra-vars "run_option=uninstall"
```

## Notes

- View Kiali dashboard: `istioctl dashboard kiali --address=0.0.0.0 --port 5901 --browser=false` and browse to http://localhost:5901/kiali/

- Add a namespace label to instruct Istio to automatically inject Envoy sidecar proxies when you deploy applications:

```bash
kubectl label namespace <ns> istio-injection=enabled
````
