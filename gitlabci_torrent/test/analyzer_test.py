import os
import unittest

from gitlabci_torrent.analyzer import Analyzer


class RunningAnalyzer(unittest.TestCase):

    def test_harvester(self):
        a = Analyzer(f'logs{os.sep}core@dune-common')

        a.run()

        self.assertTrue(True)

    @unittest.skip
    def test_harvester_split(self):
        a = Analyzer(f'logs{os.sep}core@dune-common')

        a.split_data_by_job_name()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
