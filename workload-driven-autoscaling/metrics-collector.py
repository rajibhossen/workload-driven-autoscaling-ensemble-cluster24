import subprocess
from kubernetes import client, config


class CustomMetrics():
    def __init__(self):
        self.api_client = None
        self.group = "custom.metrics.k8s.io"
        self.version = "v1beta2"
        self.namespace = 'flux-operator'
        self.plural = 'services'
        self.name = 'custom-metrics-service'

        self.initialize_k8s_client()

    def initialize_k8s_client(self):
        config.load_kube_config('~/.kube/config')
        self.api_client = client.CustomObjectsApi()

    def endpoint_url(self, metric_name):
        data = self.api_client.get_namespaced_custom_object(group=self.group, version=self.version,
                                                            namespace=self.namespace, plural=self.plural,
                                                            name=self.name + '/' + metric_name)
        metric_value = data['items'][0]['value']
        return metric_value

    def get_node_up_count(self):
        return self.endpoint_url('node_up_count')

# Usage
# metric_server = CustomMetrics()
# print(metric_server.get_node_up_count())

