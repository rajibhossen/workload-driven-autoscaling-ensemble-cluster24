# Workload Driven Autoscaling Setup with Flux and Kripke
Workload-Driven Autoscaling means we will deploy the cluster with 8 instance and we will utilize workload-driven autoscaling algorithm
to have autoscaling of flux pods and cluster autoscaling.

Deploy the EKS cluster using the below command for each application.
```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```

Deploy the flux operator
```console
kubectl apply -f flux-operator-arm.yaml
```

Crate a namespace for the miniCluster.
```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-kripke.yaml
```

### Cluster Autoscaling
Deploy Cluster Autoscaler
```console
$ kubectl apply -f cluster-autoscaler/cluster-autoscaler-autodiscover.yaml
```

Verify cluster autoscaler is working properly by checking logs
```console
kubectl get pods -n kube-system
kubectl logs -n kube-system cluster-autoscaler-xxx-xxx
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

### Ensemble Application Run

Test Run
```console
flux submit -N 8 -n 512 --quiet -c 1 -o cpu-affinity=per-task --watch -vvv kripke --groups 500 --zones 64,64,64 --procs 16,8,4
```
To run the launcher program to run jobs/ensemble workflows
```console
python3 run-experiments.py --outdir /home --workdir /opt/Kripke --times 20 -N 8 --tasks 512 kripke --groups 500 --zones 64,64,64 --procs 16,8,4
```


### Workload-Driven Autoscaling and Cluster Autoscaling
Use a separate terminal to - 
```console
kubectl get pods -n flux-operator
```
Grab the name of broker-0 pod. 

Prepare workload-driven autoscaling files
- Make appropriate changes to `action-agent.py` file
  - Change the pod name in the file `action-agent.py`
- Run the agent using `python3 action-agent.py` in a separate terminal