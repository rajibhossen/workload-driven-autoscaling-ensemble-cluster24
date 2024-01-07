# Flux cluster setup with an application

We will need to setup a kubernetes cluster in aws that will have necessary supports to run an application specifically LAMMPS.
For example, LAMMPS requires EFA enabled networking and a specific placement group.

Note: For some reason, efa plugin failed with eksctl latest version. So, the current tested and working version is eksctl v0.109.0.

Deploy the cluster using the below command
```console
eksctl create cluster -f flux-with-lammps-setup/hpc7g-configs/eks-efa-cluster-config-hpc7g.yaml

kubectl apply -f flux-with-lammps-setup/hpc7g-configs/flux-operator-arm.yaml
```

```console
kubectl create namespace flux-operator
kubectl apply -f flux-with-lammps-setup/hpc7g-configs/minicluster-libfabric-new.yaml
```

This will copy configs / create directories for it
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)

kubectl cp -n flux-operator scripts/run-experiments.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments.py -c flux-sample
```

```console
kubectl exec -it -n flux-operator ${POD} -- bash
```

```console
source /etc/profile.d/z10_spack_environment.sh
asFlux="sudo -u flux -E PYTHONPATH=$PYTHONPATH -E PATH=$PATH -E FI_PROVIDER=efa -E OMPI_MCA_btl=self,ofi -E RDMAV_FORK_SAFE=1 -E FI_EFA_USE_DEVICE_RDMA=1"
. /etc/profile.d/z10_spack_environment.sh
cd /opt/spack-environment
. /opt/spack-environment/spack/share/spack/setup-env.sh
spack env activate .
cd /home/flux/examples/reaxff/HNS
```

```console
sudo -u flux -E PYTHONPATH=$PYTHONPATH -E PATH=$PATH -E HOME=/home/flux -E FI_PROVIDER=efa -E OMPI_MCA_btl=self,ofi -E RDMAV_FORK_SAFE=1 -E FI_EFA_USE_DEVICE_RDMA=1 flux proxy local:///run/flux/local bash
```

```console
flux resource list
```

```console
export FI_PROVIDER=efa
export OMPI_MCA_btl=self,ofi
export RDMAV_FORK_SAFE=1
export FI_EFA_USE_DEVICE_RDMA=1
```

To Install numpy with python3.10, at first install latest pip and then install numpy
```pycon
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install scipy
```
To run the launcher program to run jobs/ensemble workflows
```console
flux mini submit  -N 8 -n 512 --quiet -ompi=openmpi@5 -c 1 -o cpu-affinity=per-task --watch -vvv lmp -v x 1 -v y 1 -v z 1 -in in.reaxc.hns -nocite

python3 run-experiments.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 lmp -v x 64 -v y 16 -v z 16 -in in.reaxc.hns -nocite
python3 run-experiments-dynamic-size.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 -in in.reaxc.hns -nocite
```

Follow this [link](https://github.com/converged-computing/operator-experiments/tree/main/aws/lammps/hpc7g/run2) for more information. @
