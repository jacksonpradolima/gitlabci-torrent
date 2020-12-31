import csv
import os
from pathlib import Path

import pandas as pd
from alive_progress import alive_bar


class DataExtraction(object):
    def __init__(self, log_dir, project_name):
        self.log_dir = log_dir
        self.project_name = project_name
        self.df_main = None
        self.df_parsed = None

    def get_data(self, force=False):
        if self.df_main is None or force:
            df_repo = pd.read_csv(f'{self.log_dir}{os.sep}repo-data-jobs-gitlab-ci.csv', sep=';')
            df_min = pd.read_csv(f'{self.log_dir}{os.sep}data-filtering.csv', sep=';')

            # Merge with GitLab CI Information
            self.df_main = pd.merge(df_min, df_repo, on=['job_id', 'job_id'], how='left')

        return self.df_main

    def filter_data(self, df):
        # Get only valid data
        return df.query("job_status == 'failed' or job_status == 'success'")

    def get_data_parsed(self, force=False):
        if self.df_parsed is None or force:
            self.df_parsed = self.filter_data(self.get_data())

            # Select the columns
            self.df_parsed = self.df_parsed[['job_id', 'job_name', 'sha', 'pipeline_id_y',
                                             'last_run', 'test_name', 'verdict', 'duration']]

            # Workaround to avoid problems with date (when we get the CI Cycle number)
            self.df_parsed.last_run = pd.to_datetime(self.df_parsed.last_run)
            self.df_parsed.last_run = self.df_parsed['last_run'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f'))
            self.df_parsed.last_run = pd.to_datetime(self.df_parsed.last_run)
            self.df_parsed.sort_values(by=['last_run'], inplace=True)

            self.df_parsed = self.df_parsed.reset_index(drop=True)

            # Convert the test case names and commit's sha to a ID
            self.df_parsed['test_name'] = pd.factorize(self.df_parsed['test_name'])[0] + 1
            self.df_parsed['sha'] = pd.factorize(self.df_parsed['sha'])[0] + 1

        return self.df_parsed

    def feature_engineering(self, df):
        # df.loc[:, 'BuildId'] = df['sha']

        tc_fieldnames = ['Id', 'Name', 'BuildId', 'Duration',
                         'CalcPrio', 'LastRun', 'Verdict', 'Cycle', 'LastResults']
        tcdf = pd.DataFrame(columns=tc_fieldnames)

        # Id | Unique numeric identifier of the test execution
        tcdf['Id'] = df.index + 1
        # Name | Unique numeric identifier of the test case
        tcdf['Name'] = df['test_name']
        # BuildId | Value uniquely identifying the build.
        # tcdf['Sha'] = df['sha']  # Preserving "original" sha factorized
        tcdf['BuildId'] = pd.factorize(df['sha'])[0] + 1  # Generate new factorization
        # Duration | Approximated runtime of the test case
        tcdf['Duration'] = df['duration']
        # CalcPrio | Priority of the test case, calculated by the prioritization algorithm(output column, initially 0)
        tcdf['CalcPrio'] = 0
        # LastRun | Previous last execution of the test case as date - time - string(Format: `YYYY - MM - DD HH: ii`)
        tcdf['LastRun'] = df['last_run']
        # Verdict | Test verdict of this test execution(Failed: 1, Passed: 0)
        tcdf['Verdict'] = df['verdict']

        # Cycle | The number of the CI cycle this test execution belongs to
        tcdf['monthdayhour'] = tcdf['LastRun'].apply(lambda x: (x.month, x.day, x.hour))
        tcdf['Cycle'] = pd.factorize(tcdf.monthdayhour)[0] + 1
        del tcdf['monthdayhour']

        return tcdf

    def get_variants(self):
        df = self.get_data_parsed()
        
        jobs = [i.translate({ord(c): "_" for c in "!#$%^&*()[]{};:,.<>?|`~=+"}) for i in df["job_name"].unique().tolist()] 
        return jobs

    def extract_total_set(self):
        """
        We can have variants to be tested in each commit, in this case, producing many jobs
        We want a unique test case set used across the variants.
        For this, we select that ones failed max in any job of my commit (sha)
        Extract the following columns that have the largest value in case of duplicate
        :return:
        """
        # Save the unique test case set as total
        path = f"{self.log_dir}{os.sep}{self.project_name}@total"
        path = path.translate({ord(c): "_" for c in "!#$%^&*()[]{};:,.<>?|`~=+"})
        Path(path).mkdir(parents=True, exist_ok=True)

        with alive_bar(5, title="Extracting Total Set") as bar:
            bar.text('Reading Data')
            bar()
            df = self.get_data_parsed()

            bar.text('Parsing Data')
            bar()
            df2 = self.feature_engineering(df.copy())

            df2['Variant'] = df['job_name']
            df2.to_csv(f'{path}{os.sep}data-variants.csv', sep=';', na_rep='[]',
                       header=True, index=False,
                       quoting=csv.QUOTE_NONE)

            bar.text('Data Variants file saved')
            bar()
            df_total = df.groupby(['sha', 'pipeline_id_y', 'test_name'], as_index=False).max()
            df_total = df_total.reset_index(drop=True)
            df_total.to_csv(f"{path}{os.sep}data-filtering.csv", sep=';', na_rep='[]',
                            header=True, index=False,
                            quoting=csv.QUOTE_NONE)
            bar.text('Data Filtering file saved')
            bar()
            
            df_total = self.feature_engineering(df_total)
            df_total.to_csv(f'{path}{os.sep}features-engineered.csv', sep=';', na_rep='[]',
                            header=True, index=False,
                            quoting=csv.QUOTE_NONE)

            bar.text('Features Engineering file saved')
            bar()

    def extract_by_variant(self):
        print("Reading data")
        df = self.get_data_parsed()
        variants = self.get_variants()
        print("Ok, parsing variants...")

        df2 = df.copy()
        df2['job_name'] = df2['job_name'].apply(lambda x: x.translate({ord(c): "_" for c in "!#$%^&*()[]{};:,.<>?|`~=+"}))
        
        with alive_bar(len(variants), title="Extracting By Variant") as bar:
            for variant_name in variants:
                path = f"{self.log_dir}{os.sep}{self.project_name}@{variant_name.replace('/', '-')}"                
                Path(path).mkdir(parents=True, exist_ok=True)

                df_temp = df2[df2.job_name == variant_name]
                df_temp = df_temp.reset_index(drop=True)
                df_temp.to_csv(f"{path}{os.sep}data-filtering.csv", sep=';', na_rep='[]',
                               header=True, index=False,
                               quoting=csv.QUOTE_NONE)

                tcdf = self.feature_engineering(df_temp)
                tcdf.to_csv(f"{path}{os.sep}features-engineered.csv", sep=';', na_rep='[]',
                            header=True, index=False,
                            quoting=csv.QUOTE_NONE)

                bar()

        print("Variants parsed")
