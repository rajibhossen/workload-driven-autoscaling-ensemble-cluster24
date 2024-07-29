# Flux cluster setup with an application

We will need to setup a kubernetes cluster in aws that will have necessary supports to run an application specifically LAMMPS.
For example, AMG requires EFA enabled networking and a specific placement group.

Deploy the cluster using the below command

```console
cd flux-with-kripke/
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml

kubectl apply -f flux-operator-arm.yaml
```

```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-no-view.yaml
```

Put flux main broker into a variable
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)
```

This will copy configs / create directories for it
```console
kubectl cp -n flux-operator scripts/run-experiments-amg.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments.py -c flux-sample
kubectl cp -n flux-operator scripts/run-experiments-amg-dynamic-size.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments.py -c flux-sample
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

To Install numpy with python3.10, at first install latest pip and then install numpy
```pycon
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install scipy
```

To run the launcher program to run jobs/ensemble workflows
```console
flux submit  -N 8 -n 512 --quiet -opmi=pmix --watch -vvv amg -P 16 8 4 -n 160 145 75
flux submit  -N 2 -n 128 --quiet -opmi=pmix --watch -vvv amg -P 16 4 2 -n 160 160 160
# flux mini submit  -N 8 -n 512 --quiet -ompi=openmpi@5 -c 1 -o cpu-affinity=per-task --watch -vvv lmp -v x 1 -v y 1 -v z 1 -in in.reaxc.hns -nocite

python3 run-experiments.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 lmp -v x 64 -v y 16 -v z 16 -in in.reaxc.hns -nocite
python3 run-experiments-dynamic-size.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 -in in.reaxc.hns -nocite
```
static job size
```
python3 run-experiments.py --outdir /home/flux --workdir /home/flux/examples/reaxff/HNS --times 20 -N 8 --tasks 512 amg -P 16 8 4 -n 160 145 70
```
dynamic job size
```
python3.10 run-experiments.py --outdir /home/flux --workdir /home/flux/examples/reaxff/HNS --times 20 -N 8 --tasks 512
```

```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/flux/amg-$i-info.json flux-with-amg-setup/datasets/downsizing-workload-auto-1/amg-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-2-74zsh:/home/flux/amg-$i-info.json flux-with-amg-setup/datasets/large-ensemble-full-auto-1/amg-$i-info.json -c flux-sample; done
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-ktggz:/home/flux/amg-$i.log flux-with-amg-setup/datasets/no-scaling-size-16-160x145x70-1/amg-$i.log -c flux-sample; done
for i in $(seq 0 3); do kubectl cp -n flux-operator flux-sample-0-jdxpq:/home/flux/amg-$i.log flux-with-amg-setup/datasets/large-ensemble-full-auto-1/amg-$i.log -c flux-sample; done
```
Follow this [link](https://github.com/converged-computing/operator-experiments/tree/main/aws/lammps/hpc7g/run2) for more information. @
