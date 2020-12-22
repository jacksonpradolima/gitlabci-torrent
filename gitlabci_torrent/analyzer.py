import glob
import os

import pandas as pd
from alive_progress import alive_bar


class Analyzer(object):

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.project = log_dir.split(os.sep)[-1]

        # Not = Not Run
        self.tc_status = ['Passed', 'Failed', 'Timeout', 'Not', 'Exception', 'Skipped']

    def get_number_test_cases(self, path):
        line = [line for line in open(path) if 'tests failed out of' in line]

        if len(line) > 1:
            print(f"The file {path} contains multiple lines with test results.")
            return -1

        if len(line) == 0:
            # File without test results
            return 0

        return int(line[0].split('tests failed out of')[-1])

    def _get_status_from_info(self, info):
        for i in info:
            if '***' in i:
                return i.split('***')[-1]
            if i in self.tc_status:
                return i

        return ""

    def get_tests(self, path):
        # To know when I started get the tests information
        valid_info = False

        # The test cases found
        tests = []
        total_duration = 0

        num_tc = self.get_number_test_cases(path)

        unable_find = 'Unable to find required file:'
        
        if num_tc > 0:
            tc_count = 1
            # For each line in the log
            with iter(open(path, encoding="utf-8")) as ilog:
                try:
                    for line in ilog:
                        # If I am in the end of the tests
                        if valid_info and 'tests failed out of' in line:
                            valid_info = False

                        # If I am observing the lines of the tests
                        if valid_info:
                            # Ignore line with "Start NUMBER: 'test case X'"
                            if f'{tc_count}/{num_tc}' in line and 'Test' in line:
                                try:
                                    line = line.strip()

                                    tc_count += 1
                                    if unable_find in line:
                                        # Get the right part from the next line
                                        next_line = next(ilog)

                                        # 'Unable find' was put in the line wrongly
                                        if len(line.split('/')) > 2:
                                            # The line also contains some path (garbage)
                                            # We ignore the first part (f'{tc_count}/{num_tc}' )
                                            temp_line = line.split(unable_find)[0].strip()
                                            
                                            #if not temp_line.endswith('sec'):
                                            #    temp_line += ' '
                                        else:
                                            line = line.replace(unable_find, '')
                                            s_line = line.strip().split(":")

                                            # Remove the wrong part
                                            temp_line = ''.join(s_line[:-1])

                                            # Sometime the test case name is in the same line, and only the test result in the next line
                                            l = ''.join(s_line[-1])
                                            possible_tc_names = list(filter(None, l.replace('.', ' ').split(' ')))

                                            if len(possible_tc_names) > 0:
                                                pos_tc_name = list(possible_tc_names)[0]
                                                if len(pos_tc_name) > 1 and pos_tc_name not in next_line:
                                                    temp_line += ': ' + pos_tc_name

                                                for i in possible_tc_names[1:]:
                                                    if i in self.tc_status or i.replace('***','') in self.tc_status:
                                                        temp_line += ' ' + i

                                        if ":" in temp_line:
                                            temp_line += ' ' + next_line.strip()
                                        else:
                                            temp_line += ": " + next_line.strip()
                                        line = temp_line

                                    temp_line = line.strip().split(":")

                                    if len(temp_line) > 2:
                                        # For instance, when we have Exception status
                                        temp_line[1] = ' '.join(temp_line[1:])
                                        del temp_line[-1]

                                    info = [x.strip() for x in temp_line]
                                    info = info[-1].split(" ")
                                    status = self._get_status_from_info(info)

                                    #if 'Failed' in line or 'Timeout' in line or 'Not Run' in line or 'Exception' in line or 'Skipped' in line:
                                        # When the test case status is Failed or Timeout it
                                        # is in other position (1)
                                        # When the child aborted is raise, the status in position 2
                                    #    status = self._get_status_from_info(info)
                                    #else:
                                    #    if len(info) < 4:
                                    #       print(info)
                                    #   status = info[4]

                                    dur = 0
                                    tc_name = info[0]  # test case name
                                    time_magnitude = info[-1]  # duration magnitude, for instance, in sec

                                    # Not = Not Run
                                    if status not in self.tc_status:
                                        # Maybe the status is in the next two lines:
                                        for i in range(2):
                                            next_line = next(ilog)
                                            if any(tc_s in next_line for tc_s in self.tc_status):
                                                # Split the line and remove empty itens
                                                next_line = list(filter(None, next_line.strip().split(" ")))
                                                tc_name = next_line[0]  # test case name
                                                time_magnitude = next_line[-1]  # duration magnitude, for instance, in sec
                                                status = [s for s in self.tc_status if any(s in xs for xs in next_line)]

                                                status = ''.join(status)

                                                if status not in self.tc_status and i != 0:
                                                    raise Exception("Unknow test case status")
                                                else:
                                                    dur = float(next_line[-2])
                                                    break
                                            elif i != 0:
                                                raise Exception("Unknow test case status. Line: " + line)
                                    else:
                                        dur = float(info[-2])

                                    # Get the available information
                                    current_test = tc_name
                                    status = 0 if status == 'Passed' else 1
                                    duration = dur  # tc duration
                                    total_duration += duration

                                    # minutes * 60 + sec
                                    if time_magnitude != 'sec':
                                        raise Exception("Unknow test case duration")

                                    tests.append([current_test, status, duration])
                                except ValueError as e:
                                    raise Exception("Error to parse value. Line: " + line)
                                except Exception:
                                    raise

                        # If I started the line which contains the tests information
                        if 'Test project' in line:
                            valid_info = True
                except StopIteration:
                    pass
                except Exception:
                    raise

        if total_duration == 0.0:
            tests = []

        return tests

    def run(self):
        os.chdir(self.log_dir)

        df = pd.read_csv(glob.glob("repo-data-jobs-gitlab-ci.csv")[0], sep=";")

        df_tests = pd.DataFrame(
            columns=['job_id', 'sha', 'pipeline_id', 'last_run', 'test_name', 'verdict', 'duration'])

        i = 1
        total_logs = len([name for name in os.listdir('.') if os.path.isfile(name)])

        with alive_bar(total_logs) as bar:
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

                    raise Exception(f"Error in Pipeline: {pipeline_id}, SHA: {sha}, Job: {job_id}. " +
                                    f"{str(e)}. \n\nMetainformation:\n {info}")

                if len(tests) > 0:
                    # Collect the tests for a log
                    df_tests_temp = pd.DataFrame(tests, columns=['test_name', 'verdict', 'duration'])

                    df_tests_temp['job_id'] = job_id
                    df_tests_temp['sha'] = sha
                    df_tests_temp['pipeline_id'] = pipeline_id
                    df_tests_temp['last_run'] = info['job_started_at']

                    df_tests_temp = df_tests_temp[
                        ['job_id', 'sha', 'pipeline_id', 'last_run', 'test_name', 'verdict', 'duration']]

                    # Merge information
                    df_tests = df_tests.append(df_tests_temp)

                i += 1
                bar() # process each item

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
