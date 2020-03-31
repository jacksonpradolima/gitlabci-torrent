import os
import unittest

from gitlabci_torrent.data_extraction import DataExtraction


class RunningDataExtraction(unittest.TestCase):
    def test_extract_total_set(self):
        a = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')

        a.extract_total_set()

        self.assertTrue(True)

    def test_extract_by_variant(self):
        a = DataExtraction(f'logs{os.sep}libssh@libssh-mirror')

        a.extract_by_variant()

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()