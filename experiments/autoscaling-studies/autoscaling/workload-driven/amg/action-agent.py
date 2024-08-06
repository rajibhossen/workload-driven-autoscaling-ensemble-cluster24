import subprocess
import time

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


def get_current_node_count():
    subprocess.run(['kubectl', 'cp', '-n', 'flux-operator', 'flux-sample-0-2dn29:/home/node_counts.txt',
                    'current_node_count.txt', '-c', 'flux-sample'])

    with open('current_node_count.txt', 'r') as f:
        current_node = f.read()
        return current_node


if __name__ == '__main__':
    prev_count = None
    yaml_filename = 'minicluster-amg.yaml'

    while True:
        current_node = get_current_node_count()

        if int(current_node) == -500:
            print("Experiment complete")
            break

        print("Received Current Node Count - ", current_node)
        if not prev_count or current_node > prev_count:
            print('Applying changes')
            # Changing size parameter in minicluster yaml
            utils.change_minicluster_size(filename=yaml_filename, value=int(current_node))
            # Applying the minicluster yaml using kubernetes API
            perform_scaling_operation(filename=yaml_filename)
            prev_count = current_node
        print("Waiting...")
        time.sleep(110)  # AMG median runtime
