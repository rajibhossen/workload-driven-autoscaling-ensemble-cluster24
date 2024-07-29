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

### Horizontal Pod Autoscaling and Cluster Autoscaling
Deploy horizontal pod autoscaling by following the [readme](../horizontal-pod-autoscaling/README.md) of horizontal-pod-autoscaling directory.

Deploy Cluster Autoscaling by following the [readme](../cluster-autoscaler/README.md) of cluster-autoscaler directory. 


### Application and run scripts

Put flux main broker pod id into a variable. 
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-amg.py ${POD}:/home/flux/run-experiments.py -c flux-sample
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
static job size
```
python3 run-experiments.py --outdir /home/ --workdir /home/flux/ --times 20 -N 8 --tasks 512 amg -P 16 8 4 -n 160 145 70
```

Get each job information from the main broker pod
```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/flux/amg-$i-info.json /datasets/experiment-name-no/amg-$i-info.json -c flux-sample; done
```
Follow this [link](https://github.com/converged-computing/operator-experiments/tree/main/aws/lammps/hpc7g/run2) for more information. @
