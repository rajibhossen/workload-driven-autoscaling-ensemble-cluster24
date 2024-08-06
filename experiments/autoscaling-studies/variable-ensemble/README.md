# Variable Ensemble Experiments with various strategies

This directory contains larger ensemble autoscaling experiments with various strategies
- static (8, 16, 32, 64)
- Fully Automatic Autoscaling
- Workload Driven Autoscaling

Applications 
- AMG

Each subdirectory contains instructions to run the application with the mentioned strategy. 
The MPI-based ensemble consists of 20 jobs of application instance. The job parameters are generated on the fly with mean of 150 and standard deviation of 5.  Also, constrained the values to fall within the range
of 140 to 160 by setting the lower and upper bounds. 