"""
Very simple class to test out the test_dir method.
Note: this assumes that the ../test_repos/ repo exist.
"""
import os
import subprocess
import json
import pandas as pd

repo_path = "../test_repos/"
benchmark_path = "main_command/execution_commands_python_benchmark.csv"

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
num_total = benchmark_df.shape[0] # rows
details = {}
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
        #print(dirname+" "+str(data['software_invocation']))
        #print(str(data['software_invocation']))
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

    for index,row in benchmark_df.iterrows():
        if dir_name in row["repository"]:

            row_type = row["type"].strip()
            if row_type in current_type:
                num_correct += 1
                #print("## CORRECT type for " + dir_name)
            else:
                print("## ERROR type for %s: infer type [%s] - real type [%s]" %(dir_name, current_type, row_type))
                print("## ERROR TOTAL INFO INFERRED for %s - %s" %(dir_name, software_inf))

print("Accuracy: " + str(num_correct) + " out of " + str(num_total) + ". "+ str(num_correct/num_total))
