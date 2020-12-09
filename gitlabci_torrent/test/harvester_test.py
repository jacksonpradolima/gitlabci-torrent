import unittest

from gitlabci_torrent.harvester import Haverster


class RunningHarvester(unittest.TestCase):
    def test_harvester(self):
        h = Haverster(6055600, 'logs', '2019/01/04')

        # h.analise_project()

        self.assertTrue('libssh' == h.get_user() and 'libssh-mirror' == h.get_project_name())


if __name__ == '__main__':
    unittest.main()
