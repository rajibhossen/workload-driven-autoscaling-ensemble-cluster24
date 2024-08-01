# Fully automatic autoscaling setup with Flux and Kripke
Full Autoscaling means we will deploy the cluster with 8 instance and we will enable horizontal pod autoscaling and cluster autoscaling.

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

### Horizontal Pod Autoscaling and Cluster Autoscaling
Deploy the metric server first - 
```console
kubectl apply -f horizontal-pod-autoscaling/metrics-server.yaml
```

Deploy the horizontal pod autoscaler
```console
kubectl apply -f horizontal-pod-autoscaling/hpa-cpu.yaml
```

Verify horizontal pod autoscaling is working
```console
kubectl get hpa -n flux-operator
```

Deploy Cluster Autoscaler
```console
$ kubectl apply -f cluster-autoscaler/cluster-autoscaler-autodiscover.yaml
```

Verify cluster autoscaler is working properly by checking logs
```console
kubectl get pods -n kube-system
kubectl logs -n kube-system cluster-autoscaler-xxx-xxx
```

### Application and run scripts

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
