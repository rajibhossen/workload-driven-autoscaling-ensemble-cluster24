# Dataset for main autoscaling experiments

Strategies
- Static with 8 instance
- Static with 16 instance
- Static with 32 instance
- Static with 64 instance
- fully automatic autoscaling
- workload-driven autoscaling

Applications
- Lammps
- AMG
- Kripke
- Laghos

Each experiment was run 3-5 times. In the paper, we took the median of first three runs. data are organized in the order of experiment done. 

Directory and Files
- Two csv files are representing the runtime and cost of runtime for all strategies
- [individual job runtimes](individual_job_runtimes) represent the individual job completion time. we used the median from this as an input to the workload-driven algorithm.

