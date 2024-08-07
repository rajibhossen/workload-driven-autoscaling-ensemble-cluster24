# Study autoscaling for MPI-based ensemble applications
This repository includes code and data for experiments published in [Cluster Computing 2024](https://clustercomp.org/2024/papers/) Conference. 
The title of the paper is "Enabling Workload-Driven Elasticity in MPI-based Ensembles" with DOI - 


Directories
- [Experiments](experiments/) - This directory contains the code, scripts, and configuration files for all the experiments
  - [autoscaling-studies](experiments/autoscaling-studies) - Contains instructions, code, and configuration for main autoscaling with various applications.
  - [scaling](experiments/scaling) - Contains instructions for experiments ran with kubescaler
- [Datasets](datasets/) - This directory contains the datasets of all experiments. 
  - [autoscaling](datasets/autoscaling-studies) - Contains datasets of all autoscaling strategies with all applications
  - [horizontal pod autoscaling](datasets/horizontal-pod-autoscaling-simulation) - Simulation data for horizontal pod autoscaling 
  - [scaling](datasets/scaling) - Contains datasets for experiments conducted by kubescaler. 
- [setup](setup) - This directory contains the instructions to setup horizontal pod autoscaling and cluster autoscaling. These are for standalone setup. We provided setup instructions for these with each experiments. 

Please cite if you find it useful.

**Hossen, M. R., Sochat, V., Sarkar, A., Islam, M., & Milroy, D. (2024). Repository for workload-driven autoscaling Cluster 2024 (0.0.0). IEEE Cluster conference (Cluster), Kobe, Japan. Zenodo. https://doi.org/10.5281/zenodo.13247408**