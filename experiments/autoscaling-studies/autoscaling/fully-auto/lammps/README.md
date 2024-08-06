# Full Autoscaling Experiments with Flux and LAMMPS
Full Autoscaling means we will deploy the cluster with 8 instance and we will enable horizontal pod autoscaling and cluster autoscaling. 

Deploy the EKS cluster using the below command for each application.
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