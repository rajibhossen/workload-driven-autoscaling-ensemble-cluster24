# Workload Driven Autoscaling with Flux and Laghos
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
kubectl apply -f minicluster-laghos.yaml
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

### Application running

Put flux main broker pod id into a variable. 
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

Copy run script with workload driven algorithm that will submit ensemble application in Flux and provide cluster autoscaling node count. 
```console
kubectl cp -n flux-operator run-experiments-workload-driven.py ${POD}:/opt/laghos/run-experiments.py -c flux-sample
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

Test run
```console
flux submit -N 8 -n 512 --quiet -c 1 -o cpu-affinity=per-task --watch -vvv /opt/laghos/laghos -pa -p 1 -tf 0.6 -pt 211 -m data/cube_211_hex.mesh --ode-solver 7 --max-steps 160 --cg-tol 0 -cgm 50 -ok 3 -ot 2 -rs 4 -rp 1
```
To run the launcher program to run jobs/ensemble workflows
```console
python3 run-experiments.py --outdir /home/ --workdir /opt/laghos/ --times 20 -N 8 --tasks 512 /opt/laghos/laghos -pa -p 1 -tf 0.6 -pt 211 -m data/cube_211_hex.mesh --ode-solver 7 --max-steps 160 --cg-tol 0 -cgm 50 -ok 3 -ot 2 -rs 4 -rp 1
```

### Workload-Driven Autoscaling Action Execution
Prepare workload-driven autoscaling files
- Change the pod name in the file `action-agent.py`
- Make sure the yaml location is pointing to this directory minicluster file
- Run the agent using `python3 action-agent.py` in a separate terminal
