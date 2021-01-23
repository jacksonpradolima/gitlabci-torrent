import unittest

from gitlabci_torrent.utils.gitlab_utils import auth_gl


class GitUtilsTestCase(unittest.TestCase):
    def test_gh_config(self):
        try:
            gl = auth_gl("GitLab")
            self.assertTrue(True)
        except:
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
