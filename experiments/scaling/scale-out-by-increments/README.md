# Test Scale

Here, we conduct experiment by scaling out with various increments (4, 8, 16) upto 64 instances.

```bash
# Scale out by 4
$ python test-scale.py --increment 4 cluster-scale-out-4 --max-node-count 64 --min-node-count 0 --start-iter 0 --end-iter 5

# Scale out by 8
$ python test-scale.py --increment 8 cluster-scale-out-8 --max-node-count 64 --min-node-count 0 --start-iter 0 --end-iter 5

# Scale out by 16
$ python test-scale.py --increment 16 cluster-scale-out-16 --max-node-count 64 --min-node-count 0 --start-iter 0 --end-iter 5
```

Follow this [README](https://github.com/converged-computing/kubescaler/blob/main/examples/aws/README.md) for details about metrics collected
