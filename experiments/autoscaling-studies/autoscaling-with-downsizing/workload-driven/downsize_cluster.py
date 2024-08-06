import json
import subprocess
import ast
import time
from pathlib import Path
from kubernetes import client, config
import boto3


def delete_instances():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    ec2 = boto3.client('ec2')
    autoscaling_client = boto3.client(('autoscaling'))
    previous = ""
    while True:
        subprocess.run(['kubectl', 'cp', '-n', 'flux-operator', 'flux-sample-0-gfh5p:/home/hostname_for_deletion.txt',
                        'hostname_for_deletion.txt', '-c', 'flux-sample'])
        my_file = Path('hostname_for_deletion.txt')
        pod_host_mapping = {}
        pods_set = set()
        if my_file.is_file():
            with open(my_file) as f:
                x = f.read()
                if previous and previous == x:
                    continue
                previous = x
                line = ast.literal_eval(x)
                for pod_ip in line:
                    pods_set.add(pod_ip)
                hosts = v1.list_namespaced_pod(namespace='flux-operator')
                for pod in hosts.items:
                    if pod.status.pod_ip in pods_set:
                        pod_host_mapping[pod.status.pod_ip] = pod.status.host_ip

                for pod, host in pod_host_mapping.items():
                    response = ec2.describe_instances(
                        Filters=[{
                            'Name': 'network-interface.addresses.private-ip-address',
                            'Values': [host]
                        }]
                    )
                    instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
                    print(instance_id)
                    command = autoscaling_client.terminate_instance_in_auto_scaling_group(InstanceId=instance_id,
                                                                                          ShouldDecrementDesiredCapacity=True)
                    print(command)
                    # instance_id = subprocess.run(["aws", "ec2", "describe-instances", "--filters", "Name=private-ip-address,Values=", str(host), "--query", "'Reservations[*].Instances[*].[InstanceId]'", "--output", "text"], stdout=subprocess.PIPE)
                    # print(pod,host,instance_id.stdout.decode('utf-8'))
        time.sleep(30)


delete_instances()
