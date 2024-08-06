# Cluster Creation 
We will create cluster without any instances. The main `kubescaler` will record timings of various components responsible for creating EKS cluster
in AWS.

```console
python k8_cluster_operations.py --node-count 0 --machine-type hpc6a.48xlarge --operation create
```

Follow this [README](https://github.com/converged-computing/kubescaler/blob/main/examples/aws/README.md) for details about metrics collected
