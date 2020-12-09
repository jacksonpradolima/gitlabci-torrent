# GitLabCI-Torrent [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/jacksonpradolima/gitlabci-torrent) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3988266.svg)](https://doi.org/10.5281/zenodo.3988266)
GitLab CI Torrent - Mining CI job logs

# Requirements

- Python >= 3.6
- Install the modules from **requirements.txt**

# How do I start?

1. Create a personal Access Token (see [Personal Token Acess](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) guide) for the GitLab instance desired, for example, https://gitlab.com or https://gitlab.dune-project.org/
1. Complete the **configuration.properties** file with your GitLab Access Token
2. Run *bin/harvester_main.py* to download the logs. The arguments available are:
    - **-p** or **--project_id** for *Repository ID* (or Project ID). Follow [this answer](https://stackoverflow.com/a/53126068) to find the ID.
    - **-k** or **--configkey** is the Configuration Key saved in **configuration.properties** (default *GitLab*)
    - The user can pass a directory where the logs will be saved using **-d** or **--save_dir** (default *logs*).
    - The user can define a threshold for the mining using the parameter **-t** or **--threshold**. This parameter is a date threshold in format YYYY/MM/DD, otherwise it will return all logs.
3. Run *analyzer_main.pyy* to extract relevant information from logs

# Contributors

- Jackson Antonio do Prado Lima (jacksonpradolima [at] gmail [dot] com)
- Willian Douglas Ferrari Mendonça


