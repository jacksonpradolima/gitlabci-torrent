import os
import unittest

from gitlabci_torrent.data_extraction import DataExtraction


class RunningDataExtraction(unittest.TestCase):
    def setUp(self):
        self.data_extraction = DataExtraction(f'logs{os.sep}core@dune-common', 'dune')

    def test_extract_total_set(self):
        self.data_extraction.extract_total_set()
        self.assertTrue(True)

    def test_extract_by_variant(self):
        self.data_extraction.extract_by_variant()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
