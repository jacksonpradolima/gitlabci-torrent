import pandas as pd
import numpy as np
import os


class ProjectStatus(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir

    def generate_summary(self):
        summary_cols = ["Period", "Builds", "Faults", "Faulty builds", "Tests", "Test suite size"]
        summary = pd.DataFrame(columns=summary_cols)

        df = pd.read_csv(f'{self.project_dir}{os.sep}data-filtering.csv', sep=';', thousands=',')

        df.last_run = pd.to_datetime(df.last_run)

        # Sort by commits arrival and start
        df = df.sort_values(by=['last_run'])

        total_builds = df.job_id.nunique()

        # Buld Period
        mindate = df['last_run'].min().strftime("%Y/%m/%d")
        maxdate = df['last_run'].max().strftime("%Y/%m/%d")

        builds = df['job_id'].max()

        faults = df.query('verdict > 0').groupby(
            ['job_id'], as_index=False).agg({'verdict': np.sum})['verdict']

        # Number of builds in which at least one test failed
        faulty_builds = faults.count()

        # Total of faults
        total_faults = faults.sum()

        # number of unique tests identified from build logs
        test_max = df['test_name'].nunique()

        tests = df.groupby(['job_id'], as_index=False).agg({'test_name': 'count'})

        # range of tests executed during builds
        test_suite_min = tests['test_name'].min()
        test_suite_max = tests['test_name'].max()

        row = [mindate + "-" + maxdate, total_builds, total_faults, faulty_builds,
               test_max, str(test_suite_min) + "-" + str(test_suite_max)]

        summary = summary.append(pd.DataFrame(
            [row], columns=summary_cols), ignore_index=True)

        print("\n")
        print(summary.head())
