import os
import unittest

from gitlabci_torrent.project_status import ProjectStatus


class RunningAnalyzer(unittest.TestCase):

    def test_harvester_split(self):
        a = ProjectStatus(f'logs{os.sep}libssh@libssh-mirror')

        a.generate_summary()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
