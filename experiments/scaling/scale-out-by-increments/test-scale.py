#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time

from kubescaler.scaler.aws import EKSCluster
from kubescaler.utils import read_json

# Save data here
here = os.path.dirname(os.path.abspath(__file__))

# Create data output directory
data = os.path.join(here, "data")


def get_parser():
    parser = argparse.ArgumentParser(
        description="K8s Scaling Experiment Runner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "cluster_name", nargs="?", help="Cluster name suffix", default="flux-cluster"
    )
    parser.add_argument(
        "--outdir",
        help="output directory for results",
        default=data,
    )
    parser.add_argument(
        "--experiment", help="Experiment name (defaults to script name)", default=None
    )
    parser.add_argument(
        "--start-iter", help="start at this iteration", type=int, default=0
    )
    parser.add_argument(
        "--end-iter", help="end at this iteration", type=int, default=3, dest="iters"
    )
    parser.add_argument(
        "--max-node-count", help="maximum node count", type=int, default=3
    )
    parser.add_argument(
        "--min-node-count", help="minimum node count", type=int, default=0
    )
    # temporarily starting with 0 nodes
    parser.add_argument(
        "--start-node-count",
        help="start at this many nodes and go up",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--machine-type", help="AWS machine type", default="hpc6a.48xlarge"
    )
    parser.add_argument(
        "--eks-nodegroup",
        action="store_true",
        help="set this to use eks nodegroup for instances, otherwise, it'll use cloudformation stack",
        default=False,
    )
    parser.add_argument(
        "--increment", help="Increment by this value", type=int, default=1
    )
    parser.add_argument(
        "--down", action="store_true", help="Test scaling down", default=False
    )
    return parser


def main():
    """
    This experiment will test scaling a cluster, three times, each
    time going from 2 nodes to 32. We want to understand if scaling is
    impacted by cluster size.
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

    # Shared tags for logging and output
    if args.down:
        direction = "decrease"
        tag = "down"
    else:
        direction = "increase"
        tag = "up"

    # Update cluster name to include tag and increment
    experiment_name = f"{experiment_name}-{tag}-{args.increment}"
    print(f"📛️ Experiment name is {experiment_name}")

    # Prepare an output directory, named by cluster
    outdir = os.path.join(args.outdir, experiment_name, args.machine_type, cluster_name)
    if not os.path.exists(outdir):
        print(f"📁️ Creating output directory {outdir}")
        os.makedirs(outdir)

    # Define stopping conditions for two directions
    def increase_by(node_count):
        # If we are greater than or equal to max node count,
        # return 0 to indicate no more scaling
        if node_count >= args.max_node_count:
            return 0

        # If we still have more than the iteration size,
        # allow an iteration of that size. This must be LESS THAN
        if node_count + args.increment < args.max_node_count:
            return args.increment

        # Temporary workaround to not exceed the max and only scale up by increment
        if node_count + args.increment > args.max_node_count:
            return 0

        # Otherwise, return the difference (the largest step we can take)
        return args.max_node_count - node_count

    # aka, "greater than min" which has to be zero
    def decrease_by(node_count):
        # If we've gone into the negative (or hit it) no more reducing
        if node_count <= 0:
            return 0

        # If we can go down the iteration size, allow it
        if node_count - args.increment >= 0:
            return args.increment

        # Finally, allow whatever is left over!
        return node_count

    # Update cluster name to include experiment name
    cluster_name = f"{experiment_name}-{cluster_name}"
    print(f"📛️ Cluster name is {cluster_name}")

    # Create 10 clusters, each going up to 32 nodes
    for iter in range(args.start_iter, args.iters):
        results_file = os.path.join(outdir, f"scaling-{iter}.json")

        # Start at the max if we are going down, otherwise the starting count
        node_count = args.max_node_count if args.down else args.start_node_count
        print(
            f"⭐️ Creating the initial cluster, iteration {iter} with size {node_count}..."
        )
        cli = EKSCluster(
            name=cluster_name,
            node_count=node_count,
            machine_type=args.machine_type,
            min_nodes=args.min_node_count,
            max_nodes=args.max_node_count,
            eks_nodegroup=args.eks_nodegroup,
        )
        # Load a result if we have it
        if os.path.exists(results_file):
            result = read_json(results_file)
            cli.times = result["times"]

        # Create the cluster (this times it)
        cli.create_cluster()
        print(f"📦️ The cluster has {cli.node_count} nodes!")

        # Flip between functions to decide to keep going based on:
        # > 0 (we are decreasing from the max node count)
        # <= max nodes (we are going up from a min node count)
        next_increment = increase_by
        if args.down:
            next_increment = decrease_by

        # Continue scaling until we reach stopping condition
        # We just call this once to enter the loop (or not)
        increment = next_increment(node_count)

        # Keep going while increment is not 0!
        while increment:
            old_size = node_count

            # Are we doing down or up?
            if args.down:
                node_count -= increment
            else:
                node_count += increment

            print(
                f"⚖️ Iteration {iter}: scaling to {direction} by {increment}, from {old_size} to {node_count}"
            )

            # Scale the cluster - we should do similar logic for the GKE client (one function)
            start = time.time()
            cli.scale(node_count)
            end = time.time()
            seconds = round(end - start, 3)
            cli.times[f"scale_{tag}_{old_size}_to_{node_count}"] = seconds
            print(
                f"📦️ Scaling from {old_size} to {node_count} took {seconds} seconds, and the cluster now has {cli.node_count} nodes!"
            )

            # Save the times as we go
            print(json.dumps(cli.data, indent=4))
            cli.save(results_file)
            increment = next_increment(node_count)

        # Delete the cluster and clean up
        print(f"⚔️ Deleting the cluster - {cluster_name}")
        cli.delete_cluster()
        print(json.dumps(cli.data, indent=4))
        cli.save(results_file)


if __name__ == "__main__":
    main()