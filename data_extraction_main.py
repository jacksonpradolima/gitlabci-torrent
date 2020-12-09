import argparse

from gitlabci_torrent.data_extraction import DataExtraction

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Data Extraction - Mining the Logs')

    ap.add_argument('-d', '--log_dir',
                    help='Directory with the logs. For instance: logs/core@dune-common', default='logs')

    args = ap.parse_args()

    a = DataExtraction(args.log_dir)

    print("Extrating Total Set...")
    a.extract_total_set()

    print("Extrating By Variant...")
    a.extract_by_variant()

    print("The analyzer process ended!")
