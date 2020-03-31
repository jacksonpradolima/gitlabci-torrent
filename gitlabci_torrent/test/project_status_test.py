import os
import unittest
import pandas as pd
from tabulate import tabulate

from gitlabci_torrent.project_status import ProjectStatus
from gitlabci_torrent.data_extraction import DataExtraction


class RunningAnalyzer(unittest.TestCase):

    def test_main_system(self):
        a = ProjectStatus(f'logs{os.sep}libssh@libssh-mirror')

        print(a.get_summary().head())

        self.assertTrue(True)

    def test_total_set(self):
        print("\nInformation about total set", end="")

        a = ProjectStatus(f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@total')

        print(a.get_summary().head())

        self.assertTrue(True)

    def test_variants(self):
        de = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')
        variants = de.get_variants()

        summary_cols = ["Name", "Period", "Builds", "Faults",
                        "Faulty builds", "Tests", "Test suite size"]

        df = pd.DataFrame(columns=summary_cols)

        a = ProjectStatus(f'')

        for variant in variants:
            variant = variant.replace('/', '-')
            a.update_project(f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@{variant}')
            df = df.append(a.get_summary())

        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

        self.assertTrue(True)

    def test_both(self):
        print("\n")
        de = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')
        variants = sorted(de.get_variants())

        summary_cols = ["Name", "Period", "Builds", "Faults",
                        "Faulty builds", "Tests", "Test suite size",
                        "Duration", "Interval"]

        df = pd.DataFrame(columns=summary_cols)

        a = ProjectStatus(f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@total')

        df = df.append(a.get_summary())

        for variant in variants:
            variant = variant.replace('/', '-')
            a.update_project(f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@{variant}')
            df = df.append(a.get_summary())

        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
        print(df.to_latex(index=False))

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
