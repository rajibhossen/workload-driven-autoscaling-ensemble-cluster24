# Horizontal Pod Autoscaling in Flux Operator Mini Cluster.

Follow this link - [Flux Operator Elasticity](https://github.com/flux-framework/flux-operator/blob/24d54d7378d35d7a28e46bcf19fc74f796536f13/docs/tutorials/elasticity.md) for details setup and latest releases. This scripts is derived from the above link. Courtesy of [@vsoch](https://github.com/vsoch)

Quick Access Link
1. [Flux Operator Elasticity](https://github.com/flux-framework/flux-operator/blob/24d54d7378d35d7a28e46bcf19fc74f796536f13/docs/tutorials/elasticity.md)

### Horizontal Autoscaler (v2) Example

The version 2 API is more flexible than version 1 in allowing custom metrics. This means we can use a [prometheus-flux](https://github.com/converged-computing/prometheus-flux)
exporter running inside of an instance to interact with it. This small set of tutorials will show setting a basic autoscaling example
based on CPU, and then one based on custom metrics.

 **[Tutorial File](https://github.com/flux-framework/flux-operator/blob/main/examples/elasticity/horizontal-autoscaler/v2-cpu/minicluster.yaml)**

### HPA Setup
Before we deploy any autoscaler, we need a metrics server! This doesn't come out of the box with kind so
we install it:
Note: You can look at aws documentation [here](https://docs.aws.amazon.com/eks/latest/userguide/metrics-server.html)

```console
$ kubectl apply -f metrics-server.yaml
```

I found this suggestion [here](https://gist.github.com/sanketsudake/a089e691286bf2189bfedf295222bd43). Ensure
it's running:

```bash
$ kubectl get deploy,svc -n kube-system | egrep metrics-server
```

#### Autoscaler with CPU

This first autoscaler will work based on CPU. We can create it as follows:

```console
$ kubectl apply -f horizontal-pod-autoscaling/hpa-cpu.yaml
horizontalpodautoscaler.autoscaling/flux-sample-hpa created
```

Remember that when you first created your cluster, your size was two, and we had two?

```bash
$ kubectl get -n flux-operator pods
NAME                  READY   STATUS    RESTARTS   AGE
flux-sample-0-4wmmp   1/1     Running   0          6m50s
flux-sample-1-mjj7b   1/1     Running   0          6m50s
```


Verify if horizontal pod autoscaling is working by checking utilization, targets, and replicas. 

```
$ kubectl get -n flux-operator hpa -w
NAME              REFERENCE                 TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
flux-sample-hpa   MiniCluster/flux-sample   0%/2%     2         4         2          33m
flux-sample-hpa   MiniCluster/flux-sample   0%/2%     2         4         2          34m
flux-sample-hpa   MiniCluster/flux-sample   3%/2%     2         4         2          34m
flux-sample-hpa   MiniCluster/flux-sample   0%/2%     2         4         3          34m
```

```bash
$ kubectl delete -f hpa-cpu.yaml
```
