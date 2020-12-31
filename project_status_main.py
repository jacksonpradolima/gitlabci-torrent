import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

from alive_progress import alive_bar

from gitlabci_torrent.project_status import ProjectStatus
from gitlabci_torrent.data_extraction import DataExtraction

summary_cols = ["Name", "Period", "Builds",
                "Faults", "Tests", "Duration", "Interval"]


def plot_project_status(project_stat: ProjectStatus, path):
    fig, ax = plt.subplots(figsize=(30, 20))
    project_stat.visualize_dataset_heatmap(fig, ax)
    plt.savefig(os.path.join(path, "heatpmap.pdf"), bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(15, 10))
    project_stat.visualize_dataset_info(ax)
    plt.savefig(os.path.join(path, "failures_by_cycle.pdf"),
                bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(15, 10))
    project_stat.visualize_testcase_volatility(ax)
    plt.savefig(os.path.join(path, "testcase_volatility.pdf"),
                bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Project Status - Observing the Project')

    ap.add_argument('-d', '--log_dir',
                    help='Directory with the logs. For instance: logs/core@dune-common', default='logs')

    ap.add_argument('-p', '--project_name',
                    help='Project Name', required=True)

    args = ap.parse_args()

    # Create a new dataframe to save the project status
    df = pd.DataFrame(columns=summary_cols)

    data_extr = DataExtraction(args.log_dir, args.project_name)
    variants = data_extr.get_variants()

    with alive_bar(len(variants) + 2, title="Project Status") as bar:
        # Get the general status from project
        #bar.text('Processing the general status from project...')
        #bar()
        #project_stat = ProjectStatus(args.log_dir)
        #df = df.append(project_stat.get_summary())

        # Get the project status from total set
        bar.text('Processing the project status from total set...')
        bar()
        path = f"{args.log_dir}{os.sep}{args.project_name}@total"
        project_stat = ProjectStatus(path)
        df = df.append(project_stat.get_summary())
        plot_project_status(project_stat, path)

        # Get the status for each variant from project
        bar.text('Processing the project status for each variant...')
        bar()
        for variant in variants:
            variant = variant.replace('/', '-')            
            path = f"{args.log_dir}{os.sep}{args.project_name}@{variant}"
            
            project_stat.update_project(path)
            df = df.append(project_stat.get_summary())
            plot_project_status(project_stat, path)

            bar()

    print("\n\nExporting Project Status to project_status.txt")
    with open('project_status.txt', 'w') as tf:
        tf.write(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

    print("Exporting Project Status to project_status_table.tex")
    df.to_latex('project_status_table.tex', index=False)
