# Setup Kubernetes Cluster with Cluster Autoscaling

## Deploy the cluster
This file creates/deletes/scales a EKS Cluster. The nodes are managed by both EKS Nodegroup and Cloudformation Stacks.

```
python3 k8s_cluster_operations.py -h
positional arguments:
  cluster_name          Cluster name suffix

optional arguments:
  -h, --help            show this help message and exit
  --experiment EXPERIMENT
    Experiment name (defaults to script name)

  --node-count NODE_COUNT
    starting node count of the cluster

  --max-node-count MAX_NODE_COUNT
    maximum node count

  --min-node-count MIN_NODE_COUNT
    minimum node count

  --machine-type MACHINE_TYPE
    AWS EC2 Instance types

  --operation [{create,delete,scale}]
    Define which operation you want to perform, If you want to scale, be sure to increase the NODE_COUNT. The cluster size will increase depending on the current instance size. if NODE_COUNT is less than the current, the cluster nodes will be scaled down.

  --eks-nodegroup
    Include this option to use eks nodegroup for instances, otherwise, it'll use cloudformation stack. EKS Nodegroup will automatically set tags in the aws autoscaling group so that cluster autoscaler can discover them.

  --enable-cluster-autoscaler
    Include this to enable cluster autoscaling. This will also create an OIDC provider for the cloud. be sure to take a note of the RoleARN that this script will print.
```

Example usage

```console
basicinsect:flux_operator_ca_hpa hossen1$ python3 k8s_cluster_operations.py --operation "create" --enable-cluster-autoscaler --eks-nodegroup
📛️ Cluster name is kubernetes-flux-operator-hpa-ca-cluster
⭐️ Creating the cluster sized 1 to 5...
🥞️ Creating VPC stack and subnets...
🥣️ Creating cluster...
The status of nodegroup CREATING
Waiting for kubernetes-flux-operator-hpa-ca-cluster-worker-group nodegroup...
Setting Up the cluster OIDC Provider
The cluster autoscaler Role ARN - arn:aws:iam::<account-id>:role/AmazonEKSClusterAutoscalerRole

⏱️ Waiting for 1 nodes to be Ready...
Time for kubernetes to get nodes - 5.082208871841431
🦊️ Writing config file to kubeconfig-aws.yaml
  Usage: kubectl --kubeconfig=kubeconfig-aws.yaml get nodes
```

## Set UP Cluster Autoscaler

Be sure to change two things in this file [cluster-autoscaler-autodiscover.yaml](cluster-autoscaler/cluster-autoscaler-autodiscover.yaml)

1. RoleARN  `arn:aws:iam::<account-id>:role/AmazonEKSClusterAutoscalerRole` in the service account portion
2. Cluster Name - `kubernetes-flux-operator-hpa-ca-cluster` in the commnds of the cluster autoscaler.

then apply the changes..
```console
kubectl --kubeconfig=kubeconfig-aws.yaml apply -f cluster-autoscaler/cluster-autoscaler-autodiscover.yaml
```

Verify cluster autoscaler is up
```console
$ kubectl --kubeconfig=kubeconfig-aws.yaml get pods -n kube-system
NAME                                  READY   STATUS    RESTARTS   AGE
aws-node-2dz6x                        1/1     Running   0          9h
aws-node-pzwl9                        1/1     Running   0          9h
cluster-autoscaler-747689d74b-6lkfk   1/1     Running   0          8h
coredns-79df7fff65-q984f              1/1     Running   0          9h
coredns-79df7fff65-tlkwc              1/1     Running   0          9h
kube-proxy-8ch5x                      1/1     Running   0          9h
kube-proxy-kq9ch                      1/1     Running   0          9h
metrics-server-7db4fb59f9-qdp2c       1/1     Running   0          7h5m
```

This will print the logs. be sure that cluster autoscaler discovered the autoscaling group and working properly.
```console
kubectl --kubeconfig=kubeconfig-aws.yaml -n kube-system logs deploy/cluster-autoscaler
```

## Run application to collect metrics
Follow this [ca_hpa_readme.md](README_CA_HPA.md) to see how to run a program that will collect metrics for horizontal pod autoscaling, cluster autoscaling
