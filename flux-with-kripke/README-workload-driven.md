# Workload Driven Autoscaling Setup with Flux and Kripke
Workload-Driven Autoscaling means we will deploy the cluster with 8 instance and we will utilize workload-driven autoscaling algorithm
to have autoscaling of flux pods and cluster autoscaling.

Deploy the EKS cluster using the below command for each application. 
Make sure you provided `8` in the `managedNodeGroups` `desiredCapacity` field, and a relatively larger number in `maxSize` field for workload-driven autoscaling to work. 

```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```

Deploy the flux operator
```console
kubectl apply -f flux-operator-arm.yaml
```

Crate a namespace for the miniCluster. Provide appropriate size in the `size` field. Populate `maxSize` field in the minicluster
and provide a larger value to enable workload-driven autoscaling to make changes. 
```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-kripke.yaml
```

### Application setup scripts

Put flux main broker pod id into a variable. 
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

Copy run script with workload driven algorithm that will submit ensemble application in Flux and provide cluster autoscaling node count. 
```console
kubectl cp -n flux-operator run-experiments-workload-driven.py ${POD}:/opt/Kripke/run-experiments.py -c flux-sample
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

### Workload-Driven Autoscaling and Cluster Autoscaling
Use a separate terminal to - 

Deploy Cluster Autoscaling by following the [readme](../cluster-autoscaler/README.md) of cluster-autoscaler directory. 

For workload-driven autoscaling, the file - [workload-driven agent](../workload-driven-autoscaling/action-agent.py) is responsible for syncing with the cluster
and applying changes. We implemented the algorithm in the run-scirpts - [workload-driven algorithm](run-experiments-laghos-worload-driven.py).
To run the workload-driven autoscaling
- Make appropriate changes (yaml file location of MiniCluster in the workload-driven agent mentioned above)
- Change the pod name and number in the file
- Run the agent using `python3 action-agent.py`
- Run another script to collect pods, container timings in a separate terminal - `python3.10 scripts/application_ca_hpa_metrics.py --outdir <>`
- 
### Ensemble Application Run

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
for i in $(seq 0 19); do kubectl cp flux-sample-0-gfh5p:/home/kripke-$i-info.json flux-with-kripke/datasets/experiment-name-no/kripke-$i-info.json -c flux-sample; done
```