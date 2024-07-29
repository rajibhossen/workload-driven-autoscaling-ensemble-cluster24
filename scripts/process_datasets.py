import os, json
from os.path import isfile, join

import pandas as pd
from glob import glob
import statistics


def individual_time(path_to_json):
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    runtimes = []
    for file in json_files:
        with open(os.path.join(path_to_json, file)) as json_file:
            json_text = json.load(json_file)
            runtime = json_text['runtime']
            # print(runtime)
            runtimes.append(runtime)
    print("Median - ", statistics.median(runtimes))


def total_time(path_to_json):
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    minimum = float('inf')
    maximum = -float('inf')
    for file in json_files:
        with open(os.path.join(path_to_json, file)) as json_file:
            json_text = json.load(json_file)
            minimum = min(minimum, json_text['t_submit'])
            maximum = max(maximum, json_text['t_cleanup'])
    return maximum - minimum


if __name__ == '__main__':

    runtimes = []
    for i in range(3):
        path_to_json = "/Users/hossen/Projects/flux-k8s-scaler/flux-with-laghos/datasets/no-scaling-8node-" + str(i + 1) + "/"
        total = total_time(path_to_json)
        print(total)
        runtimes.append(total)

    # print(runtimes)

    # for i in range(3):
    #     path_to_json = "/Users/hossen/Projects/flux-k8s-scaler/flux-with-amg-setup/datasets/fixed-ensemble-no-scaling-size-64-160x145x70-" + str(
    #         i + 1) + "/"
    #     individual_time(path_to_json)
