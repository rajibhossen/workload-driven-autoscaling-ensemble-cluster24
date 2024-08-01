# Autoscaling static (64) cluster setup with Flux and AMG
Static cluster means we will deploy the cluster with predefined instance number(64 in this case) and we will not enable autoscaling.

We will need to setup a kubernetes cluster in aws that will have necessary supports to run an application specifically Kripke.

Deploy the EKS cluster using the below command for each application.
```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```
Deploy the flux operator
```console
kubectl apply -f flux-operator-refactor-arm.yaml
```

Crate a namespace for the miniCluster.
```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-kripke.yaml
```

Put flux main broker pod id into a variable. 
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-kripke.py ${POD}:/opt/Kripke/run-experiments.py -c flux-sample
```

Now exec into the flux broker pod
```console
kubectl exec -it -n flux-operator ${POD} -- bash
```

We source the flux path, connect to running instance and verify
```console
export fluxsocket=local:///mnt/flux/view/run/flux/local
flux proxy $fluxsocket bash
flux resource list
```

Test Run
```console
flux submit -N 8 -n 512 --quiet -c 1 -o cpu-affinity=per-task --watch -vvv kripke --groups 500 --zones 64,64,64 --procs 16,8,4
```
To run the launcher program to run jobs/ensemble workflows
```console
python3 run-experiments.py --outdir /home --workdir /opt/Kripke --times 20 -N 8 --tasks 512 kripke --groups 500 --zones 64,64,64 --procs 16,8,4
```

Collect experiment data from kubernetes pods
```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-jqhm2:/home/kripke-$i-info.json datasets/experiment_name/kripke-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp flux-sample-0-ktggz:/home/flux/kripke-$i.log datasets/experiment_name/kripke-$i.log -c flux-sample; done
```