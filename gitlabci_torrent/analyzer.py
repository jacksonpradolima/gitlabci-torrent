import glob
import os

import pandas as pd


class Analyzer(object):

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.project = log_dir.split(os.sep)[-1]

    def get_number_test_cases(self, path):
        line = [line for line in open(path) if 'tests failed out of' in line]

        if len(line) > 1:
            print(f"The file {path} contains multiple lines with test results.")
            return -1

        if len(line) == 0:
            # File without test results
            return 0

        return int(line[0].split('tests failed out of')[-1])

    def get_tests(self, path):
        # To know when I started get the tests information
        valid_info = False

        # The test cases found
        tests = []
        total_duration = 0

        num_tc = self.get_number_test_cases(path)
        
        if num_tc > 0:
            tc_count = 1
            # For each line in the log
            for line in open(path, encoding="utf-8"):
                # If I am in the end of the tests
                if valid_info and 'tests failed out of' in line:
                    valid_info = False

                # If I am observing the lines of the tests
                if valid_info:
                    # Ignore line with "Start NUMBER: 'test case X'"
                    if f'{tc_count}/{num_tc}' in line and 'Test' in line:
                        tc_count += 1

                        temp_line = line.strip().split(":")
                        if len(temp_line) > 2:
                            # For instance, when we have Exception status
                            temp_line[1] = ' '.join(temp_line[1:])
                            del temp_line[-1]

                        info = [x.strip() for x in temp_line]
                        info = info[-1].split(" ")
                        
                        print(line)

                        if 'Failed' in line or 'Timeout' in line or 'Not Run' in line or 'Exception' in line or 'Skipped' in line:
                            # When the test case status is Failed or Timeout it
                            # is in other position
                            status = info[1].split('***')[-1]
                        else:
                            status = info[4]

                        # Not = Not Run
                        if status not in ['Passed', 'Failed', 'Timeout', 'Not', 'Exception', 'Skipped']:
                            raise Exception("Unknow test case status")

                        # Get the available information
                        current_test = info[0]  # test case name
                        status = 0 if status == 'Passed' else 1
                        duration = float(info[-2])
                        total_duration += duration

                        # minutes * 60 + sec
                        if info[-1] != 'sec':
                            raise Exception("Unknow test case duration")

                        tests.append([current_test, status, duration])

                # If I started the line which contains the tests information
                if 'Test project' in line:
                    valid_info = True

        if total_duration == 0.0:
            tests = []

        return tests

    def run(self):
        os.chdir(self.log_dir)

        df = pd.read_csv(glob.glob("repo-data-jobs-gitlab-ci.csv")[0], sep=";")

        df_tests = pd.DataFrame(
            columns=['job_id', 'sha', 'pipeline_id', 'last_run', 'test_name', 'verdict', 'duration'])

        i = 1
        for file in glob.glob("*.log"):
            # Identifying the file
            pipeline_id, sha, job_id = file.replace('.log', '').split("_")
            pipeline_id = int(pipeline_id)
            job_id = int(job_id)

            # Get information about the job
            info = df[(df.job_id == job_id) & (df.commit_id == sha)
                      & (df.pipeline_id == pipeline_id)].iloc[0]

            try:
                tests = self.get_tests(file)
            except Exception as e:
                raise Exception(f"Error in Pipeline: {pipeline_id}, SHA: {sha}, Job: {job_id}. {str(e)}. \n\nMetainformation:\n {info}")
                

            if len(tests) > 0:
                # Collect the tests for a log
                df_tests_temp = pd.DataFrame(
                    tests, columns=['test_name', 'verdict', 'duration'])

                df_tests_temp['job_id'] = job_id
                df_tests_temp['sha'] = sha
                df_tests_temp['pipeline_id'] = pipeline_id
                df_tests_temp['last_run'] = info['job_started_at']

                df_tests_temp = df_tests_temp[
                    ['job_id', 'sha', 'pipeline_id', 'last_run', 'test_name', 'verdict', 'duration']]

                # Merge information
                df_tests = df_tests.append(df_tests_temp)

            i += 1

        # Save the results
        df_tests.to_csv('data-filtering.csv', sep=';', index=False)

        print(f"\n\n{i} logs analyzed")

    def split_data_by_job_name(self):
        os.chdir(self.log_dir)

        df = pd.read_csv(glob.glob("repo-data-jobs-gitlab-ci.csv")[0], sep=";")
        job_names = df['job_name'].unique()

        df_tests = pd.read_csv(glob.glob('data-filtering.csv')[0], sep=';')

        print('Total of jobs', len(job_names))
        for job_name in job_names:
            print(job_name)
