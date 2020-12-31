import argparse

from gitlabci_torrent.data_extraction import DataExtraction

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Data Extraction - Splitting by Variants')

    ap.add_argument('-d', '--log_dir',
                    help='Directory with the logs. For instance: logs/core@dune-common', default='logs')

    ap.add_argument('-p', '--project_name',
                    help='Project Name', required=True)

    args = ap.parse_args()

    a = DataExtraction(args.log_dir, args.project_name)
    a.extract_total_set()
    a.extract_by_variant()

    print("The data extraction process ended!")
