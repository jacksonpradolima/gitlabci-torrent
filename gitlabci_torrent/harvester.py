import json
import os
from datetime import date, datetime
from pathlib import Path
import gitlab
import pandas as pd

from gitlabci_torrent.utils.gitlab_utils import auth_gl


class Haverster(object):

    def __init__(self, configkey, project_id, save_dir, threshold=None):
        self.project_id = project_id
        self.save_dir = save_dir

        self.threshold = None
        if threshold is not None:
            threshold = threshold.split("/")
            self.threshold = date(year=int(threshold[0]), month=int(threshold[1]), day=int(
                threshold[2]))

        # GitLab authentication
        self.gl = auth_gl(configkey)

        # Get the project and its jobs
        self.project = self.gl.projects.get(self.project_id)

        self.jobs = None
        self.jobs_attributes = None

    def get_save_dir(self):
        return f'{self.save_dir}{os.sep}{self.get_user()}@{self.get_project_name()}'

    def get_project(self):
        return self.project

    def get_user(self):
        return self.project.attributes['namespace']['path']

    def get_project_name(self):
        return self.project.attributes['name']

    def _to_date(self, dd):
        """
        This function converts a string with date in format YYYY-MM-ddThh:mm:ssZ to date object
        :param dd: date in str
        :return: date in date object
        """
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        return datetime.strptime(dd, date_format).date()

    def get_jobs(self):
        if self.jobs is None:
            self.jobs = self.project.jobs.list(all=True)

            if self.threshold is not None:
                self.jobs = [job for job in self.get_jobs() if self._to_date(
                    job.attributes['created_at']) >= self.threshold]
        return self.jobs

    def get_jobs_attributes(self):
        if self.jobs_attributes is None:
            self.jobs_attributes = [job.attributes for job in self.get_jobs()]
        return self.jobs_attributes

    def jobs_information_csv(self, jobs_attributes, save_dir):
        # Prepare the dataset
        df = pd.json_normalize(jobs_attributes)
        # print(df.columns)

        """
        
        df.columns = df.columns.map(lambda x: x.split(".")[-1])
        # Rename columns (multiple 'id' columns)
        df.columns = ['job_allow_failure', 'artifacts', 'artifacts_expire_at', 'author_email',
                      'author_name', 'authored_date', 'committed_date', 'committer_email',
                      'committer_name', 'commit_created_at', 'commit_id', 'commit_message', 'commit_parent_ids',
                      'commit_short_id', 'commit_title', 'commit_web_url', 'job_coverage', 'job_created_at',
                      'job_duration',
                      'job_finished_at', 'job_id', 'job_name', 'pipeline_created_at', 'pipeline_id', 'pipeline_ref',
                      'pipeline_sha', 'pipeline_status',
                      'pipeline_updated_at', 'pipeline_web_url', 'project_id', 'job_ref', 'runner', 'runner_active',
                      'runner_description', 'runner_id', 'runner_ip_address', 'runner_is_shared', 'runner_name',
                      'runner_online',
                      'runner_status', 'job_stage', 'job_started_at', 'job_status', 'job_tag', 'user_avatar_url',
                      'user_bio',
                      'user_created_at', 'user_id', 'user_job_title', 'user_linkedin', 'user_location', 'user_name',
                      'user_organization', 'user_public_email', 'user_skype', 'user_state', 'user_twitter', 'username',
                      'user_web_url', 'user_website_url', 'job_web_url']
        
        # Now we know the desired columns
        df = df[['job_id', 'job_name', 'job_status', 'job_stage', 'job_ref', 'job_tag', 'job_allow_failure',
                 'job_created_at', 'job_started_at', 'job_finished_at', 'job_coverage', 'job_duration',
                 'commit_id', 'commit_title', 'commit_message',
                 'pipeline_id', 'pipeline_status']]
        """

        df.columns = df.columns.map(lambda x: x.replace('.', '_'))
        df = df[['id', 'name', 'status', 'stage', 'ref', 'tag', 'allow_failure',
                 'created_at', 'started_at', 'finished_at', 'coverage', 'duration',
                 'commit_id', 'commit_title', 'commit_message',
                 'pipeline_id', 'pipeline_status']]

        df.columns = ['job_id', 'job_name', 'job_status', 'job_stage', 'job_ref', 'job_tag', 'job_allow_failure',
                      'job_created_at', 'job_started_at', 'job_finished_at', 'job_coverage', 'job_duration',
                      'commit_id', 'commit_title', 'commit_message',
                      'pipeline_id', 'pipeline_status']

        df['job_created_at'] = pd.to_datetime(df['job_created_at'])
        df['job_started_at'] = pd.to_datetime(df['job_started_at'])
        df['job_finished_at'] = pd.to_datetime(df['job_finished_at'])

        # save information
        df.to_csv(f'{save_dir}{os.sep}repo-data-jobs-gitlab-ci.csv', sep=";", index=False)

    def analise_project(self):
        # Prepare the folder where we gonna download them
        Path(self.get_save_dir()).mkdir(parents=True, exist_ok=True)

        # Saving the complete jobs information
        with open(f'{self.get_save_dir()}{os.sep}repo-data-jobs-gitlab-ci.json', 'w', encoding='utf-8') as f:
            json.dump(self.get_jobs_attributes(), f, indent=4)

        # Save a summary in csv
        self.jobs_information_csv(
            self.get_jobs_attributes(), self.get_save_dir())

    def download_logs(self):
        jobs_attributes = self.get_jobs_attributes()
        jobs_trace = [job.trace() for job in self.get_jobs()]

        for trace, attribute in zip(jobs_trace, jobs_attributes):
            job_id = attribute['id']
            sha = attribute['commit']['id']
            pipeline_id = attribute['pipeline']['id']

            # Save each log file in the project folder
            # The file name is to split by pipeline_commit_job
            with open(f"{self.get_save_dir()}{os.sep}{pipeline_id}_{sha}_{job_id}.log", 'w', encoding='utf-8') as f:
                f.write(trace.decode("utf-8"))
