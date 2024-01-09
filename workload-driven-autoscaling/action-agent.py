import yaml
from kubernetes import client, config, utils
import kubernetes
import utils


def apply_simple_item(dynamic_client: kubernetes.dynamic.DynamicClient, manifest: dict, verbose: bool = False):
    api_version = manifest.get("apiVersion")
    kind = manifest.get("kind")
    resource_name = manifest.get("metadata").get("name")
    namespace = manifest.get("metadata").get("namespace")
    crd_api = dynamic_client.resources.get(api_version=api_version, kind=kind)

    try:
        crd_api.get(namespace=namespace, name=resource_name)
        crd_api.patch(body=manifest, content_type="application/merge-patch+json")
        if verbose:
            print(f"{namespace}/{resource_name} patched")
    except kubernetes.dynamic.exceptions.NotFoundError:
        crd_api.create(body=manifest, namespace=namespace)
        if verbose:
            print(f"{namespace}/{resource_name} created")


def perform_scaling_operation(filename):
    config.load_kube_config('~/.kube/config')
    DYNAMIC_CLIENT = kubernetes.dynamic.DynamicClient(kubernetes.client.api_client.ApiClient())

    yaml_file_location = filename
    with open(yaml_file_location, 'r') as f:
        yaml_file = yaml.safe_load(f)
        apply_simple_item(dynamic_client=DYNAMIC_CLIENT, manifest=yaml_file, verbose=True)


utils.change_minicluster_size(filename='minicluster-libfabric-new-custom-metrics.yaml', value=3)
perform_scaling_operation(filename="minicluster-libfabric-new-custom-metrics.yaml")
