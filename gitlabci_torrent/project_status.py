import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable

# set ggplot style
plt.style.use('ggplot')
sns.set_style("whitegrid")

mpl.rcParams.update({'font.size': 24})



class ProjectStatus(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.project = project_dir.split(os.sep)[-1]

    def update_project(self, project_dir):
        self.project_dir = project_dir
        self.project = project_dir.split(os.sep)[-1]

    def get_summary(self):
        summary_cols = ["Name", "Period", "Builds", "Faults", "Tests",
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

        total_builds = df.sha.nunique()

        # Buld Period
        mindate = df['last_run'].min().strftime("%Y/%m/%d")
        maxdate = df['last_run'].max().strftime("%Y/%m/%d")

        builds = df['sha'].max()

        faults = df.query('verdict > 0').groupby(['sha'], as_index=False).agg({'verdict': np.sum})

        # Number of builds in which at least one test failed
        faulty_builds = faults['verdict'].count() if len(faults) > 0 else 0

        # Total of faults
        total_faults = faults['verdict'].sum() if len(faults) > 0 else 0

        # number of unique tests identified from build logs
        test_max = df['test_name'].nunique()

        tests = df.groupby(['sha'], as_index=False).agg({'test_name': 'count'})

        # range of tests executed during builds
        test_suite_min = tests['test_name'].min()
        test_suite_max = tests['test_name'].max()

        row = [self.project.split("@")[-1], mindate + "-" + maxdate, total_builds,
               f"{total_faults} ({faulty_builds})",
               f"{test_max} ({test_suite_min} - {test_suite_max})",
               f"{round(np.mean(duration), 4)} ({round(np.std(duration), 3)})" if len(duration) > 0 else "-",
               f"{round(np.mean(diff_date), 4)} ({round(np.std(diff_date), 3)})" if len(diff_date) > 0 else "-"]

        summary = summary.append(pd.DataFrame(
            [row], columns=summary_cols), ignore_index=True)

        return summary

    def visualize_dataset_heatmap(self, fig, ax, attribute="Verdict"):
        df = pd.read_csv(f'{self.project_dir}{os.sep}features-engineered.csv', sep=';', thousands=',')

        bid = df.BuildId.values
        nerr = df[attribute].values.astype(np.int)
        name = df.Name.values

        # The Test Case ID showed in the plot are not the real Test Case Name
        # Here a new id is created
        # Note that there is no warranty of the order of Test Case Number. Also,
        # the names not necessarily are numbers
        tc2idx = {}
        for n in name:
            if not n in tc2idx:
                tc2idx[n] = len(tc2idx)
        total_use_cases = len(tc2idx)

        # Not executed tests are noted as -1 value
        data = np.zeros((len(set(bid)), total_use_cases)) - 1
        for i, b in enumerate(bid):
            n = tc2idx[name[i]]
            e = nerr[i]
            data[b - 1, n] = e

        data = data.astype(np.int)

        set_errors = sorted(list(np.unique(data[data >= 0])))
        ticks_names = ['Not exist in T'] + ["{}".format(x)
                                            for x in set_errors]

        # Ignore the "gaps" in gradient
        # Map the original heatmapvalues to a discrete domain
        set_ticks = sorted(list(np.unique(data)))

        offset = len(set_errors) / 3

        data_copy = data.copy()
        for t in set_ticks:
            updt_val = set_ticks.index(t)
            if t < 0:
                updt_val += offset * t
            if t > 0:
                updt_val += offset

            data_copy[data == t] = updt_val

        data = data_copy
        ticks_values = sorted(list(np.unique(data)))

        ##########
        # Figure #
        ##########
        divider = make_axes_locatable(ax)
        cbar_ax = divider.append_axes('right', size='5%', pad=0.05)

        img = ax.imshow(data.T, cmap="binary", interpolation=None)

        clb = fig.colorbar(img, cax=cbar_ax)
        max_ticks = 13  # Limit number of ticks in colorbar
        idx_to_show = [0]  # Show for sure the two firts ticks

        idx_to_show += list(np.arange(1, len(ticks_values),
                                      int(len(ticks_values) / min(len(ticks_values),
                                                                  max_ticks))))
        clb.set_ticks(np.array(ticks_values)[idx_to_show])
        clb.set_ticklabels(np.array(ticks_names)[idx_to_show])

        clb.outline.set_edgecolor('black')
        clb.outline.set_linewidth(1)

        ax.set_xlabel("CI Cycle")
        ax.set_ylabel("Test Case Id")
        ax.set_aspect("auto")

        ax.invert_yaxis()
        ax.grid(b=None)
        cbar_ax.grid(b=None)
        ax.locator_params(axis='y', nbins=5)
        ax.locator_params(axis='x', nbins=5)

    def visualize_dataset_info(self, ax, attribute='Verdict'):
        df = pd.read_csv(f'{self.project_dir}{os.sep}features-engineered.csv', sep=';', thousands=',')
        df_group = df.groupby(['BuildId'], as_index=False).agg({attribute: np.sum, 'Duration': np.mean})

        ax.set_xlabel('CI Cycle')
        ax.set_ylabel('Number of Failures')
        df_group[[attribute]].plot(ax=ax)
        plt.legend([f"Total Failures: {int(df_group[attribute].sum())}"],
                   loc='center left',
                   bbox_to_anchor=(0.655, -0.10))
        plt.tight_layout()

    def visualize_testcase_volatility(self, ax):
        df = pd.read_csv(f'{self.project_dir}{os.sep}features-engineered.csv', sep=';', thousands=',')
        df_group = df.groupby(['BuildId'], as_index=False).agg({'Name': 'count'})

        ax.set_xlabel('CI Cycle')
        ax.set_ylabel('Number of Test Cases')
        df_group[["Name"]].plot(ax=ax)
        ax.legend().set_visible(False)
        plt.tight_layout()
