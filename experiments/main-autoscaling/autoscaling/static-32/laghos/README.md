# Autoscaling with Static-32 cluster with Flux and Laghos
Static cluster means we will deploy the cluster with predefined instance number (32 in this case) and we will not enable autoscaling.

We will need to setup a kubernetes cluster in aws with `eksctl` that will have necessary supports to run an application specifically Laghos.

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
kubectl apply -f minicluster-laghos.yaml
```

Put flux main broker pod id into a variable. 
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-laghos.py ${POD}:/opt/laghos/run-experiments.py -c flux-sample
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
Run 20 job ensemble with Laghos
```console
python3 run-experiments.py --outdir /home/ --workdir /opt/laghos/ --times 20 -N 8 --tasks 512 /opt/laghos/laghos -pa -p 1 -tf 0.6 -pt 211 -m data/cube_211_hex.mesh --ode-solver 7 --max-steps 160 --cg-tol 0 -cgm 50 -ok 3 -ot 2 -rs 4 -rp 1
```

Collect experiment data from kubernetes pods
```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/laghos-$i-info.json datasets/experiment-name-no/laghos-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/laghos-$i.log datasets/experiment-name-no/laghos-$i.log -c flux-sample; done
```