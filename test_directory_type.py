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

num_correct = 0
num_total = benchmark_df.shape[0] # rows
details = {}
for dirname in os.listdir(repo_path):
    print("processing: " +dirname)
    cmd = 'python code_inspector.py -i '+ repo_path + dirname
    proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    req_dict = {}
    with open("OutputDir/DirectoryInfo.json", "r") as file:
        data = json.load(file)
    file.close()
    current_type = "unknown"
    # This will have to be changed if dir_type JSON definition is changed
    if data['dir_type']:
        # print(dirname+" "+str(data['dir_type']))
        print(str(data['dir_type']))
        try:
            aux = data['dir_type']['0']
            current_type = aux["type"]
        except:
            try:
                current_type = data['dir_type']["type"]
            except:
                current_type = data['dir_type']

    for index,row in benchmark_df.iterrows():
        if dirname in row["repository"]:

            if row["type"] in current_type:
                num_correct += 1
                print("#### CORRECT type for " + dirname)

print("Accuracy: " + str(num_correct) + " out of " + str(num_total) + ". "+ str(num_correct/num_total))