# Full Autoscaling Experiments with Flux and LAMMPS
Full Autoscaling means we will deploy the cluster with 8 instance and we will enable horizontal pod autoscaling and cluster autoscaling. 

Deploy the EKS cluster using the below command for each application. 
Make sure you provided `8` in the `managedNodeGroups` `desiredCapacity` field, and a relatively larger number in `maxSize` field for horizontal pod autoscaling to work. 

```console
eksctl create cluster -f eks-efa-cluster-config-hpc7g.yaml
```

Now, install flux operator in the cluster. 
```console
kubectl apply -f flux-operator-arm.yaml
```

Crate a namespace for the miniCluster. Provide appropriate size in the `size` field. Populate `maxSize` field in the minicluster
and provide a larger value to enable HPA to increase pods. 
```console
kubectl create namespace flux-operator
kubectl apply -f minicluster-lammps.yaml
```

### Horizontal Pod Autoscaling and Cluster Autoscaling
Deploy horizontal pod autoscaling by following the [readme](../horizontal-pod-autoscaling/README.md) of horizontal-pod-autoscaling directory.

Deploy Cluster Autoscaling by following the [readme](../cluster-autoscaler/README.md) of cluster-autoscaler directory. 

### Application and run scripts
Copy run script that will submit ensemble application in Flux.
```console
POD=$(kubectl get pods -n flux-operator -o json | jq -r .items[0].metadata.name)

kubectl cp -n flux-operator run-experiments.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments.py -c flux-sample
```

Log into the broker pod
```console
kubectl exec -it -n flux-operator ${POD} -- bash
```

Source environment and variables. 
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

Verify flux can see the nodes we deploy the cluster with.
```console
flux resource list
```

```console
export FI_PROVIDER=efa
export OMPI_MCA_btl=self,ofi
export RDMAV_FORK_SAFE=1
export FI_EFA_USE_DEVICE_RDMA=1
```

Numpy is required to run dynamic size experiment. To Install numpy with python3.10, at first install latest pip and then install numpy
```pycon
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
python3.10 -m pip install scipy
```

Test run lammps application
```console
flux mini submit  -N 8 -n 512 --quiet -ompi=openmpi@5 -c 1 -o cpu-affinity=per-task --watch -vvv lmp -v x 1 -v y 1 -v z 1 -in in.reaxc.hns -nocite
```
To run the ensemble workflows with static job parameters and fixed resources
```console
python3 run-experiments.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 lmp -v x 64 -v y 16 -v z 16 -in in.reaxc.hns -nocite
```
To run ensemble workflows with dynamic job parameters and fixed resources. 
```console
python3 run-experiments-dynamic-size.py --outdir /home/flux --workdir /opt/lammps/examples/reaxff/HNS --times 20 -N 8 --tasks 512 -in in.reaxc.hns -nocite
```

Get each job information from the main broker pod
```console
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-74zsh:/home/flux/lammps-$i-info.json flux-with-lammps/datasets/experiment-no/lammps-$i-info.json -c flux-sample; done
```

Follow this [link](https://github.com/converged-computing/operator-experiments/tree/main/aws/lammps/hpc7g/run2) for more information. @