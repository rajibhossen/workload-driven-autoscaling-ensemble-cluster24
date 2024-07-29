# Static Setup with Flux and Laghos
Full Autoscaling means we will deploy the cluster with 8 instance and we will enable horizontal pod autoscaling and cluster autoscaling.

Deploy the EKS cluster using the below command for each application. 
Make sure you provided `8` in the `managedNodeGroups` `desiredCapacity` field, and a relatively larger number in `maxSize` field for horizontal pod autoscaling to work. 

```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```

Deploy the flux operator
```console
kubectl apply -f flux-operator-arm.yaml
```

Crate a namespace for the miniCluster. Provide appropriate size in the `size` field. Populate `maxSize` field in the minicluster
and provide a larger value to enable HPA to increase pods. 
```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-laghos.yaml
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
kubectl cp -n flux-operator scripts/run-experiments-laghos.py ${POD}:/opt/laghos/run-experiments.py -c flux-sample
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

Collect experiment data from kubernetes pods
```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-mb977:/home/flux/laghos-$i-info.json datasets/workload-driven-2/laghos-$i-info.json -c flux-sample; done
```