import argparse
from datetime import date

from gitlabci_torrent.harvester import Haverster

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Harvester - Download the Logs')
    ap.add_argument('-p', '--project_id', type=int,
                    required=True, help="Repository ID")

    ap.add_argument('-k', '--configkey', type=str, default="GitLab",
                    help="Configuration Key")

    # The user can pass a directory where the logs will be saved
    ap.add_argument(
        '-d', '--save_dir', help='Directory to save the logs', default='logs')

    ap.add_argument(
        '-t', '--threshold',
        help='Date Threshold in format YYYY/MM/DD, otherwise it will be used the most recent date (now)',
        default=None)

    args = ap.parse_args()

    h = Haverster(args.configkey, args.project_id,
                  args.save_dir, args.threshold)

    print("Collecting the jobs")
    h.analise_project()
    print(f'{len(h.get_jobs())} found.')

    print("Downloading the jobs")
    h.download_logs()

    print("The harvester process ended!")
