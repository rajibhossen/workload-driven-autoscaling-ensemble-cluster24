#!/usr/bin/env python3

import argparse
import os
import threading
from datetime import datetime, timezone

from kubernetes import client as k8s
from kubernetes import config, watch

import kubescaler.utils as utils

# Save data here
here = os.path.dirname(os.path.abspath(__file__))

# Create data output directory
data = os.path.join(here, "data")


def datetime_utcnow_str():
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def str_to_datetime(datetime_str_obj):
    return datetime.strptime(datetime_str_obj, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )


def watch_for_pod_events(
    k8s_client, output_dir, namespace="flux-operator", outdir=None
):
    index = 0
    pods_for_flux = {}
    watcher = watch.Watch()
    for event in watcher.stream(
        func=k8s_client.list_namespaced_pod, namespace=namespace
    ):
        event_type = event["type"]
        # object = event["object"]  # object is one of type return_type
        raw_object = event["raw_object"]  # raw_object is a dict

        name = raw_object["metadata"]["name"]
        status = raw_object["status"]

        # temporary save all objects for inspection.
        utils.write_json(
            raw_object, os.path.join(outdir, f"{name}-{event_type}-{str(index)}.json")
        )

        if event_type == "ADDED":
            pods_for_flux[name] = {}
            pods_for_flux[name]["created"] = raw_object["metadata"]["creationTimestamp"]
            if raw_object["status"]["phase"] == "Running":
                pods_for_flux[name]["waiting_for_scheduled"] = {
                    "current_status": True,
                    "start": None,
                    "end": None,
                    "duration": None,
                }
                pods_for_flux[name]["waiting_for_container"] = {
                    "current_status": True,
                    "start": None,
                    "end": None,
                    "duration": None,
                }
            else:
                pods_for_flux[name]["waiting_for_scheduled"] = {
                    "current_status": False,
                    "start": datetime_utcnow_str(),
                    "end": None,
                    "duration": None,
                }
                pods_for_flux[name]["waiting_for_container"] = {
                    "current_status": False,
                    "start": datetime_utcnow_str(),
                    "end": None,
                    "duration": None,
                }

        elif event_type == "MODIFIED":
            for condition in status["conditions"]:
                if (
                    condition["type"] == "PodScheduled"
                    and condition["status"] == "True"
                    and (
                        not pods_for_flux[name]["waiting_for_scheduled"][
                            "current_status"
                        ]
                    )
                ):
                    pods_for_flux[name]["waiting_for_scheduled"][
                        "current_status"
                    ] = True
                    pods_for_flux[name]["waiting_for_scheduled"][
                        "end"
                    ] = datetime_utcnow_str()
                    pods_for_flux[name]["waiting_for_scheduled"]["duration"] = (
                        datetime.now(tz=timezone.utc)
                        - str_to_datetime(
                            pods_for_flux[name]["waiting_for_scheduled"]["start"]
                        )
                    ).total_seconds()
                elif condition["type"] == "Initialized":
                    pass
                elif condition["type"] == "Ready":
                    pass
                elif condition["type"] == "ContainersReady":
                    pass

            if "containerStatuses" in status.keys():
                for container_status in status["containerStatuses"]:
                    if (
                        container_status["name"] == "flux-sample"
                        and container_status["ready"] is True
                        and (
                            not pods_for_flux[name]["waiting_for_container"][
                                "current_status"
                            ]
                        )
                    ):
                        pods_for_flux[name]["waiting_for_container"][
                            "current_status"
                        ] = True
                        pods_for_flux[name]["waiting_for_container"][
                            "end"
                        ] = datetime_utcnow_str()
                        pods_for_flux[name]["waiting_for_container"]["duration"] = (
                            datetime.now(tz=timezone.utc)
                            - str_to_datetime(
                                pods_for_flux[name]["waiting_for_container"]["start"]
                            )
                        ).total_seconds()

        elif event_type == "DELETED":
            for container_status in status["containerStatuses"]:
                pods_for_flux[name]["pod_started"] = container_status["state"][
                    "terminated"
                ]["startedAt"]
                pods_for_flux[name]["pod_finished"] = container_status["state"][
                    "terminated"
                ]["finishedAt"]
                pods_for_flux[name]["pod_container_duration"] = (
                    str_to_datetime(pods_for_flux[name]["pod_finished"])
                    - str_to_datetime(pods_for_flux[name]["pod_started"])
                ).total_seconds()
        index += 1
        utils.write_json(pods_for_flux, output_dir)
        print("🫛 POD Event")


def watch_cluster_autoscaler(k8s_client, output_dir, namespace="kube-system"):
    cluster_autoscaler_pod_name = None
    response = k8s_client.list_namespaced_pod(namespace=namespace)

    for pod in response.items:
        if "cluster-autoscaler" in pod.metadata.name:
            cluster_autoscaler_pod_name = pod.metadata.name

    print("🛺 Scaler Cluster event streaming started...")
    watcher = watch.Watch()
    for log_line in watcher.stream(
        func=k8s_client.read_namespaced_pod_log,
        name=cluster_autoscaler_pod_name,
        namespace=namespace,
        follow=True,
        timestamps=True,
        since_seconds=10,
    ):
        log_line += "\n"
        utils.write_file(log_line, output_dir, mode="a")


def watch_hpa_events(autoscaling_v2, output_dir, namespace="flux-operator"):
    watcher = watch.Watch()
    event_data = []
    for event in watcher.stream(
        func=autoscaling_v2.list_namespaced_horizontal_pod_autoscaler,
        namespace=namespace,
    ):
        event_type = event["type"]
        # object = event["object"]  # object is one of type return_type
        raw_object = event["raw_object"]  # raw_object is a dict

        event_dict = {}
        event_dict["event_type"] = event_type
        event_dict["event_receive_time"] = datetime_utcnow_str()
        event_dict["spec"] = raw_object["spec"]
        event_dict["status"] = raw_object["status"]

        event_data.append(event_dict)
        utils.write_json(event_data, output_dir)
        print("↔️ ↔️ HPA Autoscaler events..")


def get_parser():
    parser = argparse.ArgumentParser(
        description="K8s Scaling Experiment Runner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--flux-namespace",
        help="Namespace of the flux operator",
        default="flux-operator",
    )
    parser.add_argument(
        "--autoscaler-namespace",
        help="Namespace of the cluster autoscaler",
        default="kube-system",
    )
    parser.add_argument(
        "--hpa-namespace",
        help="Namespace of the horizontal pod autoscaler",
        default="flux-operator",
    )
    parser.add_argument(
        "--kubeconfig",
        help="kubernetes config file name, full path if the file is not in the current directory",
        default="kubeconfig-aws.yaml",
    )
    parser.add_argument(
        "--outdir", help="Path for the experimental results", default=data
    )
    parser.add_argument(
        "--filedir", help="Directory name for the experiment", default=None
    )
    return parser


def main():
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, _ = parser.parse_known_args()

    # loading kubernetes config file and initializing client
    # config.load_kube_config(config_file=args.kubeconfig)
    config.load_kube_config()
    coreV1 = k8s.CoreV1Api()
    autoscalingV2 = k8s.AutoscalingV2Api()

    experiment_name = "kubernetes-pods-ca-hpa"
    if args.filedir:
        outdir = os.path.join(args.outdir, experiment_name, args.filedir)
    else:
        outdir = os.path.join(args.outdir, experiment_name, datetime_utcnow_str())
    if not os.path.exists(outdir):
        print(f"📁️ Creating output directory {outdir}")
        os.makedirs(outdir)

    pods_event_file = os.path.join(outdir, f"{args.flux_namespace}-pods-events.json")
    ca_events_logs = os.path.join(outdir, f"{args.autoscaler_namespace}-ca-events.logs")
    hpa_events_file = os.path.join(
        outdir, f"{args.hpa_namespace}-hpa-status-events.json"
    )

    print("🍥 Starting the threads for collecting data")

    pod_events_thread = threading.Thread(
        target=watch_for_pod_events,
        args=(coreV1, pods_event_file, args.flux_namespace, outdir),
    )
    ca_events_thread = threading.Thread(
        target=watch_cluster_autoscaler,
        args=(coreV1, ca_events_logs, args.autoscaler_namespace),
    )
    hpa_events_thread = threading.Thread(
        target=watch_hpa_events,
        args=(autoscalingV2, hpa_events_file, args.hpa_namespace),
    )

    pod_events_thread.start()
    ca_events_thread.start()
    hpa_events_thread.start()

    pod_events_thread.join()
    ca_events_thread.join()
    hpa_events_thread.join()


if __name__ == "__main__":
    main()
