# Cluster Deletion 
We will delete the cluster that we created. The main `kubescaler` will record timings of various components responsible for deleting EKS cluster
in AWS. Normally, deletion happense in the order of creation of the cluster. 


```console
python k8_cluster_operations.py --operation delete
```

Follow this [README](https://github.com/converged-computing/kubescaler/blob/main/examples/aws/README.md) for details about metrics collected
