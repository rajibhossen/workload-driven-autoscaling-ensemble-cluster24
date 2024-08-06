# Scaling out in Kubernetes 
In this study, we wanted to see how various components of AWS impacts cluster creation, deletion and scaling out operations. 

The [kuberscaler](https://github.com/converged-computing/kubescaler/tree/main) repository maintains all the code to facilitate these experiments. 

Experiments
- Scale out by increments of various sizes to study scale-out policy
- Study timings of cluster creation and deletion components

Directories
- [cluster creation](cluster-creation) - contains cluster creation instructions. 
- [cluster deletion](cluster-deletion) - contains cluster deletion instructions.
- [scale out by increments](scale-out-by-increments) - contains instructions to produce the scale out operation by various increments to upto 64.

Download the repository in your local environment
```console
git clone https://github.com/converged-computing/kubescaler.git
```

Follow this [README](https://github.com/converged-computing/kubescaler/blob/main/examples/aws/README.md) for details about metrics collected
