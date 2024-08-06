### Horizontal Pod Autoscaling Simulation
We simulated horizontal pod autoscaling behavior to find out the target CPU utilization. This directory contains the code to generate the simulated data.

Usage
``console
python3 hpa-simulations.py --desired_metric_starting 50 --current_replicas 8 --repeat_simulation 20
``

