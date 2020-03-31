import pandas as pd
import numpy as np
import os


class ProjectStatus(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.project = project_dir.split(os.sep)[-1]

    def update_project(self, project_dir):
        self.project_dir = project_dir
        self.project = project_dir.split(os.sep)[-1]

    def get_summary(self):
        summary_cols = ["Name", "Period", "Builds", "Faults",
                        "Faulty builds", "Tests", "Test suite size",
                        "Duration", "Interval"]

        summary = pd.DataFrame(columns=summary_cols)

        df = pd.read_csv(f'{self.project_dir}{os.sep}data-filtering.csv', sep=';', thousands=',')

        df['last_run'] = pd.to_datetime(df['last_run'])

        # Sort by commits arrival and start
        df = df.sort_values(by=['last_run'])

        # Convert to minutes only valid build duration
        duration = [x / 60 for x in df.duration.tolist()]

        dates = pd.to_datetime(df['last_run'].unique())

        # Difference between commits arrival - Convert to minutes to improve the view
        diff_date = [(dates[i] - dates[i + 1]).seconds /
                     60 for i in range(len(dates) - 1)]

        total_builds = df.job_id.nunique()

        # Buld Period
        mindate = df['last_run'].min().strftime("%Y/%m/%d")
        maxdate = df['last_run'].max().strftime("%Y/%m/%d")

        builds = df['job_id'].max()

        faults = df.query('verdict > 0').groupby(['job_id'], as_index=False).agg({'verdict': np.sum})

        # Number of builds in which at least one test failed
        faulty_builds = faults['verdict'].count() if len(faults) > 0 else 0

        # Total of faults
        total_faults = faults['verdict'].sum() if len(faults) > 0 else 0

        # number of unique tests identified from build logs
        test_max = df['test_name'].nunique()

        tests = df.groupby(['job_id'], as_index=False).agg({'test_name': 'count'})

        # range of tests executed during builds
        test_suite_min = tests['test_name'].min()
        test_suite_max = tests['test_name'].max()

        row = [self.project.split("@")[-1], mindate + "-" + maxdate, total_builds, total_faults, faulty_builds,
               test_max, str(test_suite_min) + "-" + str(test_suite_max),
               f"{round(np.mean(duration), 4)} ({round(np.std(duration), 3)})" if len(duration) > 0 else "-",
               f"{round(np.mean(diff_date), 4)} ({round(np.std(diff_date), 3)})" if len(diff_date) > 0 else "-"]

        summary = summary.append(pd.DataFrame(
            [row], columns=summary_cols), ignore_index=True)

        return summary
