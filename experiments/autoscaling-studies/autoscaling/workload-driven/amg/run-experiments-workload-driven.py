#!/usr/bin/env python3

import argparse
import json
import math
import os
import subprocess
import sys
import time

here = os.path.abspath(os.path.dirname(__file__))

# Basic submit and monitor / saving of logs for multiple jobs
# Submit 10 times, each on 2 nodes
# cd /opt/lammps/examples/reaxff/HNS
# python run-experiments.py --workdir /opt/lammps/examples/reaxff/HNS --tasks 2 --times 10 -N 2 lmp -v x 1 -v y 1 -v z 1 -in in.reaxc.hns -nocite --outdir /home/scohat1/etc --identifier lammps

# Make sure we can connect to the handle
try:
    import flux
    import flux.job

    handle = flux.Flux()

except ImportError:
    sys.exit("Cannot import flux, is the broker running?")


def get_parser():
    parser = argparse.ArgumentParser(
        description="Flux Basic Experiment Runner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-id", "--identifier", help="Identifier for the run", default="amg"
    )
    parser.add_argument("--workdir", help="working directory")
    parser.add_argument(
        "--outdir",
        help="output directory for logs, etc.",
        default=os.path.join(here, "data"),
    )
    parser.add_argument("-N", help="number of nodes", type=int, default=1)
    parser.add_argument(
        "--sleep", help="sleep seconds waiting for jobs", type=int, default=10
    )
    parser.add_argument("--tasks", help="number of tasks", type=int, default=1)
    parser.add_argument(
        "--times", help="Number of times to run experiment command", type=int
    )
    parser.add_argument("--index", help="Providing job number", type=int, default=0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print example command and exit",
    )
    return parser


def get_info(jobid):
    """
    Get details for a job
    """
    jobid = flux.job.JobID(jobid)
    payload = {"id": jobid, "attrs": ["all"]}
    rpc = flux.job.list.JobListIdRPC(handle, "job-list.list-id", payload)
    try:
        jobinfo = rpc.get()

    # The job does not exist!
    except FileNotFoundError:
        return None

    jobinfo = jobinfo["job"]

    # User friendly string from integer
    state = jobinfo["state"]
    jobinfo["state"] = flux.job.info.statetostr(state)

    # Get job info to add to result
    info = rpc.get_jobinfo()
    jobinfo["nnodes"] = info._nnodes
    jobinfo["result"] = info.result
    jobinfo["returncode"] = info.returncode
    jobinfo["runtime"] = info.runtime
    jobinfo["priority"] = info._priority
    jobinfo["waitstatus"] = info._waitstatus
    jobinfo["nodelist"] = info._nodelist
    jobinfo["nodelist"] = info._nodelist
    jobinfo["exception"] = info._exception.__dict__

    # Only appears after finished?
    if "duration" not in jobinfo:
        jobinfo["duration"] = ""
    return jobinfo


def get_queue_metrics():
    jobs = flux.job.job_list(handle)
    listing = jobs.get()
    # print(listing)
    pending_jobs = 0
    for jobs in listing["jobs"]:
        payload = {"id": jobs["id"], "attrs": ["all"]}
        rpc = flux.job.list.JobListIdRPC(handle, "job-list.list-id", payload)
        try:
            jobinfo = rpc.get()
        # The job does not exist, assume completed
        except FileNotFoundError:
            return "INACTIVE"

        jobinfo = jobinfo["job"]
        state = jobinfo["state"]
        if state == 8:
            pending_jobs += 1

    return pending_jobs


def calculate_node_count(override_algorithm=None):
    if override_algorithm:
        with open("node_counts.txt", "w") as f:
            f.write(str(-500))
        return

    job_runtime = 117  # 120 seconds on average
    estimated_node_uptime = 250  # in seconds from aws to kubernetes
    max_allowable_nodes = 48
    current_node_counts = 8
    jobs_in_queue = get_queue_metrics()

    print(f"Total jobs in the queue - {jobs_in_queue}")

    # estimated_total_job_runtime = job_runtime * jobs_in_queue

    adjusted_jobs = jobs_in_queue - math.ceil(estimated_node_uptime / job_runtime)

    new_nodes = adjusted_jobs * current_node_counts - current_node_counts

    if new_nodes > max_allowable_nodes:
        with open("node_counts.txt", "w") as f:
            f.write(str(max_allowable_nodes))

        # print(f"Calculated nodes are - {max_allowable_nodes}")
    else:
        with open("node_counts.txt", "w") as f:
            f.write(str(new_nodes))
        # print(f"Calculated nodes are - {new_nodes}")




def main():
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, command = parser.parse_known_args()

    # Show args to the user
    print("         N: %s" % args.N)
    print("     times: %s" % args.times)
    print(" Job Index: %s" % args.index)
    print("     sleep: %s" % args.sleep)
    print("    outdir: %s" % args.outdir)
    print("     tasks: %s" % args.tasks)
    print("   command: %s" % " ".join(command))
    print("   workdir: %s" % args.workdir)
    print("   dry-run: %s" % args.dry_run)
    print("identifier: %s" % args.identifier)

    # Ensure output directory exists
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    def get_job_prefix(i):
        identifier = f"{args.identifier}-{i}"
        return os.path.join(args.outdir, identifier)

    # Hard code options for all setups
    flux_options = [
        "-opmi=pmix",
        "-vvv",
    ]

    # Submit all jobs
    jobs = []
    for i in range(args.index, args.times + args.index):
        prefix = get_job_prefix(i)
        outfile = f"{prefix}.log"

        flux_command = (
            [
                "flux",
                # The flux in the container is 0.44.0
                "submit",
                "-N",
                str(args.N),
                "-n",
                str(args.tasks),
                "--output",
                outfile,
                "--error",
                outfile,
            ]
            + flux_options
            + command
        )

        # If doing a dry run, stop here
        print(" ".join(flux_command))
        if args.dry_run:
            continue

        job = subprocess.Popen(flux_command, stdout=subprocess.PIPE)
        jobid = job.communicate()[0]
        # jobid = subprocess.check_output(flux_command)
        jobid = jobid.decode("utf-8").strip()
        count = i + 1
        print(f"Submit {jobid}: {count} of {args.times}")
        jobs.append(jobid)

    # At this point all jobs are submit, and each should use all resources
    # so we *should* be running one at a time. Now we can wait for each to save output, etc.
    # Wait for futures
    print("\n⭐️ Waiting for jobs to finish...")
    print(f"Job ID's are - {jobs} \n")
    for i, jobid in enumerate(jobs):

        # calculate node count for semi autoscaling
        calculate_node_count()

        state = "RUN"
        while state == "RUN":
            info = get_info(jobid)
            if info and info["state"] == "INACTIVE":
                state = info["state"]
                print(
                    f"No longer waiting on job {jobid}, FINISHED {info['returncode']}!"
                )
                break
            else:
                print(
                    f"Still waiting for job {jobid} on {info['nodelist']}, has state {info['state']}"
                )
                time.sleep(args.sleep)

        # When we get here, save all the metadata
        prefix = get_job_prefix(i + args.index)
        outfile = f"{prefix}-info.json"
        with open(outfile, "w") as fd:
            fd.write(json.dumps(info, indent=4))
    calculate_node_count(override_algorithm=True)
    print("Jobs are complete, goodbye! 👋️")


if __name__ == "__main__":
    main()
