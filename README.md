[<img align="right" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/pradolima)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


# GitLabCI-Torrent tool <img width="40" src="https://emojis.slackmojis.com/emojis/images/1605479284/10796/among_us_party.gif?1605479284" alt="Among us Party" />


### An easy way to mining the GitLab CI job logs seeking test results <img width="40" src="https://emojis.slackmojis.com/emojis/images/1563480763/5999/meow_party.gif?1563480763" alt="Meow Party" />

![](https://img.shields.io/badge/python-3.6+-blue.svg)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3988266.svg)](https://doi.org/10.5281/zenodo.3988266)

This tool contains methods to download, analyze, and extract data from job logs hosted at GitLab CI. They are:

1. **Harvester** which downloads the logs (```harvester_main.py```)
2. **Analyzer** to extract relevant information from logs (```analyzer_main.py```)
3. **Data Extraction** (```data_extraction_main.py```) to split the data by variants (Read our article to know about [Highly Configuration Systems](https://doi.org/10.1145/3382025.3414967))
4. **Project Status** (```project_status_main.py```) to observe relevant information about the system and its variants, such as the period (variant exist/logs extracted), the number of builds, the number of faults (and build that fails), the number of tests (variation), the mean test duration, and the interval between commits.

# :pencil: Citation 

If this tool contributes to a project which leads to a scientific publication, I would appreciate a citation.

```
@InProceedings{PradoLima_Learning2020,
  author    = {Prado Lima, Jackson A. and Mendon\c{c}a, Willian D. F. and Vergilio, Silvia R. and Assun\c{c}\~{a}o, Wesley K. G.},
  title     = {{Learning-Based Prioritization of Test Cases in Continuous Integration of Highly-Configurable Software}},
  booktitle = {Proceedings of the 24th ACM Conference on Systems and Software Product Line: Volume A - Volume A},
  series    = {SPLC'20}
  year      = {2020},
  isbn      = {9781450375696},
  doi       = {10.1145/3382025.3414967},
  articleno = {31},
  numpages  = {11},
  location  = {Montreal, Quebec, Canada},
  publisher = {Association for Computing Machinery},
}
```

# :red_circle: Installing required dependencies

The following command allows to install the required dependencies:

```
 $ pip install -r requirements.txt
 ```

# :heavy_exclamation_mark: Allowing the tool to connect witgh GitLab CI

1. Create a personal Access Token (see [Personal Token Acess](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) guide) for the GitLab instance desired, for example, https://gitlab.com or https://gitlab.dune-project.org/. This token needs privileges to read the repository and gather the logs.
2. Complete the **configuration.properties** file with your GitLab Access Token

#  Using the tool <img width="40" src="https://emojis.slackmojis.com/emojis/images/1609352144/11926/dianajoa.gif?1609352144" alt="Dianajoa" />

## 📌 Downloading the job logs (*Harvester*)

To download the logs from a project, do:

```
python harvester_main.py -p ProjectID -k ConfigKey
```

**where:** 
- `-p` or `--project_id` for *Repository ID* (or Project ID). Follow [this answer](https://stackoverflow.com/a/53126068) to find the ID.
- `-k` or `--configkey` is the Configuration Key saved in **configuration.properties** (default **GitLab**)

The another parameters available are:
- The user can pass a directory where the logs will be saved using `-d` or `--save_dir` (default **logs**).
- The user can define a threshold for the mining using the parameter `-t` or `--threshold`. This parameter is a date threshold in format YYYY/MM/DD, otherwise it will return all logs.

## 📌 Running the data extraction process (*Analyzer*)

To extract the features for one project, do:

```
python analyzer_main.py -d PathToLogs
```

**where:** 
- `-d` or `--logs_dir` is the directory with the logs.

## 📌 Splitting by Variants (*Data Extraction*)

To split the test results by variant, do:

```
python data_extraction_main.py -d PathToLogs -p ProjectName
```

**where:** 
- `-d` or `--logs_dir` is the directory with the logs.
- `-p` or `--project_name` the project name. Here, some projects have similar name for repository and (gitlab) user. In this way, you can decide the right name.


## 📌 Observing the project (*Project Status*)

To observe the project status for one project, do:

```
python project_status_main.py -d PathToLogs -p ProjectName
```

**where:** 
- `-d` or `--logs_dir` is the directory with the logs.
- `-p` or `--project_name` the project name. Here, some projects have similar name for repository and (gitlab) user. In this way, you can decide the right name.

# Contributors

- 👨‍💻 Jackson Antonio do Prado Lima <a href="mailto:jacksonpradolima@gmail.com">:e-mail:</a>
- 👨‍💻 Willian Douglas Ferrari Mendonça <a href="mailto:williandouglasferrari@gmail.com">:e-mail:</a>

<a href="https://github.com/jacksonpradolima/gitlabci-torrent/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=jacksonpradolima/gitlabci-torrent" />
</a>