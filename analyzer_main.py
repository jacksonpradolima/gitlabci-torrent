import argparse

from gitlabci_torrent.analyzer import Analyzer

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Analyzer - Mining the Logs')

    ap.add_argument('-d', '--save_dir',
                    help='Directory with the logs. For instance: logs/core@dune-common', default='logs')

    args = ap.parse_args()

    a = Analyzer(args.save_dir)
    a.run()

    print("The analyzer process ended!")
