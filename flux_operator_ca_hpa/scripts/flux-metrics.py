try:
    import flux
    import flux.job
    import flux.resource
except ImportError:
    exit()

# Keep a global handle so we make it just once
handle = flux.Flux()


def get_queue_metrics():
    """
    Update metrics for counts of jobs in the queue

    See https://github.com/flux-framework/flux-core/blob/master/src/common/libjob/job.h#L45-L53
    for identifiers.
    """
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
        # print(jobinfo)
        # User friendly string from integer
        jobinfo = jobinfo["job"]
        state = jobinfo["state"]
        if state == 8:
            pending_jobs += 1

        # print(jobs['id'], flux.job.info.statetostr(state))
    return pending_jobs


def main():
    job_runtime = 120  # 120 seconds on average
    estimated_node_uptime = 250  # in seconds from aws to kubernetes
    max_allowable_nodes = 50

    jobs_in_queue = get_queue_metrics()

    print(jobs_in_queue)

    estimated_total_job_runtime = job_runtime * jobs_in_queue

    current_nodes = 1
    while True:
        if (
            (estimated_total_job_runtime - estimated_node_uptime) / current_nodes
        ) > estimated_node_uptime:
            current_nodes += 1
        else:
            break

    if current_nodes * 8 > max_allowable_nodes:
        print(int(max_allowable_nodes / current_nodes))
    else:
        print(current_nodes)

    # perform kubernetes scaling operation on the minicluster


if __name__ == "__main__":
    main()
