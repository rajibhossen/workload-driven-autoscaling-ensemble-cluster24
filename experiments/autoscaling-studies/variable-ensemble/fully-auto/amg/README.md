# Fully automatic autoscaling setup with Flux and AMG
Full Autoscaling means we will deploy the cluster with 8 instance and we will enable horizontal pod autoscaling and cluster autoscaling.

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
kubectl apply -f minicluster-amg.yaml
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
kubectl cp -n flux-operator run-experiments-variable-parameters.py ${POD}:/home/run-experiments.py -c flux-sample
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

Numpy is required to run dynamic size experiment. If numpy is not already present, install latest pip and then install numpy
```pycon
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install scipy
```

Run jobs with variable parameter sizes
```
python3.10 run-experiments.py --outdir /home/flux --workdir /home/flux/examples/reaxff/HNS --times 20 -N 8 --tasks 512
```