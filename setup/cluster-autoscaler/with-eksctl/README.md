# Setting Up Cluster Autoscaler in EKS
Follow the cluster creation command with `eksctl` to setup cluster with necessary IAM permission, service accounts and OIDC providers. 

For example,
```console
eksctl create cluster -f <experiment-directory>/eks-efa-cluster-config-hpc7g.yaml
```

Deploy the autoscaler:

Change the name of the cluster in the command section of cluster autoscaler container.

```console
$ kubectl apply -f cluster-autoscaler/cluster-autoscaler-autodiscover.yaml
```

Helpful Links
1. https://www.kubecost.com/kubernetes-autoscaling/kubernetes-cluster-autoscaler/
2. https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/CA_with_AWS_IAM_OIDC.md
3. https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html#irsa-create-role
4. https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md
