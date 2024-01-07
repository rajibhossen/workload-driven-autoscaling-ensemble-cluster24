#!/usr/bin/env python3

import argparse
import sys
import time

from kubescaler.scaler.aws import EKSCluster


def get_parser():
    parser = argparse.ArgumentParser(
        description="K8s Cluster Creator / Destroyer!",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "cluster_name",
        default="kubernetes-flux-operator",
        help="Cluster name suffix",
        nargs="?",
    )
    parser.add_argument(
        "--experiment",
        default="hpa-ca-cluster",
        help="Experiment name (defaults to script name)",
    )
    parser.add_argument("--node-count", default=1, type=int, help="starting node count")
    parser.add_argument(
        "--max-node-count",
        default=5,
        type=int,
        help="maximum node count",
    )
    parser.add_argument(
        "--min-node-count", default=1, type=int, help="minimum node count"
    )
    parser.add_argument("--machine-type", default="m5.large", help="AWS machine type")
    parser.add_argument(
        "--operation",
        default="create",
        const="create",
        nargs="?",
        choices=["create", "delete", "scale"],
        help="create or delete Cluster",
    )
    parser.add_argument(
        "--eks-nodegroup",
        default=False,
        action="store_true",
        help="set this to use eks nodegroup for instances, otherwise, it'll use cloudformation stack",
    )
    parser.add_argument(
        "--enable-cluster-autoscaler",
        default=False,
        action="store_true",
        help="set this to enable cluster autoscaling",
    )
    return parser


def main():
    """
    Demonstrate creating and deleting a cluster. If the cluster exists,
    we should be able to retrieve it and not create a second one.
    """
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, _ = parser.parse_known_args()

    # Pull cluster name out of argument
    cluster_name = args.cluster_name

    # Derive the experiment name, either named or from script
    experiment_name = args.experiment
    if not experiment_name:
        experiment_name = sys.argv[0].replace(".py", "")
    time.sleep(2)

    # Update cluster name to include experiment name
    cluster_name = f"{cluster_name}-{experiment_name}"
    print(f"📛️ Cluster name is {cluster_name}")

    cli = EKSCluster(
        name=cluster_name,
        node_count=args.node_count,
        max_nodes=args.max_node_count,
        min_nodes=args.min_node_count,
        machine_type=args.machine_type,
        eks_nodegroup=args.eks_nodegroup,
        enable_cluster_autoscaler=args.enable_cluster_autoscaler,
    )

    if args.operation == "create":
        print(
            f"⭐️ Creating the cluster sized {args.min_node_count} to {args.max_node_count}..."
        )
        cluster_details = cli.create_cluster()
    elif args.operation == "delete":
        print("⭐️ Deleting the cluster...")
        cli.delete_cluster()
    elif args.operation == "scale":
        print(f"Adding/Removing {args.node_count} from the cluster - {cluster_name}")
        cluster_details = cli.load_cluster_info()

        if not cluster_details:
            exit()
        cli.scale(args.node_count)
    else:
        raise argparse.ArgumentError(
            args.operation, "Please specify a valid operations the cluster"
        )


if __name__ == "__main__":
    main()
