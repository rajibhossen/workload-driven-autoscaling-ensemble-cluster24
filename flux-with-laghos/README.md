# Flux cluster setup with an application

We will need to setup a kubernetes cluster in aws that will have necessary supports to run an application specifically LAMMPS.
For example, AMG requires EFA enabled networking and a specific placement group.

Deploy the cluster using the below command

```console
eksctl create cluster -f flux-with-laghos/eks-efa-cluster-config-hpc7g.yaml

kubectl apply -f flux-with-laghos/flux-operator-arm.yaml
```

```console
kubectl create namespace flux-operator
kubectl apply -f flux-with-laghos/minicluster-laghos.yaml
```

Put flux main broker into a variable
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

This will copy configs / create directories for it
```console
kubectl cp -n flux-operator scripts/run-experiments-laghos.py ${POD}:/opt/laghos/run-experiments.py -c flux-sample
```

Now exec into the flux broker pod
```console
kubectl exec -it -n flux-operator ${POD} -- bash
```

We source the flux path, connect to running instance and verify
```console
# . /mnt/flux/flux-view.sh
. /etc/profile.d/z10_spack_environment.sh
export fluxsocket=local:///mnt/flux/view/run/flux/local
flux proxy $fluxsocket bash
flux resource list
```

To run the launcher program to run jobs/ensemble workflows
```console
flux submit -N 8 -n 512 --quiet -c 1 -o cpu-affinity=per-task --watch -vvv /opt/laghos/laghos -pa -p 1 -tf 0.6 -pt 211 -m data/cube_211_hex.mesh --ode-solver 7 --max-steps 160 --cg-tol 0 -cgm 50 -ok 3 -ot 2 -rs 4 -rp 1

python3 run-experiments.py --outdir /home/ --workdir /opt/laghos/ --times 20 -N 8 --tasks 512 /opt/laghos/laghos -pa -p 1 -tf 0.6 -pt 211 -m data/cube_211_hex.mesh --ode-solver 7 --max-steps 160 --cg-tol 0 -cgm 50 -ok 3 -ot 2 -rs 4 -rp 1
```


```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/flux/amg-$i-info.json flux-with-amg-setup/datasets/downsizing-workload-auto-1/amg-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-2-74zsh:/home/flux/amg-$i-info.json flux-with-amg-setup/datasets/large-ensemble-full-auto-1/amg-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-ktggz:/home/flux/amg-$i.log flux-with-amg-setup/datasets/no-scaling-size-16-160x145x70-1/amg-$i.log -c flux-sample; done
for i in $(seq 0 3); do kubectl cp -n flux-operator flux-sample-0-jdxpq:/home/flux/amg-$i.log flux-with-amg-setup/datasets/large-ensemble-full-auto-1/amg-$i.log -c flux-sample; done
```
Follow this [link](https://github.com/converged-computing/operator-experiments/tree/main/aws/lammps/hpc7g/run2) for more information. @
