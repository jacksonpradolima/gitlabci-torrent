import os
import unittest

from gitlabci_torrent.analyzer import Analyzer


class RunningAnalyzer(unittest.TestCase):
    @unittest.skip
    def test_harvester(self):
        a = Analyzer(f'logs{os.sep}libssh@libssh-mirror')

        a.run()

        self.assertTrue(True)

    def test_harvester_split(self):
        a = Analyzer(f'logs{os.sep}libssh@libssh-mirror')

        a.split_data_by_job_name()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
