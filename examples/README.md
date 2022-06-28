# Data with Persistent Volumes

If you don't have a storage network solution that can connected to your KubeFlow cluster, you can copy data to a Persistent Volume Claim (PVC) using the below configuration. The top block creates the storage request (change the amount to the required value), and the bottom creates a simple shell container where you can inspect and move files around as necessary.

Copy the following to a new file:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: exp-data
  namespace: kubeflow-user-example-com
spec:
  storageClassName: external-nfs-dynamic
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 5Gi

---
apiVersion: v1
kind: Pod
metadata:
  name: exp-data-debug
  namespace: kubeflow-user-example-com
spec:
  containers:
  - name: alpine
    image: alpine:latest
    command: ['sleep', 'infinity']
    volumeMounts:
    - name: mypvc
      mountPath: /share
      readOnly: False
  volumes:
  - name: mypvc
    persistentVolumeClaim:
      claimName: exp-data
```

Create the new resources:
```bash
kubectl apply -f <filename>.yaml
```

Transfer files to remote from local:
```bash
kubectl cp -n kubeflow-user-example-com data exp-data-debug:/share
```

(Debugging) Connect to the shell container for inspecting synchronized files:
```bash
kubectl exec -it -n kubeflow-user-example-com exp-data-debug -- sh
```

(Debugging) Transfer files to local from remote:
```bash
kubectl cp -n kubeflow-user-example-com exp-data-debug:/share data
```
