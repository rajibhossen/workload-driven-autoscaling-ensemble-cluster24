# Larger Ensemble Application with AMG
We will perform static, fully automatic and workload-driven autoscaling with larger ensemble size(100 members) with AMG Application.
- Follow the setup guidelines for [static](README-static.md), [fully automatic](README-full-automatic.md) and [workload-driven](README-workload-driven.md)

#### For static and fully automatic

Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-amg.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments.py -c flux-sample
```

Run the larger ensemble (100 members) workflows with chosen parameters
```
python3 run-experiments.py --outdir /home/ --workdir /home/flux/ --times 100 -N 8 --tasks 512 amg -P 16 8 4 -n 160 145 70
```

#### For workload-driven

Copy run script that will submit ensemble application in Flux.
```console
kubectl cp -n flux-operator run-experiments-workload-driven.py ${POD}:/home/flux/examples/reaxff/HNS/run-experiments-workload-driven.py -c flux-sample
```
Run the larger ensemble (100 members) workflows with chosen parameters for workload-driven
```
python3 run-experiments.py --outdir /home/ --workdir /home/flux/ --times 100 -N 8 --tasks 512 amg -P 16 8 4 -n 160 145 70
```

- Follow the rest of the guidelines for static, fully automatic and workload-driven respectively.

Get each job information from the main broker pod
```
for i in $(seq 0 19); do kubectl cp -n flux-operator flux-sample-0-gfh5p:/home/flux/amg-$i-info.json /datasets/experiment-name-no/amg-$i-info.json -c flux-sample; done
```