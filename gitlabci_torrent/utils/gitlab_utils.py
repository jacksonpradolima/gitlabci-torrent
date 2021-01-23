import configparser

import gitlab


def auth_gl(configkey):
    '''
    A pattern to access the GitLab
    :param token:
    :return:
    '''
    config = configparser.ConfigParser()
    config.read(f"../../configuration.properties")

    # An easy way to change in the future the gitlab api version
    gl = gitlab.Gitlab(config[configkey]['Url'],
                       private_token=config[configkey]['Token'], api_version=4)
    gl.auth()

    return gl
