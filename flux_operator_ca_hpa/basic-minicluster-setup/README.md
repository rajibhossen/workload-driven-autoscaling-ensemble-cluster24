# Flux Operator Mini Cluster Setup

## Basic Minicluster setup
This setup assumes you already created kubernetes cluster with at least 1/2 Nodes by following the direction [here](../README.md)

Create the flux-operator namespace and install the operator:

```bash
$ kubectl create namespace flux-operator
$ kubectl apply -f operator-minicluster/basic-configs/flux-operator.yaml
```


```bash
$ kubectl apply -f operator-minicluster/basic-configs/minicluster.yaml
```

You'll need to wait for the container to pull (status `ContainerCreating` to `Running`).
At this point, wait until the containers go from creating to running.

```bash
$ kubectl get -n flux-operator pods
NAME                  READY   STATUS    RESTARTS   AGE
flux-sample-0-4wmmp   1/1     Running   0          6m50s
flux-sample-1-mjj7b   1/1     Running   0          6m50s
```

## Flux Cluster for With LAMMPS Application

For this setup, we can not use python api, because, currently, we need placement group for lammps and boto3 api lacks the support for providing `placement group` option. So, we will use `eksctl`. If you don't have `eksctl`, please install it first.

```console
eksctl create cluster -f operator-minicluster/hpc7g-configs/eks-efa-cluster-config-hpc7g.yaml
```

This will create a cluster with managed nodegroup, oidc provider, and service account for cluster autoscaler.

Now deploy an arm version of the Flux Operator.
```console
kubectl apply -f operator-minicluster/hpc7g-configs/flux-operator-arm.yaml
```

This will create our size 1 cluster that we will be running LAMMPS on many times:
```
kubectl create namespace flux-operator
kubectl apply -f operator-minicluster/hpc7g-configs/minicluster-libfabric-new.yaml # 18.1.1
```

More to follow...
