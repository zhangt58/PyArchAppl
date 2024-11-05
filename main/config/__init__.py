import configparser
from pathlib import Path
from typing import Union

_cwdir = Path(__file__).parent


def read_config(config_file: Union[Path, None] = None) -> dict:
    """ Read the configuration file as a dictionary.

    Parameters
    ----------
    config_file : Path or None
        The file path to the configuration file, if not set, use the default
        one distributed with the package.

    Returns
    -------
    r : dict
        A dictionary of the configurations.
    """
    if config_file is None:
        config_file = _cwdir.joinpath("default.ini")
    config = configparser.ConfigParser()
    _config_pth = config.read(config_file.expanduser())
    # utilized server config
    server_key = config['main']['use']
    if server_key not in config:
        raise RuntimeError(f"'{server_key}' section not found in {config_file}")
    server_config = dict(config[server_key])
    if 'url' not in server_config:
        raise RuntimeError(f"'url' not found in '{server_key}' section")
    all_config = {
        'server': server_config,
        'path': _config_pth[0]
    }
    # commands default options
    if 'pyarchappl-get' in config:
        get_config = dict(config['pyarchappl-get'])
        if 'use_json' in get_config:
            get_config['use_json'] = config['pyarchappl-get'].getboolean('use_json')
        all_config['pyarchappl-get'] = get_config

    return all_config


def get_config_path() -> Path:
    """ Return the configuration file path, searching priority:

    1. ~/.pyarchappl/config.ini
    2. /etc/pyarchappl/config.ini
    3. <package-dir>/config/default.ini

    Returns
    -------
    pth : Path
        The path of the configuration file.
    """
    if Path("~/.pyarchappl/config.ini").expanduser().is_file():
        return Path("~/.pyarchappl/config.ini").expanduser()
    elif Path("/etc/pyarchappl/config.ini").is_file():
        return Path("/etc/pyarchappl/config.ini")
    else:
        return _cwdir.joinpath("default.ini")


config_path: Path = get_config_path()
SITE_CONFIG: dict = read_config(config_path)
SITE_SERVER_CONFIG: dict = SITE_CONFIG['server']
if 'admin_port' in SITE_SERVER_CONFIG:
    SITE_ADMIN_URL = f"{SITE_SERVER_CONFIG['url']}:{SITE_SERVER_CONFIG['admin_port']}"
else:
    SITE_ADMIN_URL = f"{SITE_SERVER_CONFIG['url']}"
if 'data_port' in SITE_SERVER_CONFIG:
    SITE_DATA_URL = f"{SITE_SERVER_CONFIG['url']}:{SITE_SERVER_CONFIG['data_port']}"
else:
    SITE_DATA_URL = f"{SITE_SERVER_CONFIG['url']}"

