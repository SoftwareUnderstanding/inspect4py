"""
Very simple class to test out the test_dir method.
Note: this assumes that the ../test_repos/ repo exist.
"""
import csv
import os
import subprocess
import json
import pandas as pd
from datetime import datetime

# TO DO: These should be configured separately
repo_path = "../test_repos/"
benchmark_path = "main_command/execution_commands_python_benchmark.csv"
# benchmark_path = "main_command/execution_commands_python_benchmark_test.csv"
benchmark_summary = "main_command/evaluation_summary.csv"

benchmark_df = pd.read_csv(benchmark_path)

if not os.path.isdir(repo_path):
    os.makedirs(repo_path)

# Download repos if they don't exist in the repo_path
for index, row in benchmark_df.iterrows():
    current_repo = "https://github.com/" + row["repository"]
    print("Downloading: " + row["repository"])
    cmd = 'cd ' + repo_path + ' && git clone ' + current_repo
    proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    # print(stderr)

# Process
num_correct = 0
num_error = 0
num_total = benchmark_df.shape[0]  # rows
num_analyses = 0
details = {}
repos_with_error = []
for dir_name in os.listdir(repo_path):
    print("######## Processing: " + dir_name)
    cmd = 'python code_inspector.py -i ' + repo_path + dir_name
    proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    req_dict = {}
    with open("output_dir/DirectoryInfo.json", "r") as file:
        data = json.load(file)
    file.close()
    current_type = "unknown"
    # This will have to be changed if software_invocation JSON definition is changed
    if 'software_invocation' in data.keys() and data['software_invocation']:
        # print(dirname+" "+str(data['software_invocation']))
        # print(str(data['software_invocation']))
        try:
            aux = data['software_invocation']['0']
            current_type = aux["type"]
            software_inf = aux
        except:
            try:
                current_type = data['software_invocation']["type"]
                software_inf = data['software_invocation']
            except:
                current_type = data['software_invocation']
                software_inf = data['software_invocation']
    flag = 0
    for index, row in benchmark_df.iterrows():
        if dir_name == row["repository"].split("/")[-1].strip():
            row_type = row["type"].strip()
            if row_type in current_type:
                num_correct += 1
            else:
                print("## ERROR type for %s: infer type [%s] - real type [%s]" % (dir_name, current_type, row_type))
                print("## ERROR TOTAL INFO INFERRED for %s - %s" % (dir_name, software_inf))
                num_error += 1
                repos_with_error.append(dir_name)
            num_analyses += 1
            flag = 1
    if not flag:
        print("--> ATTENTION! %s NOT FOUND! " % dir_name)

# Create evaluation_summary.
write_header = False
if not os.path.exists(benchmark_summary):
    write_header = True

with open(benchmark_summary, 'w') as summary:
    writer = csv.writer(summary, delimiter=',')
    if write_header:
        writer.writerow(['date', '#repositories', 'accuracy', 'error_repos'])
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    writer.writerow([date, num_analyses, str(num_correct / num_analyses), str(repos_with_error)])


print("Accuracy: " + str(num_correct) + " out of " + str(num_analyses) + ". Num errors=" + str(num_error) + ". " + str(
    num_correct / num_analyses))
