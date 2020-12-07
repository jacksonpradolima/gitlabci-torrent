import os
import unittest
import pandas as pd


import matplotlib.pyplot as plt
from tabulate import tabulate

from gitlabci_torrent.project_status import ProjectStatus
from gitlabci_torrent.data_extraction import DataExtraction


class RunningAnalyzer(unittest.TestCase):
    @unittest.skip
    def test_main_system(self):
        a = ProjectStatus(f'logs{os.sep}libssh@libssh-mirror')

        print(a.get_summary().head())

        self.assertTrue(True)

    @unittest.skip
    def test_total_set(self):
        print("\nInformation about total set", end="")

        a = ProjectStatus(f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@total')

        print(a.get_summary().head())

        self.assertTrue(True)

    #@unittest.skip
    def test_variants(self):
        de = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')
        variants = de.get_variants()

        summary_cols = ["Name", "Period", "Builds",
                        "Faults", "Tests",
                        "Duration", "Interval"]

        df = pd.DataFrame(columns=summary_cols)

        a = ProjectStatus(f'')

        for variant in variants:
            variant = variant.replace('/', '-')
            a.update_project(f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@{variant}')
            df = df.append(a.get_summary())

        print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

        self.assertTrue(True)

    @unittest.skip
    def test_both(self):
        print("\n")
        de = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')
        variants = sorted(de.get_variants())

        summary_cols = ["Name", "Period", "Builds",
                        "Faults", "Tests",
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

    @unittest.skip
    def test_plot_heatmap_total(self):
        path = f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@total'
        a = ProjectStatus(path)

        fig, ax = plt.subplots(figsize=(30, 20))
        a.visualize_dataset_heatmap(fig, ax)
        plt.savefig(os.path.join(path, "heatpmap.pdf"), bbox_inches='tight')

        fig, ax = plt.subplots(figsize=(15, 10))
        a.visualize_dataset_info(ax)
        plt.savefig(os.path.join(path, "failures_by_cycle.pdf"), bbox_inches='tight')
        plt.clf()

        fig, ax = plt.subplots(figsize=(15, 10))
        a.visualize_testcase_volatility(ax)
        plt.savefig(os.path.join(path, "testcase_volatility.pdf"), bbox_inches='tight')
        plt.clf()

        self.assertTrue(True)

    @unittest.skip
    def test_plot_heatmap_variants(self):
        de = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')
        variants = sorted(de.get_variants())

        for variant in variants:
            variant = variant.replace('/', '-')
            path = f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@{variant}'
            a = ProjectStatus(path)

            fig, ax = plt.subplots(figsize=(30, 20))
            a.visualize_dataset_heatmap(fig, ax)
            plt.savefig(os.path.join(path, "heatpmap.pdf"), bbox_inches='tight')

            fig, ax = plt.subplots(figsize=(15, 10))
            a.visualize_dataset_info(ax)
            plt.savefig(os.path.join(path, "failures_by_cycle.pdf"), bbox_inches='tight')
            plt.clf()

            fig, ax = plt.subplots(figsize=(15, 10))
            a.visualize_testcase_volatility(ax)
            plt.savefig(os.path.join(path, "testcase_volatility.pdf"), bbox_inches='tight')
            plt.clf()

        self.assertTrue(True)

    @unittest.skip
    def test_plot_variant(self):
        path = f'logs{os.sep}libssh@libssh-mirror{os.sep}libssh@visualstudio-x86'
        a = ProjectStatus(path)

        fig, ax = plt.subplots(figsize=(30, 20))
        a.visualize_dataset_heatmap(fig, ax)
        plt.savefig(os.path.join(path, "heatpmap.pdf"), bbox_inches='tight')

        fig, ax = plt.subplots(figsize=(15, 10))
        a.visualize_dataset_info(ax)
        plt.savefig(os.path.join(path, "failures_by_cycle.pdf"), bbox_inches='tight')
        plt.clf()

        fig, ax = plt.subplots(figsize=(15, 10))
        a.visualize_testcase_volatility(ax)
        plt.savefig(os.path.join(path, "testcase_volatility.pdf"), bbox_inches='tight')
        plt.clf()

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
