# Setting Up Cluster Autoscaler in EKS
Run this script to create a cluster and a nodegroup with 1 instance. The node group will have necessary tags required for cluster autoscaling.

```console
python3 create-delete-k8s-cluster.py --min-node-count 1 --max-node-count 3 --machine-type m5.large
```
or
```console
eksctl create cluster -f flux-with-lammps-setup/hpc7g-configs/eks-efa-cluster-config-hpc7g.yaml
```

Note: the eksctl yaml script will create everything needed for cluster autoscaling. So, if you creates the cluster with eksctl, skip the steps below and directly apply the cluster autoscaler.

### Create a service account for the kubernetes autoscaler.

First, create the IAM OIDC Provider for the cluster. Follow this link for more details - [Link](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html). Grab the cluster name from the output

```console
$ export cluster_name="kubernetes-flux-operator-hpa-ca-cluster"

$ oidc_id=$(aws eks describe-cluster --name $cluster_name --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5)

$ eksctl utils associate-iam-oidc-provider --cluster $cluster_name --approve
```

Create a policy for the Service Account Role

```console
$ aws iam create-policy --policy-name AmazonEKSClusterAutoscalerPolicy --policy-document file://AmazonEKSClusterAutoscalerPolicy.json
```

### Create a Role and attach the policy - Follow for [More](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html#irsa-create-role)

First, set account id and oidc_provider
```console
$ account_id=$(aws sts get-caller-identity --query "Account" --output text)

$ oidc_provider=$(aws eks describe-cluster --name $cluster_name --region $AWS_REGION --query "cluster.identity.oidc.issuer" --output text | sed -e "s/^https:\/\///")
```

Now, create role with the below command. keep a note of the role arn
```console
$ aws iam create-role --role-name AmazonEKSClusterAutoscalerRole --assume-role-policy-document file://trust-relationship.json --description "AWS Iam role for cluster autoscaler"
```

Attach the policy we created earlier.
```console
$ aws iam attach-role-policy --role-name AmazonEKSClusterAutoscalerRole --policy-arn=arn:aws:iam::$account_id:policy/AmazonEKSClusterAutoscalerPolicy
```

### Create Service Account
Create a kubernetes service account with the RoleARN. autoscaler yamls provided by AWSs already have the service account portion, you can just edit and put ROLEARN.

```yaml
---
apiVersion: v1
kind: ServiceAccount
metadata:
labels:
    k8s-addon: cluster-autoscaler.addons.k8s.io
    k8s-app: cluster-autoscaler
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::<account-id>:role/AmazonEKSClusterAutoscalerRole
  name: cluster-autoscaler
  namespace: kube-system
---
```
### Deploy the autoscaler
Finally, be sure to change the name of the cluster in the command section of cluster autoscaler container.

```console
$ kubectl apply -f cluster-autoscaler/cluster-autoscaler-autodiscover.yaml
```

Helpful Links
1. https://www.kubecost.com/kubernetes-autoscaling/kubernetes-cluster-autoscaler/
2. https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/CA_with_AWS_IAM_OIDC.md
3. https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html#irsa-create-role
4. https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/README.md
