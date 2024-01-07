from scipy.stats import truncnorm


def calculate_node_count():
    job_runtime = 120  # 120 seconds on average
    estimated_node_uptime = 250  # in seconds from aws to kubernetes
    max_allowable_nodes = 50
    current_node_counts = 8
    jobs_in_queue = 19

    print(f"Total jobs in the queue - {jobs_in_queue}")

    estimated_total_job_runtime = job_runtime * (jobs_in_queue-1)

    current_nodes = 8
    # print(int((estimated_total_job_runtime)/estimated_node_uptime))
    # print(min(8*current_node_counts, max_allowable_nodes))
    parallel = 1
    while True:
        execution_time = (jobs_in_queue//parallel + min(jobs_in_queue % parallel, 1))
        # print(execution_time)
        parallel += 1
        if (execution_time*job_runtime) < estimated_node_uptime:
            print(parallel*current_node_counts)
            break

    #     if ((estimated_total_job_runtime - estimated_node_uptime) / current_nodes) > estimated_node_uptime:
    #         current_nodes += 8
    #
    #     if current_nodes > max_allowable_nodes:
    #         print(f"Calculated nodes are - {max_allowable_nodes}")
    #     else:
    #         print(f"Calculated nodes are - {current_nodes}")


