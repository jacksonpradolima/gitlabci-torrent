import configparser
import gitlab


def auth_gl():
    '''
    A pattern to access the GitLab
    :param token:
    :return:
    '''
    config = configparser.ConfigParser()
    config.read('../../configuration.properties')

    # An easy way to change in the future the gitlab api version
    gl = gitlab.Gitlab('https://gitlab.com', private_token=config['Gitlab.com']['Token'], api_version=4)
    gl.auth()

    return gl
