#!/usr/bin/env python3

import argparse
import csv
import math
import random


def get_parser():
    parser = argparse.ArgumentParser(
        description="Horizontal Pod Autoscaling Desired Replica Counts simulation",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--current_replicas",
        default=8,
        type=int,
        help="The current replica count of the applicatino",
    )
    parser.add_argument(
        "--current_metric_value_low",
        default=95,
        type=int,
        help="Lowest anticipated average utilization of the PODS",
    )
    parser.add_argument(
        "--current_metric_value_high",
        default=100,
        type=int,
        help="Highest anticipated average utilization of the PODS",
    )
    parser.add_argument(
        "--desired_metric_starting",
        default=50,
        type=int,
        help="starting of desired metrics value, it will go up to 100",
    )
    parser.add_argument(
        "--repeat_simulation",
        default=20,
        type=int,
        help="Number of times to repeat the simulation",
    )
    parser.add_argument(
        "--outdir", default=None, help="Filename to write the simulation results"
    )
    return parser


def main():
    """
    Simulates Horizontal Pod Autoscaling Behavior for calculating the desired replicas with known CPU utilization
    """
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, _ = parser.parse_known_args()

    current_replicas = args.current_replicas
    current_metric_value_low = args.current_metric_value_low
    current_metric_value_high = args.current_metric_value_high
    desired_metric_value_starting = args.desired_metric_starting
    metric_upper_limit = 100

    outfile = f"hpa-simulation-cr-{current_replicas}-dm-{desired_metric_value_starting}-repeat-{args.repeat_simulation}.csv"

    with open(outfile, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["desired_metric_value", "current_metric_value", "desired_replicas"]
        )
        for i in range(args.repeat_simulation):
            for desired_metric_value in range(
                desired_metric_value_starting, metric_upper_limit + 1
            ):
                current_metric_value = random.uniform(
                    current_metric_value_low, current_metric_value_high
                )
                desiredReplicas = math.ceil(
                    current_replicas * (current_metric_value / desired_metric_value)
                )
                writer.writerow(
                    [desired_metric_value, current_metric_value, desiredReplicas]
                )


if __name__ == "__main__":
    main()
