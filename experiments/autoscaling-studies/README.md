### Autoscaling studies with various strategies and applications 
Here, we describe all the experiments for autoscaling.

For the experiments, we have utilized the following applications -
- LAMMPS
- AMG
- Kripke
- Laghos

Autoscaling Strategies
- Static with various instance numbers (8, 16, 32, 64)
- Fully automatic autoscaling (Horizontal pod autoscaling + cluster autoscaling)
- Workload-Driven Autoscaling

Experiments
- [main autoscaling](autoscaling/) - Autoscaling strategies with four application in fixed ensemble jobs (20 members)
- [variable ensemble](variable-ensemble) - Autoscaling strategies with AMG application in variable ensemble jobs (20 members)
- [larger ensemble](larger-ensemble) - Autoscaling strategies with AMG application in Large ensemble jobs (100 members)
- [workload driven with downsizing](autoscaling-with-downsizing)Workload-driven and fully automatic strategies with AMG application with downsizing enabled and fixed ensemble jobs (20 members)

Monitoring

We also monitor various events and track timings in application environment such as pod schedule duration. Details are here [monitoring-and-tracking](monitoring-and-tracking-events).

Horizontal Pod Autoscaling

Simulated Horizontal pod autoscaling to identify the target cpu utilization. [This](horizontal-pod-autoscaling) contains the code for that. 