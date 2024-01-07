# Horizontal Pod Autoscaling in Flux Operator Mini Cluster.

Follow this link - [Flux Operator Elasticity](https://github.com/flux-framework/flux-operator/blob/24d54d7378d35d7a28e46bcf19fc74f796536f13/docs/tutorials/elasticity.md) for details setup and latest releases. This scripts is derived from the above link. Courtesy of [@vsoch](https://github.com/vsoch)

Quick Access Link
1. [Flux Operator Elasticity](https://github.com/flux-framework/flux-operator/blob/24d54d7378d35d7a28e46bcf19fc74f796536f13/docs/tutorials/elasticity.md)

### Horizontal Autoscaler (v2) Example

The version 2 API is more flexible than version 1 in allowing custom metrics. This means we can use a [prometheus-flux](https://github.com/converged-computing/prometheus-flux)
exporter running inside of an instance to interact with it. This small set of tutorials will show setting a basic autoscaling example
based on CPU, and then one based on custom metrics.

 **[Tutorial File](https://github.com/flux-framework/flux-operator/blob/main/examples/elasticity/horizontal-autoscaler/v2-cpu/minicluster.yaml)**

Look at the scale endpoint of the MiniCluster with `kubectl` directly! Remember that we haven't installed a horizontal auto-scaler yet:

```console
$ kubectl get --raw /apis/flux-framework.org/v1alpha1/namespaces/flux-operator/miniclusters/flux-sample/scale | jq
```

```console
{
  "kind": "Scale",
  "apiVersion": "autoscaling/v1",
  "metadata": {
    "name": "flux-sample",
    "namespace": "flux-operator",
    "uid": "581c708a-0eb2-48da-84b1-3da7679d349d",
    "resourceVersion": "3579",
    "creationTimestamp": "2023-05-20T05:11:28Z"
  },
  "spec": {
    "replicas": 2
  },
  "status": {
    "replicas": 0,
    "selector": "hpa-selector=flux-sample"
  }
}
```

The above knows the selector to use to get pods (and look at current resource usage).
The output above is also telling us the `autoscaler/v1` is being used, which I used to think
means I could not use autoscaler/v2, but they seem to work OK (note that autoscaler/v2 is
installed to my current cluster with Kubernetes 1.27).

### HPA Setup
Before we deploy any autoscaler, we need a metrics server! This doesn't come out of the box with kind so
we install it:
Note: You can look at aws documentation [here](https://docs.aws.amazon.com/eks/latest/userguide/metrics-server.html)

```console
$ kubectl apply -f horizontal-pod-autoscaling/metrics-server.yaml
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

If you watch your pods (and your autoscaler and your endpoint) you'll
see first that the resource usage changes (just by way of Flux starting):
And to get it to change more, try shelling into your broker leader pod, connecting
to the broker, and issuing commands:

```bash
$ kubectl exec -it -n flux-operator flux-sample-0-p85cj bash
$ sudo -u fluxuser -E $(env) -E HOME=/home/fluxuser flux proxy local:///run/flux/local bash
$ openssl speed -multi 4
```

You'll see it change (with updates between 15 seconds and 1.5 minutes!):

```
$ kubectl get -n flux-operator hpa -w
NAME              REFERENCE                 TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
flux-sample-hpa   MiniCluster/flux-sample   0%/2%     2         4         2          33m
flux-sample-hpa   MiniCluster/flux-sample   0%/2%     2         4         2          34m
flux-sample-hpa   MiniCluster/flux-sample   3%/2%     2         4         2          34m
flux-sample-hpa   MiniCluster/flux-sample   0%/2%     2         4         3          34m
```

With the openssl command above, I got it to hit a much higher load:

```bash
flux-sample-hpa   MiniCluster/flux-sample   0%/2%          2         4         4          7m30s
flux-sample-hpa   MiniCluster/flux-sample   21%/2%         2         4         4          8m30s
flux-sample-hpa   MiniCluster/flux-sample   25%/2%         2         4         4          8m46s
flux-sample-hpa   MiniCluster/flux-sample   25%/2%         2         4         4          9m1s
```

See the [autoscaler/v1](#creating-the-v1-autoscaler) example for more detail about outputs. They have
a slightly different design, but result in the same output to the terminal.
When you are done demo-ing the CPU autoscaler, you can clean it up:

```bash
$ kubectl delete -f hpa-cpu.yaml
```
