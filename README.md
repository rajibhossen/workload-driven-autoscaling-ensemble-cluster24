# Study autoscaling for MPI-based ensemble applications
This repository includes code and data for experiments published in [Cluster Computing 2024](https://clustercomp.org/2024/papers/) Conference. 
The title of the paper is "Enabling Workload-Driven Elasticity in MPI-based Ensembles" with DOI - 


Directories
- [Experiments](experiments/) - This directory contains the code, scripts, and configuration files for all the experiments
  - [Experiments/autoscaling-studies](experiments/autoscaling-studies) - Contains instructions, code, and configuration for main autoscaling with various applications.
    - [main autoscaling](experiments/autoscaling-studies/autoscaling) - The autoscaling of all strategies (static, fully automatic, workload-driven) for all applications
    - [larger ensemble](experiments/autoscaling-studies/larger-ensemble) - The autoscaling of all strategies (static, fully automatic, workload-driven) with larger ensemble size (100 members)
  - [Experiments/scaling](experiments/scaling) - Contains instructions for experiments ran with kubescaler
- [Datasets](datasets/) - This directory contains the datasets of all experiments. 

