import csv
import math
import os
import subprocess
import json
import pandas as pd
from datetime import datetime
import enum


class SoftwareTypes(enum.Enum):
    Package = 0
    Library = 1
    Service = 2
    Script = 3
    Error = 4


def return_type(string_with_type):
    if "package" in string_with_type:
        return SoftwareTypes.Package
    if "library" in string_with_type:
        return SoftwareTypes.Library
    if "service" in string_with_type:
        return SoftwareTypes.Service
    if "script" in string_with_type:
        return SoftwareTypes.Script
    return SoftwareTypes.Error


def get_precision_from_confusion_matrix(software_type, confusion_matrix):
    # value / sum of row
    precision = confusion_matrix[software_type.value][software_type.value] / sum(confusion_matrix[software_type.value])
    return precision


def get_recall_from_confusion_matrix(software_type, confusion_matrix):
    # value / sum of column
    sum_column = 0
    for i in range(len(confusion_matrix)):
        sum_column += confusion_matrix[i][software_type.value]
    recall = confusion_matrix[software_type.value][software_type.value] / sum_column
    return recall


def print_confusion_matrix(confusion_matrix):
    print("Confusion matrix: ")
    print("Predicted \\ Annotated labels")
    print("\t\tpackage, library, service, script")
    for x in range(len(confusion_matrix)):
        print(SoftwareTypes(x).name, end=': ')
        for y in range(len(confusion_matrix)):
            print(confusion_matrix[x][y], end='')
            print(' ', end='')
        print()


def main():
    # TODO: These should be configured separately, or set by input
    repo_path = "../../../test_repos/"
    benchmark_path = "../../evaluation/software_type/software_type_benchmark.csv"
    benchmark_summary = "../../evaluation/software_type/evaluation_summary.csv"
    benchmark_summary_scripts_precision_recall = \
        "../../evaluation/software_type/evaluation_summary_scripts_precision_recall.csv"
    benchmark_summary_scripts_ndcg = "../../evaluation/software_type/evaluation_summary_scripts_ndcg.csv"

    benchmark_df = pd.read_csv(benchmark_path)

    confusion_matrix = [[0 for x in range(4)] for x in range(4)]

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

    repos_with_error = []
    repos_with_error_script = []
    repos_with_error_script_ndcg = []
    num_repos = 0
    num_entries_script_service = 0
    total_precision_scripts = 0
    total_recall_scripts = 0
    total_ndcg_scripts = 0
    for dir_name in os.listdir(repo_path):
        print("######## Processing: " + dir_name + " Repo no. " + str(num_repos))  # repo_path
        cmd = 'inspect4py -i ' + repo_path + dir_name + " -o ../../output_dir/ -si"
        proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if not os.path.exists("../../output_dir/directory_info.json"):
            print("Error when applying code_inspector to " + dir_name + str(stderr))
            repos_with_error.append(dir_name)
            continue
        with open("../../output_dir/directory_info.json", "r") as file:
            data = json.load(file)
        file.close()
        # delete last DirInfo to avoid reading incorrect information in case of errors.
        os.remove("../../output_dir/directory_info.json")
        current_type = ""
        if 'software_type' in data.keys() and data['software_type']:
            current_type = data['software_type']
        flag = 0
        for index, row in benchmark_df.iterrows():
            if dir_name == row["repository"].split("/")[-1].strip():
                # First evaluation: type comparison
                type_benchmark = return_type(row["label"].strip())
                type_predicted = return_type(current_type)
                print("Label: %s; Predicted: %s" % (type_benchmark, type_predicted))
                # fill confusion matrix
                if type_predicted == SoftwareTypes.Error or type_benchmark == SoftwareTypes.Error:
                    print("---> ERROR extracting type for %s" % dir_name)
                    repos_with_error.append(dir_name)
                else:
                    confusion_matrix[type_predicted.value][type_benchmark.value] += 1
                    # If they are not the same, we annotate the error
                    if type_predicted != type_benchmark:
                        repos_with_error.append(dir_name)

                # Second evaluation: Precision/recall for scripts and services:
                # Also: Discounted cumulative gain on the obtained ranking
                # Do we detect all the scripts that have been annotated (and vice versa)?
                priority_1 = []
                priority_2 = []
                priority_3 = []
                try:
                    priority_1 = row["main_file_paths_1"].split(";")
                    priority_2 = row["main_file_paths_2"].split(";")
                    priority_3 = row["main_file_paths_3"].split(";")
                except:
                    pass
                # precision/recall are calculated per entry, and averaged at the end.
                if len(priority_1) > 0:
                    num_entries_script_service += 1
                    tp_entry = 0
                    software_invocation_entries = data["software_invocation"]
                    relevance_for_entry = []
                    penalization = 0  # to measure if our ranking is too optimistic
                    for entry in software_invocation_entries:
                        try:
                            entry_file = entry["run"].split(dir_name+"/")[-1]
                        except:
                            try:
                                entry_file = entry["import"].split(dir_name + "/")[-1]
                            except:
                                print("Entry does not have import or run keys")
                        # is the file found in the target list? (precision/recall)
                        # Calculating relevance of the ranking for DCG.
                        # We calculate relevance by comparing against the annotated ranking.
                        # This only works if the ranking is sorted in ascending order.
                        if entry_file in priority_1:
                            tp_entry += 1
                            if entry["ranking"] != 1:
                                penalization += 1
                            relevance_for_entry.append(1)
                        elif entry_file in priority_2:
                            tp_entry += 1
                            if entry["ranking"] != 2:
                                penalization += 1
                            relevance_for_entry.append(2)
                        elif entry_file in priority_3:
                            tp_entry += 1
                            if entry["ranking"] != 3:
                                penalization += 1
                            relevance_for_entry.append(3)
                        else:
                            # If the element is not found, we state we did not find an element
                            # DCG does not penalize this, but we do prec/recall to compensate.
                            # Warning: dcg may vary depending on the position where the element is found.
                            relevance_for_entry.append(0)
                    relevance_for_entry = invert_scores(relevance_for_entry)
                    ideal_relevance_for_entry = sorted(relevance_for_entry, reverse=True)
                    dcg_entry = discounted_cumulative_gain(relevance_for_entry, len(relevance_for_entry))
                    idcg_entry = discounted_cumulative_gain(ideal_relevance_for_entry, len(ideal_relevance_for_entry))
                    # Normalized dcg score
                    if dcg_entry != 0:
                        ndcg_score_entry = dcg_entry/idcg_entry
                    else:
                        # If none of the files are found, the dcg will be zero
                        ndcg_score_entry = 0
                    if ndcg_score_entry < 1:
                        repos_with_error_script_ndcg.append(dir_name +
                                                            ". ndcg:" + str(ndcg_score_entry) +
                                                            ". relevance: " +
                                                            str(relevance_for_entry))
                    if penalization > 0 and ndcg_score_entry == 1:
                        repos_with_error_script_ndcg.append(dir_name +
                                                            ". PENALIZATION: " + str(penalization))

                    # software invocation entries contain all the predictions from code_inspector
                    precision_entry = tp_entry / len(software_invocation_entries)
                    # the priority lists contain all annotated scripts
                    recall_entry = tp_entry / (len(priority_1) + len(priority_2) + len(priority_3))
                    if recall_entry > 1:  # To cope for the fact that 2 scripts may have the same name
                        recall_entry = 1
                    if precision_entry < 1 or recall_entry < 1:
                        repos_with_error_script.append(dir_name + "P:" + str(precision_entry) + ". R:" +
                                                       str(recall_entry))
                    total_precision_scripts += precision_entry
                    total_recall_scripts += recall_entry
                    total_ndcg_scripts += ndcg_score_entry
                flag = 1
                num_repos += 1

        if not flag:
            print("--> ATTENTION! %s NOT FOUND in CSV (may not be a problem) " % dir_name)

    # Print confusion matrix (software type evaluation)
    print_confusion_matrix(confusion_matrix)

    # Print average precision/recall for scripts and services detection
    average_precision_scripts = total_precision_scripts / num_entries_script_service
    average_recall_scripts = total_recall_scripts / num_entries_script_service
    print("Average precision for scripts: ", average_precision_scripts)
    print("Average recall for scripts: ", average_recall_scripts)

    # Print average ndgc score
    average_ndcg_score = total_ndcg_scripts / num_entries_script_service
    print("Average normalized discounted cumulative score for script and service ranking: ", average_ndcg_score)

    # Create evaluation_summary (software type evaluation)
    write_header = False
    if not os.path.exists(benchmark_summary):
        write_header = True

    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(date)
    with open(benchmark_summary, 'a') as summary:
        writer = csv.writer(summary, delimiter=',')
        if write_header:
            writer.writerow(
                ['date', '#repositories',
                 'precision_package', 'recall_package',
                 'precision_library', 'recall_library',
                 'precision_service', 'recall_service',
                 'precision_script', 'recall_script',
                 'precision_avg', 'recall_avg',
                 'errors'])
        p_package = get_precision_from_confusion_matrix(SoftwareTypes.Package, confusion_matrix)
        r_package = get_recall_from_confusion_matrix(SoftwareTypes.Package, confusion_matrix)
        p_library = get_precision_from_confusion_matrix(SoftwareTypes.Library, confusion_matrix)
        r_library = get_recall_from_confusion_matrix(SoftwareTypes.Library, confusion_matrix)
        p_service = get_precision_from_confusion_matrix(SoftwareTypes.Service, confusion_matrix)
        r_service = get_recall_from_confusion_matrix(SoftwareTypes.Service, confusion_matrix)
        p_script = get_precision_from_confusion_matrix(SoftwareTypes.Script, confusion_matrix)
        r_script = get_recall_from_confusion_matrix(SoftwareTypes.Script, confusion_matrix)
        p_avg = (p_package + p_library + p_service + p_script) / 4
        r_avg = (r_package + r_library + r_service + r_script) / 4
        writer.writerow([date, num_repos,
                         p_package, r_package,
                         p_library, r_library,
                         p_service, r_library,
                         p_script, r_script,
                         p_avg, r_avg, repos_with_error
                         ])

        # Write second eval (precision, recall)
        write_header = False
        if not os.path.exists(benchmark_summary_scripts_precision_recall):
            write_header = True

        with open(benchmark_summary_scripts_precision_recall, 'a') as summary_part_2:
            writer = csv.writer(summary_part_2, delimiter=',')
            if write_header:
                writer.writerow(
                    ['date', '#repositories',
                     'precision_avg', 'recall_avg',
                     'errors'])
            writer.writerow([date, num_entries_script_service,
                             average_precision_scripts,
                             average_recall_scripts,
                             repos_with_error_script])

        # Write normalized discounted cumulative gain eval (ndcg score)
        write_header = False
        if not os.path.exists(benchmark_summary_scripts_ndcg):
            write_header = True

        with open(benchmark_summary_scripts_ndcg, 'a') as summary_part_3:
            writer = csv.writer(summary_part_3, delimiter=',')
            if write_header:
                writer.writerow(
                    ['date', '#repositories',
                     'ndcg_avg', 'errors'])
            writer.writerow([date, num_entries_script_service,
                             average_ndcg_score,
                             repos_with_error_script_ndcg])


def discounted_cumulative_gain(relevance_list, p):
    """
    Method that given a list of relevant documents (in this case the ranking positions),
    calculates the discounted cumulative gain for the list at position p. In order for this measure to be effective,
    the final score should be normalized (Dividing the ideal dcg by the dcg). DCG is defined as:
    dcg_p = sum(from i=1, to p) rel_i/log2(i+1)
    :param relevance_list list of elements to consider
    :param p position to which we want to calculate the score
    """
    dcg_p = 0
    i = 1
    for element in relevance_list:
        if i <= p:
            dcg_p += element/math.log2(i+1)
            i += 1
        else:
            break
    return dcg_p


def invert_scores(input_ranking):
    """
    Function that given a ranking list, it corrects its relevance in preparation for dcg. For example,
    [1,1,2,3] --> [3,3,2,1]
    [1,2] --> [2,1]
    [1] --> [1]
    :param input_ranking ordered list with the ranking
    """
    max_value = max(input_ranking)
    relevance = []
    for i in input_ranking:
        if i == 0:
            relevance.append(i)
        else:
            relevance.append(max_value-i + 1)
    return relevance


if __name__ == "__main__":
    main()

    # minitest
    # matrix = [[17, 0, 0, 0],
    #           [5, 28, 0, 1],
    #           [0, 0, 15, 1],
    #           [1, 0, 0, 28]]
    # print_confusion_matrix(matrix)
    # print(get_precision_from_confusion_matrix(SoftwareTypes.Script, matrix))

    # minitest 2 (dcg)
    # rel = [3, 2, 3, 0, 1, 2]
    # ideal = [3, 3, 2, 2, 1, 0]
    # print(discounted_cumulative_gain(rel, len(rel)))
    # print(discounted_cumulative_gain(ideal, len(ideal)))
    # ranking = [1, 1, 2, 0, 3, 3, 3, 4]
    # print(invert_scores(ranking))
