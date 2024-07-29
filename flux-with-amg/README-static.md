# Static Setup with Flux and Laghos
Static cluster means we will deploy the cluster with predefined instance number(8, 16, 32, 64) and we will not enable autoscaling.

We will need to setup a kubernetes cluster in aws that will have necessary supports to run an application specifically LAMMPS.
For example, AMG requires EFA enabled networking and a specific placement group.

Deploy the EKS cluster using the below command for each application. 
Make sure you provided appropriate number in the `managedNodeGroups` `desiredCapacity` field.
```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```
Deploy the flux operator
```console
kubectl apply -f flux-operator-refactor-arm.yaml
```

Crate a namespace for the miniCluster. Provide appropriate size in the `size` field. 
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
kubectl cp -n flux-operator run-experiments-amg.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments.py -c flux-sample
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

To run the launcher program to run jobs/ensemble workflows
```console
flux submit  -N 8 -n 512 --quiet -opmi=pmix --watch -vvv amg -P 16 8 4 -n 160 145 75
flux submit  -N 2 -n 128 --quiet -opmi=pmix --watch -vvv amg -P 16 4 2 -n 160 160 160
# flux mini submit  -N 8 -n 512 --quiet -ompi=openmpi@5 -c 1 -o cpu-affinity=per-task --watch -vvv lmp -v x 1 -v y 1 -v z 1 -in in.reaxc.hns -nocite

python3 run-experiments.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 lmp -v x 64 -v y 16 -v z 16 -in in.reaxc.hns -nocite
```
static job parameters for all jobs
```
python3 run-experiments.py --outdir /home/flux --workdir /home/flux/examples/reaxff/HNS --times 20 -N 8 --tasks 512 amg -P 16 8 4 -n 160 145 70
```

```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/flux/amg-$i-info.json flux-with-amg-setup/datasets/downsizing-workload-auto-1/amg-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-2-74zsh:/home/flux/amg-$i-info.json flux-with-amg-setup/datasets/large-ensemble-full-auto-1/amg-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-ktggz:/home/flux/amg-$i.log flux-with-amg-setup/datasets/no-scaling-size-16-160x145x70-1/amg-$i.log -c flux-sample; done
for i in $(seq 0 3); do kubectl cp -n flux-operator flux-sample-0-jdxpq:/home/flux/amg-$i.log flux-with-amg-setup/datasets/large-ensemble-full-auto-1/amg-$i.log -c flux-sample; done
```
Follow this [link](https://github.com/converged-computing/operator-experiments/tree/main/aws/lammps/hpc7g/run2) for more information. @
