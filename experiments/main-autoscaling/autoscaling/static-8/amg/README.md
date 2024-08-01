# Autoscaling static cluster setup with Flux and AMG
Static cluster means we will deploy the cluster with predefined instance number(8 in this case) and we will not enable autoscaling.

Deploy the EKS cluster using the below command for each application. 

```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```

Deploy the flux operator
```console
kubectl apply -f flux-operator-refactor-arm.yaml
```

Crate a namespace for the miniCluster. Provide appropriate size in the `size` field. 
```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-amg.yaml
```

Put flux main broker pod id into a variable. 
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-amg.py ${POD}:/home/run-experiments.py -c flux-sample
```

Now exec into the flux broker pod
```console
kubectl exec -it -n flux-operator ${POD} -- bash
```

We source the flux path, connect to running instance and verify
```console
. /etc/profile.d/z10_spack_environment.sh
export fluxsocket=local:///mnt/flux/view/run/flux/local
flux proxy $fluxsocket bash
flux resource list
```

To run the launcher program to run jobs/ensemble workflows
```console
flux submit -N 8 -n 512 --quiet -opmi=pmix --watch -vvv amg -P 16 8 4 -n 160 145 70
flux submit  -N 2 -n 128 --quiet -opmi=pmix --watch -vvv amg -P 16 4 2 -n 160 160 160

```
static job parameters for all jobs
```
python3 run-experiments.py --outdir /home --workdir /home/ --times 20 -N 8 --tasks 512 amg -P 16 8 4 -n 160 145 70
```