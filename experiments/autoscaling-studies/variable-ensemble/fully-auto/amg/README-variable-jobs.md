# Static Setup with Flux and AMG
Full Autoscaling means we will deploy the cluster with 8 instance and we will enable horizontal pod autoscaling and cluster autoscaling.

Deploy the EKS cluster using the below command for each application. 
Make sure you provided `8` in the `managedNodeGroups` `desiredCapacity` field, and a relatively larger number in `maxSize` field for horizontal pod autoscaling to work. 

```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```

Deploy the flux operator
```console
kubectl apply -f flux-operator-refactor-arm.yaml
```

Crate a namespace for the miniCluster. Provide appropriate size in the `size` field. Populate `maxSize` field in the minicluster
and provide a larger value to enable HPA to increase pods. 
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
kubectl cp -n flux-operator run-experiments-variable-jobs.py ${POD}:/home/flux/run-experiments.py -c flux-sample
```

For static, skip the next segment
### Full Autoscaling - Horizontal Pod Autoscaling and Cluster Autoscaling
Deploy horizontal pod autoscaling by following the [readme](../horizontal-pod-autoscaling/README.md) of horizontal-pod-autoscaling directory.

Deploy Cluster Autoscaling by following the [readme](../cluster-autoscaler/README.md) of cluster-autoscaler directory. 


### Workload-Driven Autoscaling and Cluster Autoscaling
Deploy Cluster Autoscaling by following the [readme](../cluster-autoscaler/README.md) of cluster-autoscaler directory. 

For workload-driven autoscaling, the file - [workload-driven agent](../workload-driven-autoscaling/action-agent.py) is responsible for syncing with the cluster
and applying changes. We implemented the algorithm in the run-scirpts - [workload-driven algorithm](run-experiments-laghos-worload-driven.py).
To run the workload-driven autoscaling
- Make appropriate changes (yaml file location of MiniCluster in the workload-driven agent mentioned above)
- Run the agent using `python3 action-agent.py`


Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-variable-jobs-workload-driven.py ${POD}:/home/flux/run-experiments.py -c flux-sample
```

### Application running

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

Numpy is required to run dynamic size experiment. To Install numpy with python3.10, at first install latest pip and then install numpy
```pycon
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install scipy
```

Test run
```console
flux submit  -N 8 -n 512 --quiet -opmi=pmix --watch -vvv amg -P 16 8 4 -n 160 145 75
```

Run the launcher program to run ensemble workflows with chosen parameters

Variable jobs 
```
python3.10 run-experiments.py --outdir /home/flux --workdir /home/flux/examples/reaxff/HNS --times 20 -N 8 --tasks 512
```

Get each job information from the main broker pod
```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/flux/amg-$i-info.json /datasets/experiment-name-no/amg-$i-info.json -c flux-sample; done
```